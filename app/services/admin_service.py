from bson import ObjectId
from pymongo import ASCENDING

from app.models.user import User
from app.database.sessions import db
from app.services.sms_service import send_sms
from app.services.user_service import is_time_slot_available

async def get_all_reservations(filters: dict):
    reservations_collection = db.get_collection('reservations')
    try:
        page = int(filters.get("page", 1))
        size = int(filters.get("size", 10))
        if page < 1 or size < 1 or size > 100:
            return {"status_code":400, "message":"Page must be >= 1 and size must be between 1 and 100."}

        query = {}
        if "status" in filters:
            query["status"] = filters["status"]
        if "student_code" in filters:
            query["student_code"] = filters["student_code"]

        skip_count = (page - 1) * size

        cursor = reservations_collection.find(query).sort("_id", ASCENDING).skip(skip_count).limit(size)
        reservations = await cursor.to_list(length=size)

        if not reservations:
            return {"error": "No reservations found.", "status_code": 404}

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
                "total_pages": total_pages
            },
            "status_code": 200
        }

    except Exception as e:
        return {"error": str(e), "status_code": 500}
  
async def create_user(data: dict):
  students_collection = db.get_collection('students')
  student = User(**data) 
  
  try:
    existing_student = await students_collection.find_one({'student_code': student.student_code})
    if existing_student:
      return {"error": "Student with this student_code already exists", "status_code": 400}
    result = await students_collection.insert_one(student.model_dump())
    return {"message": "Student created successfully", "status_code": 201, "student_id": str(result.inserted_id)}
  except Exception as e:
    return {"error": str(e), "status_code": 500}
  
async def delete_user(student_code: str):
  students_collection = db.get_collection('students')
  try:
    existing_student = await students_collection.find_one({'student_code': student_code})
    if not existing_student:
      return {"error": "Student with this code does not exists", "status_code": 400}
    result = await students_collection.delete_one({'student_code': student_code})
    return {"message": "Student deleted successfully", "status_code": 201}
  except Exception as e:
    return {"error": str(e), "status_code": 500}
  
async def get_all_students():
  students_collection = db.get_collection('students')
  try:
    students_cursor = students_collection.find({})
    students = []
    async for student in students_cursor:
      student['_id'] = str(student['_id'])
      students.append(student)
    return {"students": students, "status_code": 200}
  except Exception as e:
      return {"error": str(e), "status_code": 500}


async def approve_reservation_service(reservation_id):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": 404}

  if reservation['status'] != 'pending':
    return {"error": "Reservation already processed.", "status_code": 400}

  if not await is_time_slot_available(reservation['roomName'], reservation['startDate'], reservation['endDate']):
    return {"error": "Time slot is no longer available.", "status_code": 400}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'approved'}})

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})
  if student:
    send_sms(student['phone_number'], "Your reservation has been approved.")

  return {"message": "Reservation approved successfully.", "status_code": 200}


async def reject_reservation_service(reservation_id):
  reservations_collection = db.get_collection('reservations')
  reservation = await reservations_collection.find_one({'_id': ObjectId(reservation_id)})

  if not reservation:
    return {"error": "Reservation not found.", "status_code": 404}

  if reservation['status'] != 'pending':
    return {"error": "Reservation already processed.", "status_code": 400}

  await reservations_collection.update_one(
    {'_id': ObjectId(reservation_id)},
    {'$set': {'status': 'rejected'}})

  students_collection = db.get_collection('students')
  student = await students_collection.find_one({'student_code': reservation['student_code']})
  if student:
    send_sms(student['phone_number'], "Your reservation request has been rejected.")

  return {"message": "Reservation rejected successfully.", "status_code": 200}