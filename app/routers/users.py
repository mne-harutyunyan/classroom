from quart import Blueprint, request, jsonify

from app.services.user_service import create_reservation, user_reject_reservation_service, get_student_reservations

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
async def create():
  try:
    data = await request.get_json()
    message = await create_reservation(data)
    return jsonify(message), message['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": 500}

@user_bp.route('/reject/<reservation_id>', methods=['POST'])
async def user_reject_reservation(reservation_id):
  try:
    data = await request.get_json()
    student_code = data.get('student_code')
    if not student_code:
      return jsonify({"error": "Student code is required."}), 400
    result = await user_reject_reservation_service(reservation_id, student_code)
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": 500}

@user_bp.route('/get_approved_reservations', methods=['GET'])
async def get_approved_reservations():
  try:
    filters = request.args
    result = await get_student_reservations( filters)
    return jsonify(result), result["status_code"]
  except Exception as e:
    return {"error": str(e), "status_code": 500}
