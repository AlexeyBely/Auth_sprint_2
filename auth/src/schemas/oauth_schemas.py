from schemas.ma import ma
from marshmallow import fields
from enum import Enum
from marshmallow_enum import EnumField


class Resources(Enum):
    yandex = 'yandex'
    vk = 'vk'

    def __str__(self) -> str:
        return str(self.value)

class ResourceSchema(ma.Schema):
    name_resource = EnumField(Resources)

resource_schema = ResourceSchema()


class ClientIdSchema(ma.Schema):
    class Meta:
        fields = ('client_id', 'url_request')


class CodeConfirmationSchema(ma.Schema):
    name_resource = EnumField(Resources)
    code = fields.String(description="код подтверждения", required=True)

code_confirmation_schema = CodeConfirmationSchema()


class ResourceOauthSchema(ma.Schema):
    class Meta:
        fields = ('name_resource', 'client_id', 'modifed_at')

resource_oauth_schema = ResourceOauthSchema()
resource_oauth_list_schema = ResourceOauthSchema(many=True)


class ResourceModifedSchema(ma.Schema):
    name_resource = fields.String(description="название ресурса", required=True)
    client_id = fields.String(description="id ресурса", required=True)
    client_secret = fields.String(description="secret ресурса", required=True)

resource_modifed_schema = ResourceModifedSchema()
