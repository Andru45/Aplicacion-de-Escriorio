from datetime import datetime, timedelta
from src.pharmgest.config.database import SessionLocal, engine, Base
from src.pharmgest.database.models import Product, User, ProductBatch

def init_data():
    session = SessionLocal()
    
    # Reset rápido (si no borraste el archivo .db manual)
    # Nota: Mejor borrar el archivo pharmgest.db a mano antes de correr esto
    
    print("🌱 Sembrando datos con LOTES...")

    # 1. Admin
    admin = User(username="admin", role="admin", password_hash="secret123")
    vendedor = User(username="vendedor", role="vendedor", password_hash="1234")
    session.add(admin)
    session.add(vendedor)

    # 2. Producto: Ibuprofeno (Con 2 lotes)
    ibuprofeno = Product(
        sku="IBU-600",
        name="Ibuprofeno 600mg (Caja x 10)",
        price=250.00,
        total_stock=150 # Suma de los lotes abajo
    )
    session.add(ibuprofeno)
    session.flush() # Para obtener el ID

    # Lote 1: Bueno (Vence en 2026)
    lote_bueno = ProductBatch(
        product_id=ibuprofeno.id,
        batch_code="L-BUENO-001",
        stock=100,
        expiry_date=datetime.now() + timedelta(days=365) # 1 año futuro
    )
    
    # Lote 2: PELIGRO (Vence mañana)
    lote_casi_vencido = ProductBatch(
        product_id=ibuprofeno.id,
        batch_code="L-URGENTE-99",
        stock=50,
        expiry_date=datetime.now() + timedelta(days=1) # Mañana
    )

    session.add(lote_bueno)
    session.add(lote_casi_vencido)
    
    session.commit()
    print("✅ Base de datos lista con Lotes.")
    session.close()

if __name__ == "__main__":
    init_data()