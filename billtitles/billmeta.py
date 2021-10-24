# python3
# -*- coding: utf-8 -*-

"""
Utilities to extract metadata from bill json files.
The files are expected to be in a 'data.json' file in a path of the form:

`/congress/data/117/bills/hr/hr200/data.json`

The 'titles' key is an array of the form:
titles: [{ 
	as           str
	type         str
	title        str
	is_for_portion bool
}]
"""

from os.path import exists
import json
from typing import Tuple

def get_titles_from_bill_meta(bill_meta_path: str):
    """
    Parses the bill meta file and returns a list of titles.
    """
    with open(bill_meta_path, 'r') as f:
        bill_meta = json.load(f)
        titles = bill_meta['titles']
        return titles

def parse_billnumber(billnumber: str):
    """
    Given a bill number, returns a dict of the form:
    {congress: , billtype: , number: }
    """
    # TODO create billnumber_dict
    return billnumber_dict 


def get_billmeta_path_from_billnumber(billnumber: str) -> Tuple[str, bool]:
    """
    Given a bill number, returns the path to the bill meta file.
    """
    congress, billtype, number = parse_billnumber(billnumber)
    bill_meta_path = f'/congress/data/{congress}/bills/{billtype}/{billtype}{number}/data.json'
    file_exists = exists(bill_meta_path)
    return (bill_meta_path, file_exists)

