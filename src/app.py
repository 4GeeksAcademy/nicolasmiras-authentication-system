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
from models import db, User, Planet, Character, Favorite_Character, Favorite_Planet

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

################################


@app.route('/character', methods=['GET'])
def get_characters():

    all_characters = db.session.execute(select(Character)).scalars().all()
    result = list(map(lambda character: character.serialize(),all_characters))

    return jsonify(result), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):

    character=db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()

    return jsonify(character.serialize()), 200

@app.route('/planet', methods=['GET'])
def get_planets():

    all_planets = db.session.execute(select(Planet)).scalars().all()
    result = list(map(lambda planet: planet.serialize(),all_planets))

    return jsonify(result), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    planet=db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()

    return jsonify(planet.serialize()), 200


@app.route('/user', methods=['GET'])
def get_users():

    all_users = db.session.execute(select(User)).scalars().all()
    result = list(map(lambda user: user.serialize(),all_users))

    return jsonify(result), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    
    favorite_characters = (
        db.session.execute(
            select(Favorite_Character).where(Favorite_Character.id_user == user_id)
        ).scalars().all()
    )

    characters_result = [
        fav.character.serialize() for fav in favorite_characters if fav.character
    ]

    favorite_planets = (
        db.session.execute(
            select(Favorite_Planet).where(Favorite_Planet.id_user == user_id)
        ).scalars().all()
    )

    planets_result = [
        fav.planet.serialize() for fav in favorite_planets if fav.planet
    ]

    return jsonify({
        "user_id": user_id,
        "favorite_characters": characters_result,
        "favorite_planets": planets_result
    }), 200



@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    data = request.get_json()
    user_id = data.get("user_id")

    new_favorite = Favorite_Planet(id_planet=planet_id, id_user=user_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"planet_id": planet_id, "status": "added"}), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):

    data = request.get_json()
    user_id = data.get("user_id") 

    new_favorite = Favorite_Character(id_character=people_id, id_user=user_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"people_id": people_id, "status": "added"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    data = request.get_json()
    user_id = data.get("user_id")

    favorite = db.session.execute(
        select(Favorite_Planet).where(
            Favorite_Planet.id_user == user_id,
            Favorite_Planet.id_planet == planet_id
        )
    ).scalar_one()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"planet_id": planet_id, "status": "removed"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    
    data = request.get_json()
    user_id = data.get("user_id")

    favorite = db.session.execute(
        select(Favorite_Character).where(
            Favorite_Character.id_user == user_id,
            Favorite_Character.id_character == people_id
        )
    ).scalar_one()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"people_id": people_id, "status": "removed"}), 200



@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user= User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"msg": "usuario no existente"}), 401


    if password != user.password:
        return jsonify({"msg": "email o password incorrecto"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


################################


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
