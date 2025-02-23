from functools import wraps
from quart import request, jsonify

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Assume the role is passed in headers for simplicity
        user_role = request.headers.get("Role")
        
        if user_role != "admin":
            return jsonify({"error": "Admin access required"}), 403  # Forbidden
        
        return await func(*args, **kwargs)
    
    return wrapper