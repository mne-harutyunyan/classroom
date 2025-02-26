from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField, EnumField
from app.models.reservation import RoomName, RoomType, Status

class ReservationSchema(Document):
  _id = IntField
  roomType = EnumField(RoomType)
  roomName = EnumField(RoomName)
  startDate = DateTimeField
  endDate = DateTimeField
  isFixed = BooleanField
  group = StringField
  teacher = StringField
  recording = BooleanField
  status = EnumField(Status)