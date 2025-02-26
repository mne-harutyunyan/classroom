from enum import Enum
from bson import ObjectId
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

class RoomType(str, Enum):
  classroom = "Classroom"
  meeting_room = "Meeting Room"
  spaces = "Spaces"
  others = "Others"

class Status(str, Enum):
  pending = "pending"
  approved = "approved"
  declined = "declined"

class RoomName(str,Enum):
  ada_lovelace = 'Ada Lovelace'
  alan_turing = "Alan Turing"
  claude_shannon = "Claude Shannon"
  donald_knuth = "Donald Knuth"
  library = "Library"
  william_shockley = "William Shockley"
  darth_vader = "Darth Vader"
  sirius = "Sirius"
  proxima = "Proxima"
  black = "Black"
  blue = "Blue"
  yellow = "Yellow"
  green = "Green"
  recording_room = "Recording room"
  call_room_N2 = "Call Room N2"

class Reservation(BaseModel):
  _id: Optional[ObjectId] = None
  student_code: str = Field(...)
  roomType: RoomType = Field(...)
  roomName: RoomName = Field(...)
  startDate: datetime = Field(...)
  endDate: datetime = Field(...)
  isFixed: bool
  group: str
  teacher: str
  recording: bool
  status: Status = Field(...)
  created_at: datetime = Field(default_factory=datetime.now)

  model_config = ConfigDict(from_attributes=True)
    
  @model_validator(mode='before')
  @classmethod
  def validate_dates(cls, values):
      start_date = values.get("startDate")
      end_date = values.get("endDate")
      if start_date and end_date and end_date <= start_date:
          raise ValueError("endDate must be after startDate")
      return values