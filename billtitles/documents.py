from elasticsearch_dsl import Document


# @registry.register_document
class BillBasicDocument(Document):
    """
    ### Bill basic information document
    """

    class Index:
        name = "bill-basic"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    # class Django:
    #     model = BillBasic
    #     fields = [
    #         "bill_id",
    #         "bill_type",
    #         "number",
    #         "bill_number",
    #         "congress",
    #         "introduced_at",
    #         "updated_at",
    #     ]


class BillTitlesDocument(Document):
    """
    ### Bill titles document
    """

    # bill_basic = fields.ObjectField(
    #     properties={
    #         "bill_id": fields.TextField(attr="bill_id"),
    #         "bill_type": fields.TextField(attr="bill_type"),
    #         "number": fields.IntegerField(attr="number"),
    #         "bill_number": fields.TextField(attr="bill_number"),
    #         "congress": fields.IntegerField(attr="congress"),
    #         "introduced_at": fields.DateField(attr="introduced_at"),
    #         "updated_at": fields.DateField(attr="updated_at"),
    #     }
    # )

    class Index:
        name = "bill-titles"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    # class Django:
    #     model = BillTitles
    #     fields = ["official_title", "popular_title", "short_title"]
    #     related_models = [BillBasic]
    #
    # def get_instances_from_related(self, related_instance):
    #     if isinstance(related_instance, BillBasic):
    #         return related_instance.billtitles.all()


# @registry.register_document
class BillStageTitleDocument(Document):
    """
    ### Given stage titles document of each bill
    """

    # bill_basic = fields.ObjectField(
    #     properties={
    #         "bill_id": fields.TextField(attr="bill_id"),
    #         "bill_type": fields.TextField(attr="bill_type"),
    #         "number": fields.IntegerField(attr="number"),
    #         "bill_number": fields.TextField(attr="bill_number"),
    #         "congress": fields.IntegerField(attr="congress"),
    #         "introduced_at": fields.DateField(attr="introduced_at"),
    #         "updated_at": fields.DateField(attr="updated_at"),
    #     }
    # )

    class Index:
        name = "bill-stage-title"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    # class Django:
    #     model = BillStageTitle
    #     fields = ["title", "titleNoYear", "type", "As", "is_for_portion"]
    #     related_models = [BillBasic]
    #
    # def get_instances_from_related(self, related_instance):
    #     if isinstance(related_instance, BillBasic):
    #         return related_instance.billstagetitle.all()
