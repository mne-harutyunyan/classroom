from bson import ObjectId
from datetime import datetime
from pymongo import ASCENDING

from app.database.sessions import db
from app.services.sms_service import send_sms
from app.models.reservation import Reservation
from app.utils.helpers import send_slack_notification

async def is_time_slot_available(room_name: str, start_date: datetime, end_date: datetime) -> bool:
  reservations_collection = db.get_collection('reservations')
  
  overlapping_reservations = reservations_collection.find({
    'roomName': room_name,
    'status': 'approved', 
    '$or': [
        {'startDate': {'$lt': end_date, '$gte': start_date}},
        {'endDate': {'$gt': start_date, '$lte': end_date}},
        {'startDate': {'$lte': start_date}, 'endDate': {'$gte': end_date}}]})

  overlapping_count = await overlapping_reservations.to_list()
  return len(overlapping_count) == 0

async def create_reservation(data: dict) -> dict:
  try:
    reservation = Reservation(**data)
  except Exception as e:
    return {"error": str(e), "status_code": 400}

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation.student_code})
  if not student:
    return {"error": "Invalid student code.", "status_code": 400}

  reservations_collection = db.get_collection('reservations')
  reservation_dict = reservation.model_dump()
  reservation_dict['status'] = 'pending'
  hello = await reservations_collection.insert_one(reservation_dict)
  send_sms(student['phone_number'], "Reservation request submitted. Awaiting admin approval.")
  reservation_id = str(hello.inserted_id)
  message = f"📢 New Reservation Request:\n👤 Student Code: {reservation.student_code}\n🏫 Classroom: {reservation.roomName.name}\n🕒 Time: {reservation.startDate}:{reservation.endDate}\n Reservation ID: {reservation_id}"
  await send_slack_notification(message,reservation_id)
  return {"message": "Reservation request submitted and awaiting approval.", "status_code": 201}

async def user_reject_reservation_service(reservation_id, student_code):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": 404}

  if reservation['student_code'] != student_code:
    return {"error": "You can only reject your own reservations.", "status_code": 403}

  if reservation['status'] not in ['pending', 'approved']:
    return {"error": "Only pending or approved reservations can be rejected.", "status_code": 400}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'rejected'}})
  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})
  if student:
    send_sms(student['phone_number'], "Your reservation request has been rejected.")
  return {"message": "Reservation successfully rejected.", "status_code": 200}

async def get_student_reservations(filters: dict):
  reservations_collection = db.get_collection('reservations')
  
  page = int(filters.get("page", 1))
  size = int(filters.get("size", 10))
  if page < 1 or size < 1 or size > 100:
    return {"status_code":400, "description":"Page must be >= 1 and size must be between 1 and 100."}
  query = {"status": "approved"}

  skip_count = (page - 1) * size

  cursor = reservations_collection.find(query).sort("_id", ASCENDING).skip(skip_count).limit(size)
  reservations = await cursor.to_list(length=size)

  if not reservations:
    return {"error": "No approved reservations found", "status_code": 404}

  for reservation in reservations:
    reservation["_id"] = str(reservation["_id"])

  total_count = await reservations_collection.count_documents(query)
  total_pages = (total_count + size - 1) // size

  return {
      "reservations": reservations,
      "pagination": {
          "total": total_count,
          "page": page,
          "size": size,
          "total_pages": total_pages},
      "status_code": 200}