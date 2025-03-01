from quart import Quart
from quart_schema import QuartSchema

from app.routers.users import user_bp
from app.routers.admin import admin_bp


app = Quart(__name__)
QuartSchema(app,info={"title": "Academy Classroom", "version": "0.0.1"})

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)