import errno
import json
import logging
import os
import re
import sys
import traceback
from datetime import datetime

# import ciso8601
from billtitles.config import settings
from billtitles.models import BillBasic
from billtitles.models import BillStageTitle
from billtitles.models import BillTitles


def get_config():
    # read in an opt-in config file for changing directories
    # and supplying email settings
    # returns None if it's not there,
    # and this should always be handled gracefully
    path = "config.yml"
    if os.path.exists(path):
        # Don't use a cached config file, just in case,
        # and direct_yaml_load is not yet defined.
        import yaml

        config = yaml.load(open(path), Loader=yaml.BaseLoader)
    else:
        config = None

    return config


def get_data_path(*args):
    # Utility function to generate a part of the path
    # to data/{congress}/bills/{billtype}/{billtypenumber}
    # given as many path elements as are provided. args
    # is a list of zero or more of congress, billtype,
    # and billtypenumber (in order).
    args = list(args)
    if len(args) > 0:
        args.insert(1, "bills")
    if settings.DATA_DIR:
        data_dir = settings.DATA_DIR
        return os.path.join(data_dir, *args)
    else:
        logging.error(
            "Can not find data directory. "
            'You need to configure "DATA_DIR" in env file.'
        )
        sys.exit(1)


def filter_ints(seq):
    for s in seq:
        try:
            yield int(s)
        except (TypeError, ValueError):
            # Not an integer
            continue


def format_exception(exception):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))


def get_json_bills_to_process(options):
    if not options.get("congress"):
        congresses = sorted(filter_ints(os.listdir(get_data_path())))
    else:
        congresses = sorted([int(c) for c in options["congress"].split(",")])

    # walk through congress
    for congress in congresses:
        # turn this back into a string
        congress = str(congress)

        # walk through all bill types in that congress
        # (sort by bill type so that we proceed in a stable order each run)

        bill_types = [
            bill_type
            for bill_type in os.listdir(get_data_path(congress))
            if not bill_type.startswith(".")
        ]

        for bill_type in sorted(bill_types):

            # walk through each bill in that congress and bill type
            # (sort by bill number so that we proceed in a normal order)

            bills = [
                bill
                for bill in os.listdir(get_data_path(congress, bill_type))
                if not bill.startswith(".")
            ]

            for bill_type_and_number in sorted(
                bills, key=lambda x: int(x.replace(bill_type, ""))
            ):
                dp = get_data_path(
                    congress, bill_type, bill_type_and_number, "data.json"
                )

                if os.path.exists(dp):
                    # TODO: check if this bill already indexed
                    bill_id = f"{bill_type_and_number}-{congress}"
                    yield bill_id


def process_set(to_fetch, options):
    errors = []
    saved = []
    skips = []

    for id in to_fetch:
        try:
            results = process_data_json(id, options)
        except Exception as e:
            if options.get("raise", False):
                raise
            else:
                errors.append((id, e, format_exception(e)))
                continue

        if results.get("ok", False):
            if results.get("saved", False):
                saved.append(id)
                logging.info("[%s] Saved" % id)
            else:
                skips.append(id)
                logging.warn("[%s] Skipping: %s" % (id, results["reason"]))
        else:
            errors.append((id, results, None))
            logging.error("[%s] Error: %s" % (id, results["reason"]))

    if len(errors) > 0:
        message = "\nErrors for %s items:\n" % len(errors)
        for id, error, msg in errors:
            message += "\n\n"
            if isinstance(error, Exception):
                message += "[%s] Exception:\n\n" % id
                message += msg
            else:
                message += "[%s] %s" % (id, error)

        logging.info(message)

    logging.warning("\nErrors for %s." % len(errors))
    logging.warning("Skipped %s." % len(skips))
    logging.warning("Saved data for %s." % len(saved))

    return saved + skips  # all of the OK's


def split_bill_id(bill_id):
    return re.match(r"^([a-z]+)(\d+)-(\d+)$", bill_id).groups()


def get_bill_data_path(bill_id):
    bill_type, number, congress = split_bill_id(bill_id)
    return "%s/%s/bills/%s/%s%s/%s" % (
        settings.DATA_DIR,
        congress,
        bill_type,
        bill_type,
        number,
        "data.json",
    )


def read(destination):
    if os.path.exists(destination):
        with open(destination) as f:
            return f.read()


def get_titleNoYear(title):
    no_year_expr = re.compile(r" of \d{4}")
    return re.sub(no_year_expr, "", title)


def process_data_json(bill_id, options):
    # Load an existing bill status JSON file.
    print("[%s] Processing..." % bill_id)
    data_json_fn = get_bill_data_path(bill_id)
    source = read(data_json_fn)
    bill_data = json.loads(source)

    bill_type = bill_data["bill_type"]
    number = int(bill_data["number"])
    congress = int(bill_data["congress"])
    bill_number = f"{congress}{bill_type}{number}"
    bill_basic = (
        BillBasic.objects.create(
            bill_id=bill_id,
            bill_type=bill_type,
            number=number,
            bill_number=bill_number,
            congress=congress,
            introduced_at=datetime.strptime(
                bill_data["introduced_at"], "%Y-%m-%d"
            ).date(),
            updated_at=ciso8601.parse_datetime(bill_data["updated_at"]),
        )
        if not BillBasic.objects.filter(bill_id=bill_id).exists()
        else BillBasic.objects.filter(bill_id=bill_id).first()
    )
    print("[%s] Bill Basic information saved..." % bill_id)

    if not BillTitles.objects.filter(bill_basic__id=bill_basic.pk).exists():
        BillTitles.objects.create(
            bill_basic=bill_basic,
            official_title=bill_data["official_title"],
            popular_title=bill_data["popular_title"],
            short_title=bill_data["short_title"],
        )
    print("[%s] Bill Titles information saved..." % bill_id)

    for title_item in bill_data["titles"]:
        if not BillStageTitle.objects.filter(
            bill_basic__id=bill_basic.pk, title=title_item.get("title")
        ).exists():
            BillStageTitle.objects.get_or_create(
                bill_basic=bill_basic,
                title=title_item.get("title"),
                titleNoYear=get_titleNoYear(title_item.get("title")),
                type=title_item.get("type"),
                As=title_item.get("as"),
                is_for_portion=title_item.get("is_for_portion"),
            )
        print("[%s] Bill Stage titles information saved..." % bill_id)

    # Mark this bulk data file as processed by saving its processed lastmod
    # file under a new path.
    write(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        os.path.join(os.path.dirname(data_json_fn), "index.txt"),
    )
    print("[%s] Parsing/Index END." % bill_id)

    return {"ok": True, "saved": True}


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def write(content, destination):
    # save the content to disk.
    mkdir_p(os.path.dirname(destination))
    f = open(destination, "wb")
    try:
        f.write(content.encode("utf-8"))
    except (Exception,):
        f.write(content)
    f.close()
