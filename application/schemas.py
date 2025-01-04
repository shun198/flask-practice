from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)


# https://github.com/marshmallow-code/flask-marshmallow
user_schema = UserSchema()
partial_user_schema = UserSchema(partial=True)
