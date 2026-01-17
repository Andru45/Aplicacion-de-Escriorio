import sys
from PyQt6.QtWidgets import QApplication, QDialog
from src.pharmgest.config.logging_config import logger
from src.pharmgest.ui.main_window import MainWindow
from src.pharmgest.ui.dialogs.login_dialog import LoginDialog

def main():
    logger.info("Iniciando aplicación PharmGest")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    try:
        login = LoginDialog()
        
        if login.exec() == QDialog.DialogCode.Accepted:
            # Recuperamos los datos del usuario logueado
            role = login.current_user_role
            username = login.current_user_name
            logger.info(f"Usuario autenticado: {username} ({role})")
            
            # Se los pasamos a la ventana principal
            window = MainWindow(user_role=role, user_name=username)
            window.showMaximized()
            sys.exit(app.exec())
        else:
            logger.info("Login cancelado por el usuario")
            sys.exit()
    except Exception as e:
        logger.critical(f"Error crítico al iniciar aplicación: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    