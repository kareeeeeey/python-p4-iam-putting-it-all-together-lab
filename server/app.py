from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, User, Recipe
from config import app, db, api
from sqlalchemy.exc import IntegrityError

# Signup
class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data.get("username"),
                image_url=data.get("image_url"),
                bio=data.get("bio"),
            )
            user.password_hash = data.get("password")

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id
            return user.to_dict(), 201

        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username must be unique"]}, 422

        except Exception as e:
            return {"errors": [str(e)]}, 422

# CheckSession
class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)
        return user.to_dict(), 200

# Login
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password")):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401

# Logout
class Logout(Resource):
    def delete(self):
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401

        session.pop("user_id")
        return {}, 204

# RecipeIndex
class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)
        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        if not data.get("instructions") or len(data.get("instructions")) < 50:
            return {"errors": ["Instructions must be at least 50 characters."]}, 422

        try:
            recipe = Recipe(
                title=data.get("title"),
                instructions=data.get("instructions"),
                minutes_to_complete=data.get("minutes_to_complete"),
                user_id=user_id,
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

# Routes
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

# Health Check
@app.route("/")
def index():
    return {"message": "IAM Lab API is running ✅"}

if __name__ == "__main__":
    app.run(port=5555, debug=True)


