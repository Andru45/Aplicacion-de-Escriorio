from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QLabel, QHeaderView, QFrame, QDialog, QMessageBox)
from PyQt6.QtCore import Qt
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from src.pharmgest.config.database import SessionLocal, get_db_session
from src.pharmgest.config.logging_config import logger
from src.pharmgest.config.settings import PRICE_DECIMALS
from src.pharmgest.database.models import Sale, SaleDetail, Product

class SalesHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- 1. PANEL DE RESUMEN (KPIs) ---
        self.stats_layout = QHBoxLayout()
        
        # Tarjetas visuales
        self.card_total = self.create_stat_card("VENTA TOTAL", "$0.00", "#0078D7")   # Azul
        self.card_profit = self.create_stat_card("GANANCIA (Utilidad)", "$0.00", "#28a745") # Verde
        self.card_count = self.create_stat_card("TICKETS", "0", "#6c757d")           # Gris
        
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_profit)
        self.stats_layout.addWidget(self.card_count)
        
        layout.addLayout(self.stats_layout)

        # --- 2. TABLA DE HISTORIAL ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Fecha", "Productos (Resumen)", "Total Venta", "Ganancia Est."])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # No editable
        self.table.doubleClicked.connect(self.show_details) # Doble clic para ver detalle completo
        layout.addWidget(self.table)

        self.load_history()

    def create_stat_card(self, title, value, color):
        """Crea un cuadrito visual bonito para las estadísticas"""
        card = QFrame()
        card.setStyleSheet(f"background-color: {color}; border-radius: 8px; color: white;")
        card_layout = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 12px; font-weight: bold; opacity: 0.8;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 26px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        
        # Guardamos referencia al label del valor para actualizarlo luego
        card.value_label = lbl_value
        return card

    def load_history(self):
        try:
            with get_db_session() as session:
                # Optimización: Cargar ventas con detalles y productos en una sola consulta
                # Evita el problema N+1 de consultas
                sales = session.query(Sale)\
                    .options(joinedload(Sale.details).joinedload(SaleDetail.product))\
                    .order_by(Sale.date.desc())\
                    .all()
                
                self.table.setRowCount(0)
                total_ventas = 0
                total_ganancia = 0
                
                for row, sale in enumerate(sales):
                    self.table.insertRow(row)
                    
                    # Calcular ganancia de esta venta específica
                    ganancia_venta = 0
                    items_names = []
                    
                    for detail in sale.details:
                        # El producto ya está cargado gracias a joinedload
                        prod = detail.product
                        if prod:
                            # --- MEJORA VISUAL: Indicar si fue Caja o Unidad ---
                            tipo_venta = "Caja" if detail.is_box_sale else "Unid"
                            items_names.append(f"{prod.name} ({detail.quantity} {tipo_venta})")
                            
                            # --- CORRECCIÓN MATEMÁTICA CRÍTICA ---
                            costo_base = prod.cost if prod.cost else 0
                            
                            if detail.is_box_sale:
                                # Si es venta por CAJA, restamos el costo completo
                                costo_aplicable = costo_base
                            else:
                                # Si es venta por UNIDAD, dividimos el costo entre las unidades que trae la caja
                                if prod.is_fractionable and prod.units_per_box > 0:
                                    costo_aplicable = costo_base / prod.units_per_box
                                else:
                                    costo_aplicable = costo_base # Evitar división por cero si no está configurado
                            
                            # Cálculo: (Precio al que se vendió - Costo real proporcional) * Cantidad
                            utilidad = (detail.unit_price - costo_aplicable) * detail.quantity
                            
                            # Ajuste rápido: Si el costo es 0 (no configurado), marcamos ganancia 0 para alertar
                            if costo_base == 0:
                                utilidad = 0 
                            
                            ganancia_venta += utilidad

                    # Acumuladores globales
                    total_ventas += sale.total
                    total_ganancia += ganancia_venta
                    
                    # Llenar celdas
                    self.table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(sale.date.strftime("%d/%m %H:%M")))
                    self.table.setItem(row, 2, QTableWidgetItem(", ".join(items_names))) # Resumen rápido
                    self.table.setItem(row, 3, QTableWidgetItem(f"${sale.total:,.2f}"))
                    
                    # Columna Ganancia (Colorizada)
                    item_ganancia = QTableWidgetItem(f"${ganancia_venta:,.2f}")
                    if ganancia_venta > 0:
                        item_ganancia.setForeground(Qt.GlobalColor.darkGreen)
                    elif ganancia_venta < 0:
                        item_ganancia.setForeground(Qt.GlobalColor.red) # ROJO si hay pérdida real
                    else:
                        item_ganancia.setForeground(Qt.GlobalColor.gray) # Gris si es 0 (o falta costo)
                    self.table.setItem(row, 4, item_ganancia)

                # Actualizar Cards Superiores
                self.card_total.value_label.setText(f"${total_ventas:,.2f}")
                self.card_profit.value_label.setText(f"${total_ganancia:,.2f}")
                self.card_count.value_label.setText(str(len(sales)))
        except SQLAlchemyError as e:
            logger.error(f"Error al cargar historial de ventas: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", 
                               "Ocurrió un error al cargar el historial de ventas.")
        except Exception as e:
            logger.error(f"Error inesperado al cargar historial: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def show_details(self):
        """Muestra el detalle completo de una factura en un diálogo"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        try:
            sale_id = int(self.table.item(row, 0).text())
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error al obtener ID de venta: {e}")
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID de la venta seleccionada.")
            return
        
        try:
            with get_db_session() as session:
                sale = session.get(Sale, sale_id)
                
                if sale is None:
                    QMessageBox.warning(self, "Error", "Venta no encontrada.")
                    return
                
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Detalle Factura #{sale_id}")
                dialog.resize(500, 400)
                d_layout = QVBoxLayout(dialog)
                
                det_table = QTableWidget()
                det_table.setColumnCount(4)
                det_table.setHorizontalHeaderLabels(["Cant.", "Producto", "P. Unit", "Subtotal"])
                det_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
                
                det_table.setRowCount(0)
                for r, det in enumerate(sale.details):
                    det_table.insertRow(r)
                    det_table.setItem(r, 0, QTableWidgetItem(str(det.quantity)))
                    prod_name = det.product.name if det.product else "Producto Eliminado"
                    det_table.setItem(r, 1, QTableWidgetItem(prod_name))
                    det_table.setItem(r, 2, QTableWidgetItem(f"${det.unit_price:,.2f}"))
                    det_table.setItem(r, 3, QTableWidgetItem(f"${det.subtotal:,.2f}"))
                    
                d_layout.addWidget(det_table)
                d_layout.addWidget(QLabel(f"<b>TOTAL FACTURA: ${sale.total:,.2f}</b>"))
                
                dialog.exec()
        except SQLAlchemyError as e:
            logger.error(f"Error al cargar detalle de venta: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Base de Datos", 
                               "Ocurrió un error al cargar el detalle de la venta.")
        except Exception as e:
            logger.error(f"Error inesperado al mostrar detalles: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")