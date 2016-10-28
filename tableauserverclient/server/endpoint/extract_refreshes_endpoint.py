from .endpoint import Endpoint
from .. import PaginationItem, ExtractRefreshTaskItem
import logging

logger = logging.getLogger('tableau.endpoint.tasks')

class ExtractRefreshes(Endpoint):
    def __init__(self, parent_srv):
        super(ExtractRefreshes, self).__init__()
        self.parent_srv = parent_srv

    @property
    def baseurl(self):
        return "{0}/sites/{1}".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def get_for_schedule(self, schedule_id, req_options=None):
        url = "{0}/schedules/{1}/extracts".format(self.baseurl, schedule_id)
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        tasks = ExtractRefreshTaskItem.from_response(server_response.content, schedule_id)
        return tasks, pagination_item