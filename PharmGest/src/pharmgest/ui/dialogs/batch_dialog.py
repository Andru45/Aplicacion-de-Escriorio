from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QPushButton, QHeaderView, 
                           QDateEdit, QLineEdit, QSpinBox, QMessageBox, QWidget,
                           QAbstractItemView, QGroupBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QIcon
from sqlalchemy.exc import SQLAlchemyError
from src.pharmgest.config.database import SessionLocal, get_db_session
from src.pharmgest.config.logging_config import logger
from src.pharmgest.config.settings import DIAS_VENCIMIENTO_ADVERTENCIA
from src.pharmgest.database.models import Product, ProductBatch

class BatchDialog(QDialog):
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Gestión de Lotes y Vencimientos")
        self.resize(800, 550)
        
        layout = QVBoxLayout(self)
        
        # --- INFO SUPERIOR ---
        self.lbl_info = QLabel("Cargando...")
        self.lbl_info.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #0078D7;")
        layout.addWidget(self.lbl_info)
        
        # --- FORMULARIO DE INGRESO ---
        # Usamos QGroupBox para que se vea ordenado y con título
        group_box = QGroupBox("➕ Agregar Nuevo Lote")
        group_box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        form_layout = QHBoxLayout(group_box)
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ej: L-2025-X")
        
        self.input_qty = QSpinBox()
        self.input_qty.setRange(1, 10000)
        self.lbl_qty_unit = QLabel("Cant:") 
        
        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(QDate.currentDate().addDays(365))
        
        btn_add = QPushButton("Guardar")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #28a745; 
                color: white; 
                font-weight: bold; 
                padding: 6px 15px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        btn_add.clicked.connect(self.add_batch)
        
        # Añadir widgets al layout horizontal
        form_layout.addWidget(QLabel("Código:"))
        form_layout.addWidget(self.input_code)
        form_layout.addWidget(QLabel("Vence:"))
        form_layout.addWidget(self.input_date)
        form_layout.addWidget(self.lbl_qty_unit)
        form_layout.addWidget(self.input_qty)
        form_layout.addWidget(btn_add)
        
        layout.addWidget(group_box)

        # --- TABLA DE LOTES ---
        self.table = QTableWidget()
        self.table.setColumnCount(6) # Aumentamos columnas para el botón borrar
        self.table.setHorizontalHeaderLabels(["ID", "Lote", "Vencimiento", "Stock Real", "Estado", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # BLOQUEAR EDICIÓN (SOLUCIÓN AL PROBLEMA 2)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        try:
            with get_db_session() as session:
                product = session.get(Product, self.product_id)
                
                if not product:
                    QMessageBox.warning(self, "Error", "Producto no encontrado")
                    self.close()
                    return
                
                # Actualizar info
                if product.is_fractionable:
                    self.lbl_qty_unit.setText(f"Cajas (x{product.units_per_box}):")
                    info_text = f"📦 {product.name} | Total: {product.stock_display}"
                else:
                    self.lbl_qty_unit.setText("Unidades:")
                    info_text = f"📦 {product.name} | Total: {product.total_stock}"
                    
                self.lbl_info.setText(info_text)
                
                # Cargar lotes
                batches = session.query(ProductBatch).filter_by(product_id=self.product_id)\
                    .order_by(ProductBatch.expiry_date).all()
                
                self.table.setRowCount(0)
                today = datetime.now().date()
                
                for row, batch in enumerate(batches):
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(str(batch.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(batch.batch_code))
                    
                    expiry = batch.expiry_date.date()
                    self.table.setItem(row, 2, QTableWidgetItem(expiry.strftime("%d/%m/%Y")))
                    self.table.setItem(row, 3, QTableWidgetItem(str(batch.stock)))
                    
                    # Semáforo
                    days_left = (expiry - today).days
                    status = QTableWidgetItem()
                    if days_left < 0:
                        status.setText("🚫 VENCIDO")
                        status.setBackground(QColor("#ffcccc")) # Rojo suave
                        status.setForeground(QColor("#000000")) # Texto negro
                    elif days_left < DIAS_VENCIMIENTO_ADVERTENCIA:
                        status.setText(f"⚠️ {days_left} días")
                        status.setBackground(QColor("#fff4cc")) # Amarillo suave
                        status.setForeground(QColor("#000000"))
                    else:
                        status.setText("✅ OK")
                        # Si usas tema oscuro, el texto blanco está bien por defecto
                    
                    self.table.setItem(row, 4, status)
                    
                    # BOTÓN BORRAR
                    btn_del = QPushButton("🗑️")
                    btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_del.setStyleSheet("border: none; background: transparent; font-size: 14px;")
                    btn_del.setToolTip("Eliminar Lote (Restará el stock)")
                    btn_del.clicked.connect(lambda _, b_id=batch.id: self.delete_batch(b_id))
                    self.table.setCellWidget(row, 5, btn_del)
        except SQLAlchemyError as e:
            logger.error(f"Error al cargar lotes: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", "Error al cargar los lotes.")
        except Exception as e:
            logger.error(f"Error inesperado al cargar lotes: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def add_batch(self):
        code = self.input_code.text()
        qty_input = self.input_qty.value()
        
        if not code:
            QMessageBox.warning(self, "Error", "Debes escribir un código de lote.")
            return

        expiry = self.input_date.date().toPyDate()
        expiry_dt = datetime(expiry.year, expiry.month, expiry.day)
        
        try:
            with get_db_session() as session:
                product = session.get(Product, self.product_id)
                
                if product is None:
                    QMessageBox.warning(self, "Error", "Producto no encontrado")
                    return
            
            # 1. Calcular cuánto stock real entra
            real_stock_to_add = qty_input
            if product.is_fractionable:
                real_stock_to_add = qty_input * product.units_per_box

                # 2. Crear el Lote
                new_batch = ProductBatch(
                    product_id=self.product_id,
                    batch_code=code,
                    stock=real_stock_to_add,
                    expiry_date=expiry_dt
                )
                session.add(new_batch)
                session.flush() # Para obtener el ID antes del commit
                
                # 3. RECALCULAR STOCK TOTAL DESDE CERO (Fuente de Verdad)
                # Esto corrige cualquier error matemático previo
                all_batches = session.query(ProductBatch).filter_by(product_id=self.product_id).all()
                total_real = sum(b.stock for b in all_batches)
                
                product.total_stock = total_real
                # El commit se hace automáticamente al salir del context manager
            
            # Limpiar y recargar
            self.input_code.clear()
            self.input_qty.setValue(1)
            self.load_data()
            
        except SQLAlchemyError as e:
            logger.error(f"Error de BD al agregar lote: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", "Error al agregar el lote.")
        except Exception as e:
            logger.error(f"Error inesperado al agregar lote: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def delete_batch(self, batch_id):
        confirm = QMessageBox.question(
            self, "Eliminar Lote", 
            "¿Eliminar este lote? Se recalculará el stock total.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                with get_db_session() as session:
                    batch = session.get(ProductBatch, batch_id)
                    if batch:
                        # 1. Borrar Lote
                        session.delete(batch)
                        session.flush()
                        
                        # 2. RECALCULAR STOCK TOTAL DESDE CERO
                        product = session.get(Product, self.product_id)
                        if product:
                            all_batches = session.query(ProductBatch).filter_by(product_id=self.product_id).all()
                            total_real = sum(b.stock for b in all_batches)
                            
                            product.total_stock = total_real
                            # El commit se hace automáticamente al salir del context manager
                    else:
                        QMessageBox.warning(self, "Error", "Lote no encontrado")
                        return
                
                self.load_data()
            except SQLAlchemyError as e:
                logger.error(f"Error de BD al eliminar lote: {e}", exc_info=True)
                QMessageBox.critical(self, "Error de Base de Datos", "Error al eliminar el lote.")
            except Exception as e:
                logger.error(f"Error inesperado al eliminar lote: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")