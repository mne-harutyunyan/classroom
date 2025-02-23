from app.database.sessions import db
from app.models.user import User

async def get_all_reservations(data: dict):
    
  reservations_collection = db.get_collection('reservations')
  try:
    reservations = await reservations_collection.find().to_list(length=100)
    if not reservations:
        return {"error": "No reservations found.","status_code":404}

    for reservation in reservations:
        reservation["_id"] = str(reservation["_id"])

    return {"reservations": reservations,"status_code":200}
  except Exception as e:
    return {"error": str(e), "status_code":500}
  
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
