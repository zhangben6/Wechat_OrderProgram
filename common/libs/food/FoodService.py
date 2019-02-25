from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.models.food.Food import Food
from common.libs.Helper import getCurrentDate
from application import db,app


class FoodService():

    @staticmethod
    def setStockChangeLog(food_id=0,quantity=0,note=''):
        if food_id < 1 and quantity < 1:
            return False
        food_info = Food.query.filter_by(id=food_id).first()
        if not food_info:
            return False

        # 要关联到库存表的操作
        model_stock_change = FoodStockChangeLog()
        model_stock_change.food_id = food_id
        # 库存变更记录
        model_stock_change.unit = quantity
        # 现有库存量
        model_stock_change.total_stock = food_info.stock
        model_stock_change.note = ''
        model_stock_change.created_time = getCurrentDate()
        db.session.add(model_stock_change)
        db.session.commit()
        return True