from tortoise import Model, fields
from tortoise.validators import RegexValidator
import re


class Org(Model):
    org_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    contact = fields.CharField(max_length=50)
    preffered_protocol = fields.CharField(max_length=10, null=True)
    preffered_port = fields.IntField(max_length=5, null=True)

    users: fields.ReverseRelation["User"]

    def __str__(self):
        return f"Organisation {self.org_id}: {self.name}"


class User(Model):
    user_id = fields.IntField(pk=True)
    org_id = fields.ForeignKeyField(
        "models.Org", related_name="users", default=1)
    # : fields.ForeignKeyRelation(Org)
    username = fields.CharField(max_length=20)
    email = fields.CharField(255, validators=[RegexValidator(
        "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", re.I)])
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50, null=True, default="")
    password = fields.CharField(max_length=128)
    create_time = fields.DatetimeField(auto_now_add=True)
    last_login_time = fields.DatetimeField(auto_now=True)
    permission = fields.CharField(max_length=10, default="default")

    def __str__(self):
        return f"User {self.user_id}: {self.username}"
