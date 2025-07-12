from flask import Flask
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager,jwt_required,get_jwt
from OCRSpace.routes import ocr_bp
from Auth.routes import auth_bp
from Database.routes import db_bp
from flask_cors import CORS


app = Flask(__name__)
jwt = JWTManager(app)
BLOCKLIST = set()
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return {
        "message": "InkGrader Backend API"
    }

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLOCKLIST


@auth_bp.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    jti = get_jwt()["jti"]
    if jti:
        BLOCKLIST.add(jti)
        return {"message": "Logged out successfully"}, 200
    else:
        return {"message": "No active token found"}, 401


@app.errorhandler(404)
def not_found(error):
    return {"message": "Not found"}, 404


if __name__ == "__main__":
    app.register_blueprint(ocr_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(db_bp)
    load_dotenv()
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLOCKLIST

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=120)
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["DEBUG"] = True
    app.config["PORT"] = os.getenv("PORT", 3000)
    app.run()
