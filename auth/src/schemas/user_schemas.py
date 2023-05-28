from marshmallow import fields

from schemas.ma import ma


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'full_name', 'created_at')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('user_detail', values=dict(id='<id>')),
        'collection': ma.URLFor('user_list'),
    })


user_detail_schema = UserSchema()
user_list_schema = UserSchema(many=True)


class UserWithRolesSchema(UserSchema):
    class Meta:
        fields = ('id', 'email', 'full_name', 'created_at', 'user_roles')


user_with_roles_schema = UserWithRolesSchema()


class UserSignUpSchema(ma.Schema):
    class Meta:
        fields = ('email', 'password', 'full_name')


user_sign_up_schema = UserSignUpSchema()


class UserLoginSchema(ma.Schema):
    class Meta:
        fields = ('email', 'password')


user_login_schema = UserLoginSchema()


class ChangePasswordSchema(ma.Schema):
    class Meta:
        fields = ('new_password', )


change_password_schema = ChangePasswordSchema()


class TokensSchema(ma.Schema):
    class Meta:
        fields = ('access_token', 'refresh_token')


class AccessTokenSchema(ma.Schema):
    access_token =fields.String(required=True)


access_token_schema = AccessTokenSchema()


class InputUuidSchema(ma.Schema):
    id = fields.UUID(required=True, example="xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx")


class OutputErrorSchema(ma.Schema):
    error = fields.String(required=True)


class OutputDetailSchema(ma.Schema):
    detail = fields.String(required=True)
