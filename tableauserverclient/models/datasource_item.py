import xml.etree.ElementTree as ET
from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_not_empty, property_not_nullable, property_is_boolean, property_is_set
from .tag_item import TagItem
from ..datetime_helpers import parse_datetime
import copy


class DatasourceItem(object):
    def __init__(self, project_id, name=None):
        self._certified = None
        self._certification_note = None
        self._connected_workbooks_count = None
        self._connections = None
        self._content_url = None
        self._created_at = None
        self._database_name = None
        self._datasource_type = None
        self._description = None
        self._encrypt_extracts = None
        self._favorites_total = None
        self._id = None
        self._initial_tags = set()
        self._has_alert = None
        self._has_extracts = None
        self._name = name
        self._owner_id = None
        self._owner_name = None
        self._project_name = None
        self._published = None
        self._server_name = None
        self._size = None
        self._tags = set()
        self._updated_at = None
        self._use_remote_query_agent = None
        self._webpage_url = None

        self.project_id = project_id

    @property
    def certified(self):
        return self._certified

    @certified.setter
    @property_not_nullable
    @property_is_boolean
    def certified(self, value):
        self._certified = value

    @property
    def certification_note(self):
        return self._certification_note

    @certification_note.setter
    def certification_note(self, value):
        self._certification_note = value

    @property
    def connected_workbooks_count(self):
        return self._connected_workbooks_count

    @property
    def connections(self):
        if self._connections is None:
            error = 'Datasource item must be populated with connections first.'
            raise UnpopulatedPropertyError(error)
        return self._connections()

    @property
    def content_url(self):
        return self._content_url

    @property
    def created_at(self):
        return self._created_at

    @property
    def database_name(self):
        return self._database_name

    @property
    def datasource_type(self):
        return self._datasource_type

    @property
    def description(self):
        return self._description

    @property
    def encrypt_extracts(self):
        return self._encrypt_extracts

    @property
    def favorites_total(self):
        return self._favorites_total

    @property
    def id(self):
        return self._id

    @property
    def has_alert(self):
        return self._has_alert

    @property
    def has_extracts(self):
        return self._has_extracts

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    @property_not_nullable
    def name(self, value):
        self._name = value

    @property
    def owner_id(self):
        return self._owner_id

    @owner_id.setter
    @property_not_empty
    @property_not_nullable
    def owner_id(self, value):
        self._owner_id = value

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    @property_not_empty
    @property_not_nullable
    def project_id(self, value):
        self._project_id = value

    @property
    def project_name(self):
        return self._project_name

    @property
    def published(self):
        return self._published

    @property
    def server_name(self):
        return self._server_name

    @property
    def size(self):
        return self._size

    @property
    def tags(self):
        return self._tags

    @tags.setter
    @property_is_set
    def tags(self, value):
        self._tags = value

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def use_remote_query_agent(self):
        return self._use_remote_query_agent

    @property
    def webpage_url(self):
        return self._webpage_url

    def _parse_updated_elements(self, datasource_xml, ns):
        if not isinstance(datasource_xml, ET.Element):
            datasource_xml = ET.fromstring(datasource_xml).find('.//t:datasource', namespaces=ns)
        if datasource_xml is not None:
            datasource_fields = self._parse_element(datasource_xml, ns)
            self._set_values(datasource_fields)
            if not self._certified:
                self._certification_note = None
        return self

    def _set_values(self, datasource_fields):
        if 'isCertified' in datasource_fields:
            self._certified = string_to_bool(datasource_fields['isCertified'])
        if 'certificationNote' in datasource_fields:
            self._certification_note = datasource_fields['certificationNote']
        if 'connectedWorkbooksCount' in datasource_fields:
            self._connected_workbooks_count = int(datasource_fields['connectedWorkbooksCount'])
        if 'contentUrl' in datasource_fields:
            self._content_url = datasource_fields['contentUrl']
        if 'createdAt' in datasource_fields:
            self._created_at = parse_datetime(datasource_fields['createdAt'])
        if 'databaseName' in datasource_fields:
            self._database_name = datasource_fields['databaseName']
        if 'type' in datasource_fields:
            self._datasource_type = datasource_fields['type']
        if 'description' in datasource_fields:
            self._description = datasource_fields['description']
        if 'encryptExtracts' in datasource_fields:
            self._encrypt_extracts = string_to_bool(datasource_fields['encryptExtracts'])
        if 'favoritesTotal' in datasource_fields:
            self._favorites_total = int(datasource_fields['favoritesTotal'])
        if 'id' in datasource_fields:
            self._id = datasource_fields['id']
        if 'hasAlert' in datasource_fields:
            self._has_alert = string_to_bool(datasource_fields['hasAlert'])
        if 'hasExtracts' in datasource_fields:
            self._has_extracts = string_to_bool(datasource_fields['hasExtracts'])
        if 'name' in datasource_fields:
            self._name = datasource_fields['name']
        if 'isPublished' in datasource_fields:
            self._published = string_to_bool(datasource_fields['isPublished'])
        if 'serverName' in datasource_fields:
            self._server_name = datasource_fields['serverName']
        if 'size' in datasource_fields:
            self._size = int(datasource_fields['size'])
        if 'tags' in datasource_fields:
            self._tags = datasource_fields['tags']
            self._initial_tags = copy.copy(self._tags)
        if 'updatedAt' in datasource_fields:
            self._updated_at = parse_datetime(datasource_fields['updatedAt'])
        if 'useRemoteQueryAgent' in datasource_fields:
            self._use_remote_query_agent = string_to_bool(datasource_fields['useRemoteQueryAgent'])
        if 'webpageUrl' in datasource_fields:
            self._webpage_url = datasource_fields['webpageUrl']
        if 'owner' in datasource_fields:
            owner_fields = datasource_fields['owner']
            if 'id' in owner_fields:
                self._owner_id = owner_fields['id']
            if 'name' in owner_fields:
                self._owner_name = owner_fields['name']
        if 'project' in datasource_fields:
            project_fields = datasource_fields['project']
            if 'id' in project_fields:
                self._project_id = project_fields['id']
            if 'name' in project_fields:
                self._project_name = project_fields['name']

    @classmethod
    def from_response(cls, resp, ns):
        all_datasource_items = list()
        parsed_response = ET.fromstring(resp)
        all_datasource_xml = parsed_response.findall('.//t:datasource', namespaces=ns)

        for datasource_xml in all_datasource_xml:
            datasource_fields = cls._parse_element(datasource_xml, ns)
            datasource_item = cls(datasource_fields['project']['id'])
            datasource_item._set_values(datasource_fields)
            all_datasource_items.append(datasource_item)
        return all_datasource_items

    @staticmethod
    def _parse_element(datasource_xml, ns):
        datasource_fields = datasource_xml.attrib
        owner_elem = datasource_xml.find('.//t:owner', namespaces=ns)
        project_elem = datasource_xml.find('.//t:project', namespaces=ns)
        tags_elem = datasource_xml.find('.//t:tags', namespaces=ns)

        if owner_elem is not None:
            owner_fields = owner_elem.attrib
            datasource_fields['owner'] = owner_fields

        if project_elem is not None:
            project_fields = project_elem.attrib
            datasource_fields['project'] = project_fields

        if tags_elem is not None:
            tags = TagItem.from_xml_element(tags_elem, ns)
            datasource_fields['tags'] = tags

        return datasource_fields


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == 'true'
