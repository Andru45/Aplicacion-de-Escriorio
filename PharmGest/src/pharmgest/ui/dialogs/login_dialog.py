from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.pharmgest.config.database import SessionLocal
from src.pharmgest.database.models import User

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acceso - PharmGest ERP")
        self.resize(350, 250)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)
        
        # Variable para guardar el rol y nombre
        self.current_user_role = None
        self.current_user_name = None
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        lbl_title = QLabel("Iniciar Sesión")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(lbl_title)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setStyleSheet("padding: 8px;")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("padding: 8px;")
        
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        
        btn_login = QPushButton("ENTRAR")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        btn_login.clicked.connect(self.check_login)
        layout.addWidget(btn_login)

    def check_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Ingresa usuario y contraseña")
            return
            
        session = SessionLocal()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        
        if user and user.password_hash == password:
            # GUARDAMOS QUIÉN ES ANTES DE CERRAR
            self.current_user_role = user.role
            self.current_user_name = user.username
            self.accept()
        else:
            QMessageBox.critical(self, "Acceso Denegado", "Usuario o contraseña incorrectos")