import xml.etree.ElementTree as ET
from .. import NAMESPACE
from item_types import ItemTypes
from exceptions import ResponseBodyError
from property_decorators import property_is_int, property_is_enum

class TaskItem(object):

    class RefreshType:
        Full = "Full"
        Incremental = "Incremental"

    def __init__(self, id):
        self._id = id

    @property
    def priority(self):
        return self._priority

    @priority.setter
    @property_is_int(range=(1, 100))
    def priority(self, value):
        self._priority = value

    @property
    def task_type(self):
        return self._task_type

    @task_type.setter
    @property_is_enum(RefreshType)
    def task_type(self, value):
        self._task_type = value

    @property
    def item_type(self):
        return self._item_type

    @item_type.setter
    def item_type(self, value):
        # Check that it is Datasource or Workbook
        if not (value in [ItemTypes.Datasource, ItemTypes.Workbook]):
            error = "Invalid value: {0}. item_type must be of either ItemTypes.Datasource or ItemTypes.Workbook".format(value)
            raise ValueError(error)
        self._item_type = value

    @property
    def item_id(self):
        return self._item_id

    @item_id.setter
    def item_id(self, value):
        self._item_id = value

    def _set_values(self, priority, type, item_type, item_id):
        self.priority = priority
        self.type = type
        self.item_type = item_type
        self.item_id = item_id

    @classmethod
    def from_response(cls, resp):
        tasks_items = list()
        parsed_response = ET.fromstring(resp)
        extract_tags = parsed_response.findall('.//t:extract', namespaces=NAMESPACE)
        for extract_tag in extract_tags:
            (id, priority, type, item_type, item_id) = cls._parse_element(extract_tag)

            task = cls(id)
            task._set_values(priority, type, item_type, item_id)
            tasks_items.append(task)
        return tasks_items

    @staticmethod
    def _parse_element(extract_tag):
        id = extract_tag.get('id')
        priority = extract_tag.get('priority')
        type = extract_tag.get('type')

        datasource_tag = extract_tag.find('.//t:datasource', namespaces=NAMESPACE)
        workbook_tag = extract_tag.find('.//t:workbook', namespaces=NAMESPACE)
        if datasource_tag is not None:
            item_type = ItemTypes.Datasource
            item_id =  datasource_tag.get('id')
        elif workbook_tag is not None:
            item_type = ItemTypes.Workbook
            item_id = workbook_tag.get('id')
        else:
            error = "Missing workbook / datasource element for refresh task"
            raise ResponseBodyError(error)

        return id, priority, type, item_type, item_id