from bson import ObjectId
from http import HTTPStatus
from datetime import datetime
from pymongo import ASCENDING

from app.database.sessions import db
from app.services.sms_service import send_sms
from app.models.reservation import Reservation
from app.utils.helpers import send_slack_notification


async def is_time_slot_available(room_name: str, start_date: datetime, end_date: datetime) -> bool:
  reservations_collection = db.get_collection('reservations')

  overlapping_reservations = await reservations_collection.find({
    'roomName': room_name,
    'status': 'approved',
    '$or': [
      {'startDate': {'$lt': end_date, '$gte': start_date}},
      {'endDate': {'$gt': start_date, '$lte': end_date}},
      {'startDate': {'$lte': start_date}, 'endDate': {'$gte': end_date}}]
  }).to_list(length=None)
  
  return len(overlapping_reservations) == 0


async def create_reservation(data: dict) -> dict:
  try:
    reservation = Reservation(**data)
  
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.BAD_REQUEST}
  
  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation.student_code})

  if not student:
    return {"error": "Invalid student code.", "status_code": HTTPStatus.BAD_REQUEST}

  reservations_collection = db.get_collection('reservations')
  reservation_dict = reservation.model_dump()
  reservations_collection = db.get_collection('reservations')
  reservation_dict['status'] = 'pending'

  available = await is_time_slot_available(
    reservation_dict['roomName'],
    reservation_dict['startDate'],
    reservation_dict['endDate'])

  if not available:
    return {"message": "Room is not available", "status_code": HTTPStatus.BAD_REQUEST}

  result = await reservations_collection.insert_one(reservation_dict)
  reservation_id = str(result.inserted_id)
  send_sms(student['phone_number'], "Reservation request submitted. Awaiting admin approval.")
  message = f'''
  📢 New Reservation Request:\n
  👤 Student: {student["name"]} {student["surname"]}\n
  🏫 Classroom: {reservation_dict['roomName'].value}\n
  🕒 Time: \n
  \t\tFrom: {reservation.startDate} \n
  \t\tTo: {reservation.endDate}\n 
  🔖 Reservation ID: {reservation_id}'''

  await send_slack_notification(message, reservation_id)
  return {"message": "Reservation request submitted and awaiting approval", "Reservation ID": reservation_id, "status_code": HTTPStatus.CREATED}


async def user_reject_reservation_service(reservation_id, student_code):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": HTTPStatus.NOT_FOUND}

  if reservation['student_code'] != student_code:
    return {"error": "You can only reject your own reservations.", "status_code": HTTPStatus.FORBIDDEN}

  if reservation['status'] not in ['pending', 'approved']:
    return {"error": "Only pending or approved reservations can be rejected.", "status_code": HTTPStatus.OK}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'rejected'}})

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})

  if student:
    send_sms(student['phone_number'], "Your reservation request has been rejected.")

  return {"message": "Reservation successfully rejected.", "status_code": HTTPStatus.OK}


async def build_reservation_query(filters: dict) -> dict:
  query = {"status": "approved"}

  if "roomName" in filters:
    query["roomName"] = filters["roomName"]

  if "startDate" in filters or "endDate" in filters:
    date_filter = {}
    if "startDate" in filters:
      try:
        date_filter["$gte"] = datetime.fromisoformat(filters["startDate"])
      except ValueError:
        return {"error": "Invalid startDate format. Use YYYY-MM-DDTHH:MM:SS", "status_code": HTTPStatus.BAD_REQUEST}
    if "endDate" in filters:
      try:
        date_filter["$lte"] = datetime.fromisoformat(filters["endDate"])
      except ValueError:
        return {"error": "Invalid endDate format. Use YYYY-MM-DDTHH:MM:SS", "status_code": HTTPStatus.BAD_REQUEST}
    query["startDate"] = date_filter

  if "roomType" in filters:
    query["roomType"] = filters["roomType"]

  if filters.get("available") == "true":
    current_time = datetime.now()
    query["endDate"] = {"$gte": current_time}

  return query


async def get_student_reservations(filters: dict):
  reservations_collection = db.get_collection('reservations')

  page = int(filters.get("page", 1))
  size = int(filters.get("size", 10))

  if page < 1 or size < 1 or size > 100:
    return {"status_code": HTTPStatus.BAD_REQUEST, "description": "Page must be >= 1 and size must be between 1 and 100."}

  query = await build_reservation_query(filters)

  if "error" in query:
    return query

  skip_count = (page - 1) * size

  cursor = reservations_collection.find(query).sort("_id", ASCENDING).skip(skip_count).limit(size)
  reservations = await cursor.to_list(length=size)

  if not reservations:
    return {"error": "No approved reservations found", "status_code": HTTPStatus.NOT_FOUND}

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
    "status_code": HTTPStatus.OK}