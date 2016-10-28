from .endpoint import Endpoint
from extract_refreshes_endpoint import ExtractRefreshes
import logging

logger = logging.getLogger('tableau.endpoint.tasks')

class Tasks(Endpoint):
    def __init__(self, parent_srv):
        super(Tasks, self).__init__()
        self.parent_srv = parent_srv
        self.extract_refreshes = ExtractRefreshes(parent_srv)