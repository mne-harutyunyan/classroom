from quart import Quart
from app.routers.users import user_bp
from app.routers.admin import admin_bp
from quart_schema import QuartSchema

app = Quart(__name__)
QuartSchema(app)

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
