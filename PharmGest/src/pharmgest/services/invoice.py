import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def generate_invoice_pdf(sale_id, items, total, user_name="Admin"):
    # 1. Crear carpeta de facturas si no existe
    if not os.path.exists("facturas"):
        os.makedirs("facturas")
    
    filename = f"facturas/factura_{sale_id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # --- ENCABEZADO ---
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "FARMACIA PHARMGEST")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "Av. Principal #123, Ciudad")
    c.drawString(50, height - 85, "RNC: 1-23-45678-9")
    c.drawString(50, height - 100, f"Tel: (809) 555-0101")
    
    # Datos de la Venta
    c.drawString(400, height - 70, f"NO. FACTURA: {sale_id:06d}")
    c.drawString(400, height - 85, f"FECHA: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawString(400, height - 100, f"CAJERO: {user_name}")

    # --- LÍNEA SEPARADORA ---
    c.line(50, height - 120, 550, height - 120)

    # --- TABLA DE PRODUCTOS ---
    y = height - 150
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "CANT")
    c.drawString(100, y, "DESCRIPCIÓN")
    c.drawString(350, y, "PRECIO")
    c.drawString(450, y, "TOTAL")
    
    y -= 20
    c.setFont("Helvetica", 10)
    
    for item in items:
        # Item es un diccionario: {'qty', 'name', 'price', 'subtotal'}
        c.drawString(50, y, str(item['qty']))
        c.drawString(100, y, item['name'][:40]) # Cortar nombre si es muy largo
        c.drawString(350, y, f"${item['price']:,.2f}")
        c.drawString(450, y, f"${item['subtotal']:,.2f}")
        y -= 20
        
        # Si la factura es muy larga, crear nueva página (simplificado)
        if y < 100:
            c.showPage()
            y = height - 50

    # --- TOTALES ---
    c.line(50, y, 550, y)
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(350, y, "TOTAL A PAGAR:")
    c.drawString(460, y, f"${total:,.2f}")
    
    # Pie de página
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, "¡Gracias por su compra! - Sistema PharmGest ERP")
    
    c.save()
    return filename