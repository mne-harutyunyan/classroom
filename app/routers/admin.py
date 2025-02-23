from quart import Blueprint, request, jsonify
from app.services.admin_service import get_all_reservations, create_user, delete_user, get_all_students
from quart import jsonify
from app.utils.helpers import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/get_reservations', methods=['GET'])
async def get_reservations():
    data = await request.get_json()
    result = await get_all_reservations(data)
    return jsonify(result), result['status_code']

@admin_bp.route("/add_student", methods = ['POST'])
@admin_required
async def add_user():
    data = await request.get_json()
    result = await create_user(data)
    return jsonify(result), result['status_code']

@admin_bp.route("/delete_student/<student_code>", methods = ['DELETE'])
@admin_required
async def delete_student(student_code):
    result = await delete_user(student_code)
    return jsonify(result), result['status_code']

@admin_bp.route("/get_all_students", methods=['GET'])
@admin_required
async def get_all_students_route():
    result = await get_all_students()
    return jsonify(result), result['status_code']