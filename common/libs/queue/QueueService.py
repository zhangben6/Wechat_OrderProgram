from application import app,db
from common.libs.Helper import getCurrentDate
from common.models.queue.QueueList import QueueList
import json


class QueueService():
    @staticmethod
    def addQueue(queue_name,data = None):
        model_queue = QueueList()
        model_queue.queue_name = queue_name
        if data:
            # 将数据转换成json格式的数据
            model_queue.data = json.dumps(data)
        model_queue.created_time = model_queue.updated_time = getCurrentDate()
        db.session.add(model_queue)
        db.session.commit()
