import os
from http import HTTPStatus

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import ValidationError

from schemas import partial_user_schema, user_schema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
db = SQLAlchemy()
db.init_app(app)
# https://flask-migrate.readthedocs.io/en/latest/#api-reference
migrate = Migrate(app, db)
migrate.init_app(app, db)

# https://github.com/sveint/flask-swagger-ui
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.yml"

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
)

app.register_blueprint(swaggerui_blueprint)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


@app.route("/api/health")
def health():
    return {"msg": "pass"}


@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), HTTPStatus.OK


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"msg": "該当するユーザが存在しません"}),
            HTTPStatus.NOT_FOUND,
        )
    return jsonify(user.to_dict()), HTTPStatus.OK


@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return (
            jsonify({"msg": "Invalid input", "errors": err.messages}),
            HTTPStatus.BAD_REQUEST,
        )

    if User.query.filter_by(email=data["email"]).first():
        return (
            jsonify({"msg": "すでに存在するメールアドレスです"}),
            HTTPStatus.BAD_REQUEST,
        )

    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), HTTPStatus.CREATED


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"msg": "該当するユーザが存在しません"}),
            HTTPStatus.NOT_FOUND,
        )

    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return (
            jsonify({"msg": "Invalid input", "errors": err.messages}),
            HTTPStatus.BAD_REQUEST,
        )

    user.name = data["name"]
    user.email = data["email"]
    db.session.commit()
    return jsonify(user.to_dict()), HTTPStatus.OK


@app.route("/api/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"msg": "該当するユーザが存在しません"}),
            HTTPStatus.NOT_FOUND,
        )

    try:
        data = partial_user_schema.load(request.get_json())
    except ValidationError as err:
        return (
            jsonify({"msg": "Invalid input", "errors": err.messages}),
            HTTPStatus.BAD_REQUEST,
        )

    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify(user.to_dict()), HTTPStatus.OK


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"msg": "該当するユーザが存在しません"}),
            HTTPStatus.NOT_FOUND,
        )

    db.session.delete(user)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT
