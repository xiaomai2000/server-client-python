class TaskItem(object):

    def __init__(self, id, schedule_id):
        self._id = id
        self._schedule_id = schedule_id

    @property
    def id(self):
        return self._id

    @property
    def schedule_id(self):
        return self._schedule_id