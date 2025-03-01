import json
from quart import jsonify
from bson import ObjectId
from http import HTTPStatus
from pymongo import ASCENDING
from datetime import datetime

from app.models.user import User
from app.database.sessions import db
from app.services.sms_service import send_sms
from app.services.user_service import is_time_slot_available


async def build_reservation_query(filters: dict) -> dict:
  query = {}

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

async def get_all_reservations(filters: dict):
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


async def create_user(data: dict):
  students_collection = db.get_collection('students')
  try:
    student = User(**data)
  
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.BAD_REQUEST}
    
  existing_student = await students_collection.find_one({'student_code': student.student_code})

  if existing_student:
    return {"error": "Student with this Student Code already exists", "status_code": HTTPStatus.BAD_REQUEST}

  result = await students_collection.insert_one(student.model_dump())
  return {"message": "Student created successfully",
          "status_code": HTTPStatus.CREATED,
          "student_id": str(result.inserted_id)}


async def delete_user(student_code: str):
  students_collection = db.get_collection('students')
  existing_student = await students_collection.find_one({'student_code': student_code})

  if not existing_student:
    return {"error": "Student with this code does not exists", "status_code": HTTPStatus.BAD_REQUEST}

  result = await students_collection.delete_one({'student_code': student_code})
  return {"message": "Student deleted successfully", "status_code": HTTPStatus.OK}


async def get_all_students():
  students_collection = db.get_collection('students')
  students_cursor = students_collection.find({})
  students = []

  async for student in students_cursor:
    student['_id'] = str(student['_id'])
    students.append(student)

  return {"students": students, "status_code": HTTPStatus.OK}


async def approve_reservation_service(reservation_id):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": HTTPStatus.NOT_FOUND}

  if reservation['status'] != 'pending':
    return {"error": "Reservation already processed.", "status_code": HTTPStatus.BAD_REQUEST}

  if not await is_time_slot_available(reservation['roomName'], reservation['startDate'], reservation['endDate']):
    return {"error": "Time slot is no longer available.", "status_code": HTTPStatus.BAD_REQUEST}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'approved'}})

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})

  if student:
    send_sms(student['phone_number'], "Your reservation has been approved.")

  return {"message": "Reservation approved successfully.", "status_code": HTTPStatus.OK}


async def reject_reservation_service(reservation_id):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": HTTPStatus.NOT_FOUND}

  if reservation['status'] != 'pending':
    return {"error": "Reservation already processed.", "status_code": HTTPStatus.BAD_REQUEST}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'rejected'}})

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})

  if student:
    send_sms(student['phone_number'], "Your reservation request has been rejected.")

  return {"message": "Reservation rejected successfully.", "status_code": HTTPStatus.OK}


async def process_slack_action(payload):
  
  data = json.loads(payload)

  actions = data.get("actions", [])
  if not actions:
    return jsonify({"text": "No actions found!"}), HTTPStatus.BAD_REQUEST

  action = actions[0].get("value")
  reservation_id = data.get("callback_id")

  if not reservation_id:
    return jsonify({"text": "Missing reservation ID!"}), HTTPStatus.BAD_REQUEST

  if action == "approve":
    await approve_reservation_service(reservation_id=reservation_id)
    response_text = f"Reservation approved!\nReservation ID: {reservation_id}"

  elif action == "reject":
    await reject_reservation_service(reservation_id=reservation_id)
    response_text = f"Reservation rejected!\nReservation ID: {reservation_id}"

  else:
    return jsonify({"text": "Invalid action!"}), HTTPStatus.BAD_REQUEST

  return jsonify({"text": response_text})