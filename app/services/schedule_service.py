from datetime import datetime
from app.database.sessions import db
from app.models.schedule import Schedule

async def book_room(data):
  try:
      schedule = Schedule(**data)
      result = await db.schedules.insert_one(schedule.model_dump(exclude={'_id'}))
      return str(result.inserted_id)  
  except ValueError as ve:
      raise ve
  except Exception as e:
      raise Exception("An error occurred while booking the room")


async def get_schedules():
    try:
        schedules_cursor = db.schedules.find()
        schedules = [{**schedule,
                "_id": str(schedule["_id"]),  # Convert ObjectId to string
                "created_at": schedule["created_at"].isoformat(),
                "startDate": schedule["startDate"].isoformat(),
                "endDate": schedule["endDate"].isoformat() if schedule.get("endDate") else None}
            async for schedule in schedules_cursor]
        return schedules
    except Exception as e:
        raise Exception(f"Error fetching schedules: {str(e)}")