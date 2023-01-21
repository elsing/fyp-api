from tortoise import Model
from tortoise import fields as dbfields
from tortoise.validators import RegexValidator
from marshmallow import Schema, fields
import re


class Org(Model):
    org_id = dbfields.IntField(pk=True)
    name = dbfields.CharField(max_length=50)
    contact = dbfields.CharField(max_length=50)
    preffered_protocol = dbfields.CharField(max_length=10, null=True)
    preffered_port = dbfields.IntField(max_length=5, null=True)

    users: dbfields.ReverseRelation["User"]

    def __str__(self):
        return f"Organisation {self.org_id}: {self.name}"


class User(Model):
    user_id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField(
        "models.Org", related_name="users", default=1)
    # : fields.ForeignKeyRelation(Org)
    username = dbfields.CharField(max_length=20)
    email = dbfields.CharField(255, validators=[RegexValidator(
        "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", re.I)])
    first_name = dbfields.CharField(max_length=50)
    last_name = dbfields.CharField(max_length=50, null=True, default="")
    password = dbfields.CharField(max_length=128)
    create_time = dbfields.DatetimeField(auto_now_add=True)
    last_login_time = dbfields.DatetimeField(auto_now=True)
    permission = dbfields.CharField(max_length=10, default="default")

    def __str__(self):
        return f"User {self.user_id}: {self.username}"


class UserValidation(Schema):
    org_id = fields.Int(load_default=1)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(load_default="")
    permission = fields.Str(load_default="default")


class Stream(Model):
    stream_id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField("models.Org", related_name="streams")
    name = dbfields.CharField(max_length=50)


class StreamValidation(Schema):
    org_id = fields.Int(load_default=1)
    name = fields.Str(required=True)


class Flow(Model):
    flow_id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField("models.Org", related_name="flows")
    stream_id = dbfields.ForeignKeyField(
        "models.Stream", related_name="flows", default=1)
    name = dbfields.CharField(max_length=50)
    create_time = dbfields.DatetimeField(auto_now_add=True)
    created_by = dbfields.ForeignKeyField(
        "models.User", related_name="users")
    protocol = dbfields.CharField(max_length=10, default="wireguard")
    port = dbfields.IntField(max_length=5, default=51820)
    status = dbfields.CharField(max_length=10, default="init")
    to = dbfields.CharField(max_length=50, null=True)


class FlowValidation(Schema):
    org_id = fields.Int(load_default=1)
    stream_id = fields.Int(load_default=1)
    name = fields.Str(required=True)
    protocol = fields.Str(load_default="wireguard")
    port = fields.Int(load_default=51820)
    status = fields.Str(load_default="init")
    to = fields.Str(load_default=None)
