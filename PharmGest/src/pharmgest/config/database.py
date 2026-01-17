from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

# URL de la base de datos
DB_URL = "sqlite:///./pharmgest.db"

# Motor de base de datos con configuración para GUI
engine = create_engine(
    DB_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Cambiado a False para producción, usar logging en su lugar
)

# Activar WAL Mode (Optimización crítica)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


@contextmanager
def get_db_session():
    """
    Context manager para sesiones de base de datos.
    Garantiza que la sesión se cierre correctamente incluso si hay errores.
    
    Uso:
        with get_db_session() as session:
            product = session.get(Product, product_id)
            # La sesión se cierra automáticamente al salir del bloque
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()