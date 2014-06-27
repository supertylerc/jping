import json
from jnpr.junos.factory.table import Table
from jnpr.junos.factory.view import View

class TableJSONEncoder( json.JSONEncoder ):
  def default(self, obj):
    if isinstance(obj, View):
      obj = dict(obj.items())
    elif isinstance(obj,Table):
      obj = { item.name: item for item in obj }
    else:
      obj = super(TableJSONEncoder, self).default(obj)
    return obj
