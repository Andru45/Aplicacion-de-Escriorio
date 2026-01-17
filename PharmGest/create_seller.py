from src.pharmgest.config.database import SessionLocal
from src.pharmgest.database.models import User

session = SessionLocal()

# Verificar si ya existe
if session.query(User).filter_by(username="vendedor").first():
    print("El vendedor ya existe.")
else:
    new_user = User(
        username="vendedor",
        password_hash="1234", # Contraseña sencilla
        role="vendedor"       # Rol restringido
    )
    session.add(new_user)
    session.commit()
    print("✅ Usuario 'vendedor' creado con password '1234'")
    