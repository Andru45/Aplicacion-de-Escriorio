from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, 
                           QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.pharmgest.config.database import SessionLocal, get_db_session
from src.pharmgest.config.settings import STOCK_CRITICO, STOCK_BAJO, COLOR_STOCK_CRITICO, COLOR_STOCK_BAJO, COLOR_TEXT
from src.pharmgest.database.models import Product
from src.pharmgest.ui.pos_widget import POSWidget
from src.pharmgest.ui.sales_history import SalesHistoryWidget
from src.pharmgest.ui.dialogs.product_dialog import ProductDialog
from src.pharmgest.ui.dialogs.batch_dialog import BatchDialog

# --- WIDGET DE INVENTARIO MEJORADO ---
class InventoryWidget(QWidget):
    def __init__(self, user_role="vendedor"):
        super().__init__()
        self.user_role = user_role
        layout = QVBoxLayout(self)
        
        # --- HEADER (Buscador y Botones) ---
        header = QHBoxLayout()
        header.addWidget(QLabel("📦 Gestión de Inventario"))
        
        # BOTÓN DE REFRESCO MANUAL (¡NUEVO!) 🔄
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setToolTip("Recargar datos de la base de datos")
        btn_refresh.setStyleSheet("padding: 5px 10px;")
        btn_refresh.clicked.connect(self.load_data)
        header.addWidget(btn_refresh)
        
        header.addStretch()
        
        # SOLO ADMIN PUEDE CREAR PRODUCTOS
        if self.user_role == "admin":
            btn_add = QPushButton("➕ Nuevo Producto")
            btn_add.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 6px;")
            btn_add.clicked.connect(lambda: self.open_product_dialog())
            header.addWidget(btn_add)
            
        layout.addLayout(header)
        
        # --- TABLA ---
        self.table = QTableWidget()
        cols = 5 if self.user_role == "admin" else 4
        self.table.setColumnCount(cols)
        
        headers = ["ID", "SKU", "Producto", "Precio / Stock"]
        if self.user_role == "admin":
            headers.append("Acciones")
            
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        """Lee la BD y rellena la tabla con SEMÁFORO DE STOCK"""
        with get_db_session() as session:
            products = session.query(Product).all()
            self.table.setRowCount(0)
            
            for row, p in enumerate(products):
            self.table.insertRow(row)
            
            # Definimos items
            item_id = QTableWidgetItem(str(p.id))
            item_sku = QTableWidgetItem(p.sku)
            item_name = QTableWidgetItem(p.name)
            
            # Stock Inteligente
            stock_text = getattr(p, "stock_display", str(p.total_stock))
            item_stock = QTableWidgetItem(f"${p.price:.2f} | Stock: {stock_text}")
            
            # --- LÓGICA DEL SEMÁFORO 🚦 ---
            # Color de fondo por defecto (transparente/tema)
            bg_color = None
            text_color = None
            
            if p.total_stock <= STOCK_CRITICO:
                # ROJO SUAVE (Crítico)
                bg_color = QColor(COLOR_STOCK_CRITICO)
                text_color = QColor(COLOR_TEXT)
            elif p.total_stock <= STOCK_BAJO:
                # AMARILLO SUAVE (Advertencia)
                bg_color = QColor(COLOR_STOCK_BAJO)
                text_color = QColor(COLOR_TEXT)
            
            # Aplicar colores a todas las celdas de la fila
            items = [item_id, item_sku, item_name, item_stock]
            for item in items:
                if bg_color:
                    item.setBackground(bg_color)
                if text_color:
                    item.setForeground(text_color)
            
            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, item_sku)
            self.table.setItem(row, 2, item_name)
            self.table.setItem(row, 3, item_stock)
            
            # Botones de Acción (Admin) - Se mantienen igual
            if self.user_role == "admin":
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                
                # Re-creamos los botones igual que antes...
                btn_batch = QPushButton("📅")
                btn_batch.setStyleSheet("background-color: #6c757d; color: white;")
                btn_batch.setToolTip("Lotes / Vencimiento")
                btn_batch.clicked.connect(lambda _, pid=p.id: self.open_batch_dialog(pid))
                
                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Editar Producto")
                btn_edit.clicked.connect(lambda _, pid=p.id: self.open_product_dialog(pid))
                
                btn_del = QPushButton("🗑️")
                btn_del.setStyleSheet("color: red;")
                btn_del.setToolTip("Borrar Producto")
                btn_del.clicked.connect(lambda _, pid=p.id: self.delete_product(pid))
                
                actions_layout.addWidget(btn_batch)
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_del)
                self.table.setCellWidget(row, 4, actions_widget)

    def open_batch_dialog(self, product_id):
        dialog = BatchDialog(self, product_id)
        dialog.exec() 
        # --- LA MAGIA ESTÁ AQUÍ ---
        # Antes teníamos "if dialog.exec():", lo que significaba "solo si le das Aceptar".
        # Ahora llamamos a load_data() SIEMPRE que se cierre la ventana, 
        # sin importar si usaste la X o Guardar.
        self.load_data() 

    def open_product_dialog(self, product_id=None):
        dialog = ProductDialog(self, product_id)
        if dialog.exec(): 
            self.load_data()

    def delete_product(self, pid):
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar producto?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                with get_db_session() as session:
                    product = session.get(Product, pid)
                    if product:
                        session.delete(product)
                    else:
                        QMessageBox.warning(self, "Error", "Producto no encontrado")
                        return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar producto: {str(e)}")
                return
            self.load_data()
            
# --- CLASE PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self, user_role="vendedor", user_name="Usuario"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle(f"PharmGest ERP - Usuario: {user_name} ({user_role.upper()})")
        self.resize(1200, 700)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 1. POS
        self.pos_widget = POSWidget()
        self.tabs.addTab(self.pos_widget, "💰 Punto de Venta")
        
        # 2. INVENTARIO (Aquí es donde fallaba antes)
        self.inventory_widget = InventoryWidget(user_role=self.user_role)
        self.tabs.addTab(self.inventory_widget, "📦 Inventario")
        
        # 3. HISTORIAL (SOLO ADMIN)
        if self.user_role == "admin":
            self.history_widget = SalesHistoryWidget()
            self.tabs.addTab(self.history_widget, "📊 Historial de Ventas")
        
        self.tabs.currentChanged.connect(self.refresh_tabs)

    def refresh_tabs(self, index):
        current_widget = self.tabs.currentWidget()
        if current_widget == self.pos_widget:
            self.pos_widget.search_product()
        elif current_widget == self.inventory_widget:
            self.inventory_widget.load_data()
        elif hasattr(self, 'history_widget') and current_widget == self.history_widget:
            self.history_widget.load_history()