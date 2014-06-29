import json
from jnpr.junos.factory.table import Table
from jnpr.junos.factory.view import View

class TableJSONEncoder(json.JSONEncoder):
    """An extension of json.JSONEncoder to convert
       jnpr.junos.factory.table.Table and
       jnpr.junos.factory.view.View objects to JSON.

    """

    def default(self, obj):
        """Convert tables and views to JSON

        """
        if isinstance(obj, View):
            obj = dict(obj.items())
        elif isinstance(obj, Table):
            obj = {item.name: item for item in obj}
        else:
            obj = super(TableJSONEncoder, self).default(obj)
        return obj
