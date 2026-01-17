import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QPushButton, QLabel, 
                           QHeaderView, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from src.pharmgest.config.database import SessionLocal
from src.pharmgest.database.models import Product, Sale, SaleDetail, ProductBatch
from src.pharmgest.services.invoice import generate_invoice_pdf

class POSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = [] 
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # --- IZQUIERDA: BUSCADOR ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        lbl_search = QLabel("🔍 Buscar Producto (Nombre o SKU):")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escribe y presiona Enter...")
        self.search_input.returnPressed.connect(self.search_product)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["ID", "Producto", "Precio", "Stock Global"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.setColumnHidden(0, True)
        self.results_table.doubleClicked.connect(self.add_to_cart)
        
        left_layout.addWidget(lbl_search)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.results_table)
        
        # --- DERECHA: CARRITO ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_cart = QLabel("🛒 Ticket de Venta")
        lbl_cart.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5) 
        self.cart_table.setHorizontalHeaderLabels(["Cant.", "Producto", "P.Unit", "Total", "X"])
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.lbl_total = QLabel("TOTAL: $0.00")
        self.lbl_total.setStyleSheet("font-size: 30px; font-weight: bold; color: #28a745; margin: 10px;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        btn_pay = QPushButton("💸 COBRAR / PAGAR")
        btn_pay.setStyleSheet("background-color: #0078D7; color: white; padding: 15px; font-size: 16px; font-weight: bold;")
        btn_pay.clicked.connect(self.process_sale)
        
        right_layout.addWidget(lbl_cart)
        right_layout.addWidget(self.cart_table)
        right_layout.addWidget(self.lbl_total)
        right_layout.addWidget(btn_pay)

        main_layout.addWidget(left_panel, 6)
        main_layout.addWidget(right_panel, 4)
        
        self.search_product()

    def search_product(self):
        query_text = self.search_input.text()
        session = SessionLocal()
        query = session.query(Product)
        if query_text:
            query = query.filter(Product.name.ilike(f"%{query_text}%") | Product.sku.ilike(f"%{query_text}%"))
        products = query.all()
        
        self.results_table.setRowCount(0)
        for row, p in enumerate(products):
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.results_table.setItem(row, 1, QTableWidgetItem(p.name))
            
            if p.is_fractionable:
                price_str = f"${p.unit_price} u / ${p.box_price} c"
            else:
                price_str = f"${p.price}"
            self.results_table.setItem(row, 2, QTableWidgetItem(price_str))
            
            # FIX 1: Mostrar siempre el stock global real
            self.results_table.setItem(row, 3, QTableWidgetItem(str(p.total_stock)))
            
        session.close()

    def add_to_cart(self):
        row = self.results_table.currentRow()
        if row < 0: return
        
        product_id = int(self.results_table.item(row, 0).text())
        session = SessionLocal()
        product = session.query(Product).get(product_id)
        
        is_box_mode = True 
        final_price = product.price
        
        # FIX 2: Verificar si es fraccionable y mostrar diálogo de elección
        if product.is_fractionable:
            items = ["📦 Vender CAJA Completa", "💊 Vender UNIDAD Suelta"]
            item, ok = QInputDialog.getItem(self, "Modo de Venta", 
                f"Producto: {product.name}\nStock Total: {product.total_stock}", 
                items, 0, False)
            
            if not ok: 
                session.close()
                return
            
            if "UNIDAD" in item:
                is_box_mode = False
                final_price = product.unit_price
            else:
                final_price = product.box_price

        # Calcular Stock Máximo
        if is_box_mode:
            if product.is_fractionable and product.units_per_box > 0:
                max_stock = product.total_stock // product.units_per_box
            else:
                max_stock = product.total_stock # Si no es fraccionable, se asume que el stock total es de cajas
        else:
            max_stock = product.total_stock # Venta por unidad

        # Diálogo de cantidad con texto dinámico
        label_unit = "Cajas" if is_box_mode else "Unidades"
        qty, ok = QInputDialog.getInt(self, "Cantidad", f"¿Cuántas {label_unit}?", 1, 1, max_stock)
        
        if ok:
            subtotal = final_price * qty
            units_to_deduct = qty
            if is_box_mode and product.is_fractionable:
                units_to_deduct = qty * product.units_per_box
            
            self.cart.append({
                "id": product.id,
                "name": f"{product.name} ({'CAJA' if is_box_mode else 'UNIDAD'})",
                "price": final_price,
                "qty": qty,
                "units_to_deduct": units_to_deduct,
                "subtotal": subtotal,
                "is_box_sale": is_box_mode
            })
            self.update_cart_ui()
            
        session.close()

    def remove_from_cart(self, index):
        self.cart.pop(index)
        self.update_cart_ui()

    def update_cart_ui(self):
        self.cart_table.setRowCount(0)
        total_global = 0
        for row, item in enumerate(self.cart):
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"${item['price']:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"${item['subtotal']:.2f}"))
            
            btn_rem = QPushButton("❌")
            btn_rem.setStyleSheet("color: red; font-weight: bold;")
            btn_rem.clicked.connect(lambda _, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, btn_rem)
            total_global += item["subtotal"]
        self.lbl_total.setText(f"TOTAL: ${total_global:.2f}")

    def process_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Carrito Vacío", "No hay productos.")
            return
            
        # 1. Calcular Total
        total = sum(item["subtotal"] for item in self.cart)
        
        # 2. Calculadora de Cambio
        amount_paid, ok = QInputDialog.getDouble(self, "Cobro", 
                                               f"Total a Pagar: ${total:,.2f}\n\n¿Con cuánto paga el cliente?", 
                                               value=total, minValue=0, maxValue=1000000, decimals=2)
        if not ok:
            return 
            
        if amount_paid < total:
            QMessageBox.warning(self, "Pago Insuficiente", f"Faltan ${total - amount_paid:,.2f} para completar el pago.")
            return
            
        change = amount_paid - total
        
        print("--- INICIANDO PROCESO DE VENTA ---") # Debug

        session = SessionLocal()
        try:
            print("1. Creando venta...")
            new_sale = Sale(total=total)
            session.add(new_sale)
            session.flush()
            
            print("2. Procesando productos...")
            for item in self.cart:
                product = session.query(Product).get(item["id"])
                qty_needed = item["units_to_deduct"]
                
                if product.total_stock < qty_needed:
                    raise Exception(f"Stock insuficiente para {product.name}. (Tienes {product.total_stock}, pides {qty_needed})")
                
                product.total_stock -= qty_needed
                
                # Algoritmo FEFO
                batches = session.query(ProductBatch).filter(
                    ProductBatch.product_id == product.id,
                    ProductBatch.stock > 0
                ).order_by(ProductBatch.expiry_date).all()
                
                remaining_to_deduct = qty_needed
                for batch in batches:
                    if remaining_to_deduct <= 0: break
                    if batch.stock >= remaining_to_deduct:
                        batch.stock -= remaining_to_deduct
                        remaining_to_deduct = 0
                    else:
                        remaining_to_deduct -= batch.stock
                        batch.stock = 0
                
                # Crear detalle (Asegúrate que tu BD tenga la columna is_box_sale)
                detail = SaleDetail(
                    sale_id=new_sale.id, 
                    product_id=product.id,
                    quantity=item["qty"], 
                    unit_price=item["price"],
                    subtotal=item["subtotal"],
                    is_box_sale=item["is_box_sale"]
                )
                session.add(detail)
            
            print("3. Guardando en Base de Datos (Commit)...")
            session.commit()
            print("✅ Venta Guardada Exitosamente.")
            
            # Generar PDF
            print("4. Generando PDF...")
            pdf_path = generate_invoice_pdf(new_sale.id, self.cart, total)
            
            # Mensaje de Éxito
            msg = (f"✅ Venta #{new_sale.id} registrada.\n\n"
                   f"💰 Recibido: ${amount_paid:,.2f}\n"
                   f"💵 SU CAMBIO: ${change:,.2f}\n\n"
                   f"¿Ver Factura?")
                   
            reply = QMessageBox.question(self, "Venta Exitosa", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                print(f"5. Intentando abrir PDF: {pdf_path}")
                try:
                    os.startfile(os.path.abspath(pdf_path))
                except Exception as e_pdf:
                    print(f"⚠️ Error al abrir PDF: {e_pdf}")
                    QMessageBox.warning(self, "Aviso", f"La venta se hizo, pero no se pudo abrir el PDF automáticamente.\nError: {e_pdf}")

            # Limpieza
            self.cart = []
            self.update_cart_ui()
            self.search_product()
            
        except Exception as e:
            session.rollback()
            print(f"❌ ERROR CRÍTICO: {str(e)}")
            # Si el error es de columnas faltantes, damos una pista clara
            if "no column" in str(e) or "no such table" in str(e):
                QMessageBox.critical(self, "Error de Base de Datos", 
                    f"Tu base de datos está desactualizada.\n\nSOLUCIÓN: Borra el archivo 'pharmgest.db' y reinicia el programa.\n\nDetalle: {e}")
            else:
                QMessageBox.critical(self, "Error en Venta", f"Ocurrió un error:\n{str(e)}")
        finally:
            session.close()