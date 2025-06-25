from config import app, db
from models import User, Recipe

with app.app_context():
    print("Clearing db...")
    Recipe.query.delete()
    User.query.delete()

    print("Seeding users...")
    u1 = User(username="kareey", image_url="https://i.pravatar.cc/150?img=4", bio="IAM Lab hero")
    u1.password_hash = "password123"

    db.session.add(u1)
    db.session.commit()

    print("Seeding recipes...")
    r1 = Recipe(
        title="Spaghetti Bolognese",
        instructions="Boil water. Cook spaghetti. In a separate pan, cook minced meat with onions, tomatoes, and seasoning for 15 minutes...",
        minutes_to_complete=30,
        user_id=u1.id
    )
    db.session.add(r1)
    db.session.commit()

    print("Done seeding!")

