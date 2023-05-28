from schemas.ma import ma
from marshmallow import fields


class UserRoleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('user_role_detail', values=dict(id='<id>')),
        'collection': ma.URLFor('user_role_list'),
    })


role_detail_schema = UserRoleSchema()
role_list_schema = UserRoleSchema(many=True)


class UserRoleUpdateSchema(ma.Schema):
    class Meta:
        fields = ('name', )


role_update_schema = UserRoleUpdateSchema()


class UserProvideRoleSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'role_id')


user_provide_role_schema = UserProvideRoleSchema()


class QueryUserIdSchema(ma.Schema):
    user_id = fields.UUID(required=False, example="xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx")


query_user_id_schema = QueryUserIdSchema()
