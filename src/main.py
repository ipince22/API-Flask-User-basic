"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=["GET"])
def lista_usuarios():
    users = User.query.all()
    request_body = list(map(lambda user:user.serialize(),users))
    return jsonify(request_body),200

@app.route('/user/<id>', methods=["GET"])
def lista_un_usuario(id):
    user1 = User.query.filter_by(id=id).first()
    if user1 is None:
        return APIException("No se encontro el usuario",status_code=404)
    request_body = user1.serialize()
    return jsonify(request_body),200


@app.route('/user', methods=["POST"])
def crear_usuarios():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"],method='sha256')
    user1 = User(username=data["username"],email=data["email"],password=hashed_password)
    db.session.add(user1)
    db.session.commit()
    return jsonify("Message : Se adiciono un usuario!"),200

@app.route('/user/<id>', methods=["PUT"])
def update_usuarios(id):
    request_body = request.get_json()
    user1 = User.query.get(id)
    if user1 is None:
        raise APIException("usuario no existe!", status_code=404)
    
    if "email" in request_body:
        user1.email = request_body["email"]
    db.session.commit()
    
    return jsonify("usuario Update, OK!"),200

@app.route('/user/<id>', methods=["DELETE"])
def delete_usuarios(id):
    user1 = User.query.get(id)
    if user1 is None:
        raise APIException("usuario no existe!",status_code=404)
    db.session.delete(user1)
    db.session.commit()
    return jsonify("Registro eliminado,ok!"),200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
