from quart import Blueprint, request, jsonify
from app.services.user_service import create_user, get_users
from quart import jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
async def create_user_route():
    try:
        user_data = await request.get_json()
        response = await create_user(user_data)
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/users', methods=['GET'])
async def get_users_route():
    try:
        users = await get_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500