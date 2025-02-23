from datetime import datetime
from app.database.sessions import db
from app.models.user import User

async def create_user(user_data):
  try:
    user = User(**user_data, created_at=datetime.now())
    await db.users.insert_one(user.model_dump(exclude={'_id'}))
    return {"message": "User created successfully!"} 
  except Exception as e:
    raise Exception(f"Error creating user: {str(e)}")

async def get_users():
  try:
    users_cursor = db.users.find()
    users = [{**user,
            "_id": str(user["_id"]),
            "created_at": user["created_at"].isoformat() if user.get("created_at") else None}
        async for user in users_cursor]
    return users 
  except Exception as e:
    raise Exception(f"Error fetching users: {str(e)}")
