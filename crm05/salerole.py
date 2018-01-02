from crm05 import models


class Salerole():
    users = None
    iter_users = None
    reset_status = False
    rollback_list = []

    @classmethod
    def fetch_user(cls):
        sales = models.SaleRank.objects.all().order_by("-weigth").values('user', 'num')
        v = []
        sales = list(sales)  # [{'user': 2, 'num': 8}, {'user': 13, 'num': 2}, {'user': 1, 'num': 2}]
        while True:
            for item in sales:
                if item['num'] > 0:
                    v.append(item['user'])
                    item['num'] -= 1
                else:
                    sales.remove(item)
            if not sales:
                break
        cls.users = v

    @classmethod
    def get_sale_id(cls):
        if cls.rollback_list:
            return cls.rollback_list.pop()
        if not cls.users:
            cls.fetch_user()
        if not cls.users:
            return None
        if not cls.iter_users:
            cls.iter_users = iter(cls.users)
        try:
            user_id = next(cls.iter_users)
        except StopIteration as e:
            if cls.reset_status:
                cls.fetch_user()
                cls.reset_status = False
            cls.iter_users = iter(cls.users)
            user_id = cls.get_sale_id()
        return user_id

    @classmethod
    def reset(cls):
        cls.reset_status = True

    @classmethod
    def rollback(cls, sid):
        cls.rollback_list.insert(0, sid)
