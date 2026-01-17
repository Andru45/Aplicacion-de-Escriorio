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

# --- PRODUCTOS ---
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    
    # Precios
    price = Column(Float, nullable=False) 
    box_price = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)

    # Stock Global (Suma de lotes o manual)
    total_stock = Column(Integer, default=0)
    
    # Campos Fraccionados (Legacy/Compatibilidad)
    is_fractionable = Column(Boolean, default=False)
    units_per_box = Column(Integer, default=1)
    stock = Column(Integer, default=0) # Stock visual cajas
    stock_units = Column(Integer, default=0) # Stock real unidades

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # RELACIÓN CON LOTES (¡ESTO ES LO QUE TE FALTABA!)
    batches = relationship("ProductBatch", back_populates="product", cascade="all, delete-orphan")

    @property
    def stock_display(self):
        """Texto bonito para mostrar stock"""
        if not self.is_fractionable or self.units_per_box <= 1:
            return f"{self.total_stock} Unid."
        
        cajas = self.total_stock // self.units_per_box
        sueltas = self.total_stock % self.units_per_box
        return f"{cajas} Cajas / {sueltas} Sueltas"

# --- NUEVA TABLA: LOTES (BATCHES) ---
class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    
    batch_code = Column(String, nullable=False) # El código impreso en la caja (L-2024)
    stock = Column(Integer, default=0)          # Cuántas hay de ESTE lote específico
    expiry_date = Column(DateTime, nullable=False) # Fecha de vencimiento
    
    entry_date = Column(DateTime, default=datetime.now) # Cuándo lo compramos
    
    product = relationship("Product", back_populates="batches")

# --- VENTAS ---
class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    total = Column(Float, default=0.0)
    payment_method = Column(String, default="EFECTIVO")
    ncf = Column(String, nullable=True) 
    details = relationship("SaleDetail", back_populates="sale", cascade="all, delete-orphan")

class SaleDetail(Base):
    __tablename__ = "sale_details"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    is_box_sale = Column(Boolean, default=True) 
    
    sale = relationship("Sale", back_populates="details")
    product = relationship("Product")