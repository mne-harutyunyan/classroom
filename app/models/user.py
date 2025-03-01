import re
from enum import Enum
from quart import abort
from bson import ObjectId
from typing import Optional
from http import HTTPStatus
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Role(str, Enum):
  admin = "admin"
  student = "student"

class User(BaseModel):
  _id: Optional[ObjectId] = None
  student_code: str = Field(...)
  name: str = Field(...)
  surname: str = Field(...)
  email: str = Field(...)
  phone_number: str = Field(...)
  role: Role = Field(default=Role.student)
  created_at: datetime = Field(default_factory=datetime.now)

  model_config = ConfigDict(from_attributes=True)

  @field_validator('name', 'surname', mode='before')
  @classmethod
  def validate_values(cls, value: str, info: str) -> str:
    if not value.strip():
      return abort(HTTPStatus.BAD_REQUEST, f"{info.field_name} field can't be empty.")
    if not 1 <= len(value) <= 50:
      return abort(HTTPStatus.BAD_REQUEST, f"{info.field_name} field should be between 1 and 50 characters in length.")
    return value
  
  @field_validator('phone_number', mode='before')
  @classmethod
  def validate_phone_number(cls, phone_number: str) -> str:
    if not re.match(r"^\+\d{6,}$", phone_number):
      return abort(HTTPStatus.BAD_REQUEST, "Invalid phone number")
    return phone_number
  
  @field_validator('role', mode='before')
  @classmethod
  def validate_role(cls, role: str) -> str:
    if role not in (Role.admin, Role.student):
      return abort(HTTPStatus.BAD_REQUEST, f"Invalid role. Valid roles are {Role._member_names_}")
    return role
  
  @field_validator('email', mode='before')
  @classmethod
  def validate_email(cls, email: str) -> str:
    email = email.strip().lower()
    if not email:
      return abort(HTTPStatus.BAD_REQUEST, "Email can't be empty.")

    pattern = (r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
               r"@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+"
               r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

    if not re.match(pattern, email):
      return abort(HTTPStatus.BAD_REQUEST, "Invalid email format.")

    return email