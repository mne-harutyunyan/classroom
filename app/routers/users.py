from quart import Blueprint, request, jsonify
from app.services.user_service import create_reservation
from quart import jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
async def create():
    data = await request.get_json()
    message = await create_reservation(data)
    return jsonify(message), message['status_code']