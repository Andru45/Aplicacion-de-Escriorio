from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.pharmgest.config.database import Base

# --- USUARIOS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="vendedor") 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

# --- CATEGORÍAS ---
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="category")

# --- PRODUCTOS (Actualizado para Venta Fraccionada) ---
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # Precios
    price = Column(Float, nullable=False) # Mantenemos este por compatibilidad
    box_price = Column(Float, default=0.0) # Precio Caja
    unit_price = Column(Float, default=0.0) # Precio Unidad suelta
    cost = Column(Float, default=0.0)
    
    # Stock y Fraccionamiento
    stock = Column(Integer, default=0) # Mantenemos por compatibilidad (stock visual cajas)
    stock_units = Column(Integer, default=0) # EL STOCK REAL (Total pastillas)
    
    is_fractionable = Column(Boolean, default=False)
    units_per_box = Column(Integer, default=1)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")

    @property
    def stock_display(self):
        """Muestra el stock de forma inteligente (Cajas + Unidades)"""
        if not self.is_fractionable or self.units_per_box <= 1:
            return f"{self.stock_units} Unidades"
        
        boxes = self.stock_units // self.units_per_box
        loose = self.stock_units % self.units_per_box
        
        if loose == 0:
            return f"{boxes} Cajas"
        return f"{boxes} Cajas / {loose} Unid."

# --- VENTAS ---
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    total = Column(Float, default=0.0)
    payment_method = Column(String, default="EFECTIVO")
    
    details = relationship("SaleDetail", back_populates="sale", cascade="all, delete-orphan")

class SaleDetail(Base):
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    sale = relationship("Sale", back_populates="details")
    product = relationship("Product")