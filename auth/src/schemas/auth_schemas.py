from marshmallow import fields

from schemas.ma import ma


class BearerAuthSchema(ma.Schema):
    type = fields.String(required=True, example="http")
    scheme = fields.String(required=True, example="bearer")


class IsTokenCompromisedSchema(ma.Schema):
    is_compromised = fields.Boolean(required=True)
