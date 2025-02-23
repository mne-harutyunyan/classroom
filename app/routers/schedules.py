from quart import Blueprint, request, jsonify
from quart import jsonify
from app.services.schedule_service import book_room, get_schedules

schedule_bp = Blueprint('schedule', __name__)
    
@schedule_bp.route('/schedule', methods=['POST'])
async def book_room_route():
  try:
      data = await request.get_json()
      schedule_id = await book_room(data)
      return jsonify({
          "message": "Booked successfully!",
          "schedule_id": schedule_id
      }), 201
  except ValueError as ve:
      return jsonify({"error": f"Validation error: {str(ve)}"}), 400
  except Exception as e:
      return jsonify({"error": str(e)}), 500

@schedule_bp.route('/schedule', methods=['GET'])
async def get_schedules_route():
  try:
      schedules = await get_schedules()
      return jsonify(schedules), 200
  except Exception as e:
      return jsonify({"error": str(e)}), 500

