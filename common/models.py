from tortoise import Model
from tortoise import fields as dbfields
from tortoise.validators import RegexValidator
from marshmallow import Schema, fields, EXCLUDE
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


class River(Model):
    river_id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField("models.Org", related_name="rivers")
    name = dbfields.CharField(max_length=50)
    initiated = dbfields.BooleanField(default=False)

    class Meta:
        unknown = EXCLUDE


class RiverValidation(Schema):
    org_id = fields.Int(load_default=1)
    name = fields.Str(required=True)
    initiated = fields.Bool(load_default=False)


class Stream(Model):
    id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField(
        "models.Org", related_name="streams")
    river_id = dbfields.ForeignKeyField(
        "models.River", related_name="rivers")
    flow_id = dbfields.ForeignKeyField("models.Flow", related_name="flows")
    role = dbfields.CharField(default="client", max_length=6)
    protocol = dbfields.CharField(max_length=10, default="wireguard")
    port = dbfields.IntField(max_length=5, default=51820)
    config = dbfields.CharField(null=True, max_length=1000)
    tunnel = dbfields.CharField(null=True, max_length=1000)
    error = dbfields.CharField(null=True, max_length=1000)


class StreamValidation(Schema):
    org_id = fields.Int(load_default=1)
    river_id = fields.Int(required=True)
    flow_id = fields.Int(required=True)
    role = fields.Str(load_default="client")
    protocol = fields.Str(load_default="wireguard")
    port = fields.Int(load_default=51820)
    config = fields.Str()
    tunnel = fields.Str()
    error = fields.Str()


class Flow(Model):
    flow_id = dbfields.IntField(pk=True)
    org_id = dbfields.ForeignKeyField("models.Org", related_name="flows")
    name = dbfields.CharField(max_length=50)
    create_time = dbfields.DatetimeField(auto_now_add=True)
    created_by = dbfields.ForeignKeyField(
        "models.User", related_name="users")
    status = dbfields.CharField(max_length=10, default="init")
    description = dbfields.CharField(max_length=255, null=True, default="")
    monitor = dbfields.BooleanField(default=True)
    api_key = dbfields.CharField(max_length=36)


class FlowCreateValidation(Schema):
    org_id = fields.Int(load_default=1)
    name = fields.Str(required=True)
    status = fields.Str(load_default="init")
    description = fields.Str(load_default="")
    monitor = fields.Boolean(load_default=True)


class FlowModifyValidation(Schema):
    name = fields.Str()
    description = fields.Str()
    monitor = fields.Boolean()

    class Meta:
        unknown = EXCLUDE
