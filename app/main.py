from quart import Quart
from app.routers.users import user_bp
from app.routers.schedules import schedule_bp

app = Quart(__name__)

app.register_blueprint(user_bp)
app.register_blueprint(schedule_bp)
