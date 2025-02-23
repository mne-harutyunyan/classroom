from datetime import datetime
from app.database.sessions import db
from app.models.user import User
from app.models.reservation import Reservation
from app.services.sms_service import send_sms

async def is_time_slot_available(room_name: str, start_date: datetime, end_date: datetime) -> bool:
  reservations_collection = db.get_collection('reservations')
  
  overlapping_reservations = reservations_collection.find({
    'roomName': room_name,
    '$or': [
      {'startDate': {'$lt': end_date, '$gte': start_date}},
      {'endDate': {'$gt': start_date, '$lte': end_date}},
      {'startDate': {'$lte': start_date}, 'endDate': {'$gte': end_date}}]})

  overlapping_count = await overlapping_reservations.to_list()
  if len(overlapping_count) > 0:
     return False
  return True

async def create_reservation(data: dict) -> dict:
  try:
    reservation = Reservation(**data)
  except Exception as e:
    return {"error": str(e), "status_code": 400}

  students_collection = db.get_collection('students')

  student = await students_collection.find_one({'student_code': reservation.student_code})

  if not student:
    return {"error": "Invalid student code.", "status_code": 400}

  if not await is_time_slot_available(reservation.roomName, reservation.startDate, reservation.endDate):
    return {"error": "The selected time slot is already booked.", "status_code": 400}

  reservations_collection = db.get_collection('reservations')
  reservation_dict = reservation.model_dump()
  await reservations_collection.insert_one(reservation_dict)
  send_sms(student['phone_number'],"Reservation created successfully")
  return {"message": "Reservation created successfully", "status_code":201}