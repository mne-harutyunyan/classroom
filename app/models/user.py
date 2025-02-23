from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum
from bson import ObjectId

class Role(str, Enum):
  admin = "admin"
  student = "student"

class User(BaseModel):
  _id: Optional[ObjectId] = None
  student_code: str
  name: str
  surname: str
  email: str
  phone_number: str
  role: Role
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)