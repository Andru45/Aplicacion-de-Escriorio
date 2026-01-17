from src.pharmgest.config.database import Base, engine
from src.pharmgest.database.models import User, Product

print("🔨 Creando base de datos PharmGest...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ ¡ÉXITO! Base de datos 'pharmgest.db' creada correctamente.")
    print("🚀 Tablas creadas: Users, Products")
except Exception as e:
    print(f"❌ ERROR CRÍTICO: {e}")