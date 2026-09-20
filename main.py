from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine

from models import User, Message, Product, Transaction, Note
Base.metadata.create_all(bind=engine)

from routers import auth_router, users, chats, shop, admin

app = FastAPI(
    title="Dating App API",
    version="1.0.0",
    description="Backend für die Dating App",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(chats.router)
app.include_router(shop.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Dating App API läuft!", "docs": "/docs"}


@app.on_event("startup")
def seed_data():
    from database import SessionLocal
    from auth import hash_password

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            print("🌱 Erstelle Demo-Daten...")

            admin = User(
                name="Admin",
                email="admin@test.de",
                password_hash=hash_password("admin123"),
                age=30,
                bio="Ich bin der Admin",
                coins=9999,
                is_admin=True,
                is_verified=True,
            )
            db.add(admin)

            demo_users = [
                ("Anna", "anna@test.de", 28, "Kaffee & Reisen", 150),
                ("Ben", "ben@test.de", 32, "Sport & Kochen", 80),
                ("Clara", "clara@test.de", 25, "Kunst & Musik", 200),
                ("David", "david@test.de", 30, "Technik & Fotografie", 50),
            ]

            for name, email, age, bio, coins in demo_users:
                user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password("test123"),
                    age=age,
                    bio=bio,
                    image_url=f"https://picsum.photos/seed/{name.lower()}/600/800",
                    extra_photos=f"https://picsum.photos/seed/{name.lower()}2/600/800,https://picsum.photos/seed/{name.lower()}3/600/800",
                    interests="Reisen,Kaffee,Musik",
                    coins=coins,
                    is_verified=True,
                )
                db.add(user)

            products = [
                ("Profil-Foto freischalten", "Zusätzliches Foto", 50, "photo"),
                ("Direktnachricht senden", "Nachricht an User", 20, "message"),
                ("Super Like", "Besonderes Interesse", 30, "feature"),
                ("Premium (30 Tage)", "Alle Features", 500, "premium"),
            ]
            for name, desc, price, cat in products:
                db.add(Product(
                    name=name,
                    description=desc,
                    price_coins=price,
                    category=cat,
                    image_url=f"https://picsum.photos/seed/{cat}/400/300",
                ))

            db.commit()
            print("✅ Demo-Daten erstellt!")
            print("   Admin-Login: admin@test.de / admin123")
            print("   User-Login:  anna@test.de / test123")
    finally:
        db.close()