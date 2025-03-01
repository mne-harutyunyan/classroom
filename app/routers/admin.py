from http import HTTPStatus
from quart import Blueprint, request, jsonify

from app.utils.helpers import admin_required
from app.services.admin_service import (
  process_slack_action,
  get_all_reservations,
  create_user,
  delete_user,
  get_all_students,
  approve_reservation_service,
  reject_reservation_service
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/get_reservations', methods=['GET'])
@admin_required
async def get_reservations():
  try:
    filters = request.args
    result = await get_all_reservations(filters)
    return jsonify(result), result["status_code"]
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route("/add_student", methods=['POST'])
@admin_required
async def add_user():
  try:
    data = await request.get_json()
    result = await create_user(data)
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route("/delete_student/<student_code>", methods=['DELETE'])
@admin_required
async def delete_student(student_code):
  try:
    result = await delete_user(student_code)
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route("/get_all_students", methods=['GET'])
@admin_required
async def get_all_students_route():
  try:
    result = await get_all_students()
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route('/approve/<reservation_id>', methods=['POST'])
@admin_required
async def approve_reservation(reservation_id):
  try:
    result = await approve_reservation_service(reservation_id)
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route('/reject/<reservation_id>', methods=['POST'])
@admin_required
async def reject_reservation(reservation_id):
  try:
    result = await reject_reservation_service(reservation_id)
    return jsonify(result), result['status_code']
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}

@admin_bp.route('/slack/actions', methods=['POST'])
async def handle_slack_actions():
  try:
    body = await request.form
    payload = body.get("payload")
    if not payload:
      return jsonify({"text": "Missing payload!"}), HTTPStatus.BAD_REQUEST
    return await process_slack_action(payload)
  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}