from mongoengine import Document, StringField, DateTimeField, EmailField, EnumField
from app.models.user import Role

class UserSchema(Document):
  _id = StringField(max_length=20000000)
  name = StringField(min_length=3)
  surname = StringField(min_length=3)
  email = EmailField(domain_whitelist=["example.com","gmail.com"])
  phone_number = StringField(min_length=3)
  role = EnumField(Role)
  created_at = DateTimeField(db_field=None)