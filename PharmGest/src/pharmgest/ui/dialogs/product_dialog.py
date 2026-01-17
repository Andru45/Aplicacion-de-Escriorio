from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QDoubleSpinBox, QSpinBox, 
                           QDialogButtonBox, QMessageBox, QCheckBox, QGroupBox, QLabel)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.pharmgest.config.database import SessionLocal, get_db_session
from src.pharmgest.config.logging_config import logger
from src.pharmgest.database.models import Product

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles del Producto")
        self.resize(500, 550)
        self.product_id = product_id 
        
        layout = QVBoxLayout(self)
        
        # --- DATOS BÁSICOS ---
        group_basic = QGroupBox("Información General")
        form_basic = QFormLayout()
        
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Código único (Ej: 750123...)")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre comercial")
        
        # Precio Venta
        self.price_input = QDoubleSpinBox()
        self.price_input.setPrefix("$ ")
        self.price_input.setMaximum(999999.99)
        
        # COSTO (Sin color amarillo, estilo estándar)
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setPrefix("$ ")
        self.cost_input.setMaximum(999999.99)
        self.cost_input.setToolTip("Costo de compra al proveedor")
        
        # Stock Manual
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)
        # Etiqueta dinámica que guardaremos para cambiar el texto luego
        self.lbl_stock = QLabel("Stock Total:") 
        
        form_basic.addRow("SKU / Código:", self.sku_input)
        form_basic.addRow("Nombre:", self.name_input)
        form_basic.addRow("Precio Venta (Público):", self.price_input)
        form_basic.addRow("Costo Compra (Interno):", self.cost_input)
        form_basic.addRow(self.lbl_stock, self.stock_input)
        
        group_basic.setLayout(form_basic)
        layout.addWidget(group_basic)
        
        # --- CONFIGURACIÓN FRACCIONADA ---
        group_fraction = QGroupBox("Configuración de Venta")
        form_fraction = QFormLayout()
        
        self.chk_fractionable = QCheckBox("¿Permitir venta fraccionada (Pastillas)?")
        self.chk_fractionable.toggled.connect(self.toggle_fraction_fields)
        
        self.spin_units_box = QSpinBox()
        self.spin_units_box.setRange(1, 1000)
        self.spin_units_box.setValue(1)
        self.spin_units_box.setSuffix(" unidades por caja")
        
        self.spin_box_price = QDoubleSpinBox()
        self.spin_box_price.setPrefix("$ ")
        self.spin_box_price.setMaximum(999999.99)
        
        self.spin_unit_price = QDoubleSpinBox()
        self.spin_unit_price.setPrefix("$ ")
        self.spin_unit_price.setMaximum(999999.99)
        
        form_fraction.addRow(self.chk_fractionable)
        form_fraction.addRow("Unidades por Caja:", self.spin_units_box)
        form_fraction.addRow("Precio CAJA:", self.spin_box_price)
        form_fraction.addRow("Precio UNIDAD:", self.spin_unit_price)
        
        group_fraction.setLayout(form_fraction)
        layout.addWidget(group_fraction)
        
        self.toggle_fraction_fields(False)
        
        # --- BOTONES ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_product)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self.product_id:
            self.load_product_data()

    def toggle_fraction_fields(self, checked):
        self.spin_units_box.setEnabled(checked)
        self.spin_box_price.setEnabled(checked)
        self.spin_unit_price.setEnabled(checked)
        
        # CAMBIO VISUAL CLAVE: Explicar qué es el stock
        if checked:
            self.lbl_stock.setText("Stock Total (En PASTILLAS):")
            self.stock_input.setSuffix(" Unidades")
            # Tip: Si quieres poner 5 cajas, escribe 50
        else:
            self.lbl_stock.setText("Stock Total:")
            self.stock_input.setSuffix(" Unidades Globales")

    def load_product_data(self):
        try:
            with get_db_session() as session:
                product = session.get(Product, self.product_id)
                if product:
                    self.sku_input.setText(product.sku)
                    self.name_input.setText(product.name)
                    self.price_input.setValue(product.price)
                    self.cost_input.setValue(product.cost if product.cost else 0.0)
                    self.stock_input.setValue(product.total_stock)
                    
                    # Al cargar, activamos/desactivamos y cambiamos el texto
                    self.chk_fractionable.setChecked(product.is_fractionable)
                    self.toggle_fraction_fields(product.is_fractionable)
                    
                    self.spin_units_box.setValue(product.units_per_box)
                    self.spin_box_price.setValue(product.box_price)
                    self.spin_unit_price.setValue(product.unit_price)
                    
                    self.setWindowTitle(f"Editar: {product.name}")
                else:
                    QMessageBox.warning(self, "Error", "Producto no encontrado")
                    self.reject()
        except SQLAlchemyError as e:
            logger.error(f"Error al cargar producto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", "Error al cargar los datos del producto.")
            self.reject()
        except Exception as e:
            logger.error(f"Error inesperado al cargar producto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            self.reject()

    def save_product(self):
        # ... (El método save_product queda IGUAL que antes) ...
        sku = self.sku_input.text()
        name = self.name_input.text()
        price = self.price_input.value()
        cost = self.cost_input.value()
        stock = self.stock_input.value()
        
        is_frac = self.chk_fractionable.isChecked()
        units_box = self.spin_units_box.value()
        box_price = self.spin_box_price.value()
        unit_price = self.spin_unit_price.value()
        
        if not sku or not name:
            QMessageBox.warning(self, "Error", "El SKU y Nombre son obligatorios")
            return

        try:
            with get_db_session() as session:
                if self.product_id:
                    product = session.get(Product, self.product_id)
                    if product is None:
                        QMessageBox.warning(self, "Error", "Producto no encontrado")
                        return
                    
                    product.sku = sku
                    product.name = name
                    product.price = price
                    product.cost = cost
                    product.total_stock = stock
                    
                    product.is_fractionable = is_frac
                    product.units_per_box = units_box
                    product.box_price = box_price
                    product.unit_price = unit_price
                    
                    if is_frac and units_box > 0:
                        product.stock = stock // units_box
                    else:
                        product.stock = stock
                else:
                    new_product = Product(
                        sku=sku, name=name, price=price, cost=cost,
                        total_stock=stock,
                        is_fractionable=is_frac, units_per_box=units_box,
                        box_price=box_price, unit_price=unit_price,
                        stock=stock if not is_frac else stock // units_box
                    )
                    session.add(new_product)
                # El commit se hace automáticamente al salir del context manager
            self.accept()
        except IntegrityError as e:
            logger.error(f"Error de integridad al guardar producto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", 
                               "El SKU ya existe. Por favor, use un código único.")
        except SQLAlchemyError as e:
            logger.error(f"Error de BD al guardar producto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", "Error al guardar el producto.")
        except Exception as e:
            logger.error(f"Error inesperado al guardar producto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")