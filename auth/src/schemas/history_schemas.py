from marshmallow import fields

from schemas.ma import ma


class QueryHistorySchema(ma.Schema):
    page = fields.Int(description="номер запрашиваемой страницы",
                       required=False,
                       example=1)
    size = fields.Int(description="количество результатов на страницу",
                       required=False,
                       example=20)


query_history_schema = QueryHistorySchema()


class ItemsHistorySchema(ma.Schema):
    items = fields.String(many=True, description="список дат авторизаций пользователя")
    prev_num = fields.Int(description="номер предыдущей страницы")
    next_num = fields.Int(description="номер следующей страницы")
    total = fields.Int(description="общее количество авторизаций")
