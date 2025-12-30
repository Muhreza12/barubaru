# main_cyberpunk.py — Launcher untuk Crypto Insight dengan Cyberpunk UI
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer

class CyberpunkSplashScreen(QtWidgets.QWidget):
    """Cyberpunk-themed splash screen dengan animasi loading"""
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(500, 650)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.main_frame = QtWidgets.QFrame(self)
        self.main_frame.setObjectName("mainFrame")
        
        layout = QtWidgets.QVBoxLayout(self.main_frame)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setSpacing(30)

        # Neon logo
        logo_container = QtWidgets.QWidget()
        logo_layout = QtWidgets.QVBoxLayout(logo_container)
        logo_layout.setAlignment(QtCore.Qt.AlignCenter)
        logo_layout.setSpacing(10)
        
        logo_symbol = QtWidgets.QLabel("◢◣")
        logo_symbol.setObjectName("logoSymbol")
        logo_symbol.setAlignment(QtCore.Qt.AlignCenter)
        
        logo_text = QtWidgets.QLabel("CRYPTO INSIGHT")
        logo_text.setObjectName("logoText")
        logo_text.setAlignment(QtCore.Qt.AlignCenter)
        
        logo_layout.addWidget(logo_symbol)
        logo_layout.addWidget(logo_text)

        # Title
        self.title = QtWidgets.QLabel("INITIALIZING\nSYSTEM")
        self.title.setObjectName("titleText")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setWordWrap(True)
        
        # Subtitle
        self.subtitle = QtWidgets.QLabel("CYBERPUNK EDITION")
        self.subtitle.setObjectName("subtitleText")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)

        # Loading bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        # Loading text
        self.loading_label = QtWidgets.QLabel("LOADING")
        self.loading_label.setObjectName("loadingText")
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # System info
        self.system_info = QtWidgets.QLabel(
            "◢ NEURAL LINK ESTABLISHED\n"
            "◣ QUANTUM ENCRYPTION ACTIVE\n"
            "◢ BLOCKCHAIN SYNCING..."
        )
        self.system_info.setObjectName("systemInfo")
        self.system_info.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(logo_container)
        layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.system_info)

        self.window_layout = QtWidgets.QVBoxLayout(self)
        self.window_layout.addWidget(self.main_frame)
        
        self.setStyleSheet("""
            #mainFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 10, 15, 0.98),
                    stop:0.5 rgba(30, 10, 40, 0.98),
                    stop:1 rgba(10, 10, 15, 0.98)
                );
                border: 3px solid #ff00ff;
                border-radius: 0;
                box-shadow: 0 0 40px rgba(255, 0, 255, 0.6),
                           inset 0 0 60px rgba(0, 255, 255, 0.2);
            }
            #logoSymbol {
                font-size: 64px;
                font-weight: 900;
                color: #ff00ff;
                text-shadow: 0 0 20px #ff00ff,
                            0 0 40px #ff00ff,
                            0 0 60px #ff00ff;
            }
            #logoText {
                color: #00ffff;
                font-size: 28px;
                font-weight: 900;
                letter-spacing: 8px;
                text-shadow: 0 0 15px #00ffff,
                            0 0 30px #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #titleText {
                color: #00ffff;
                font-size: 42px;
                font-weight: 900;
                line-height: 48px;
                letter-spacing: 6px;
                text-shadow: 0 0 10px #00ffff,
                            0 0 20px #00ffff,
                            0 0 30px #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #subtitleText {
                color: #ff00ff;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 4px;
                margin-top: 10px;
                text-shadow: 0 0 10px #ff00ff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #progressBar {
                background: rgba(0, 0, 0, 0.5);
                border: 2px solid #00ffff;
                border-radius: 0;
                height: 20px;
                text-align: center;
            }
            #progressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 0, 255, 0.8),
                    stop:0.5 rgba(0, 255, 255, 0.8),
                    stop:1 rgba(255, 0, 255, 0.8));
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
            }
            #loadingText {
                color: #00ffff;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 3px;
                margin-top: 10px;
                text-shadow: 0 0 10px #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #systemInfo {
                color: #ff00ff;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                margin-top: 20px;
                text-shadow: 0 0 5px #ff00ff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        
        # Dots animation
        self.dots = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self._update_loading)
        self.loading_timer.start(400)
        
        # Progress animation
        self.progress_value = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(30)
    
    def _update_loading(self):
        """Update loading animation"""
        self.dots = (self.dots + 1) % 4
        dots_text = "." * self.dots
        self.loading_label.setText(f"LOADING{dots_text}")
    
    def _update_progress(self):
        """Update progress bar"""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.progress_timer.stop()

def main():
    """Launch Cyberpunk Auth UI"""
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Set cyberpunk font
    app.setFont(QtGui.QFont("Consolas", 10, QtGui.QFont.Bold))
    
    try:
        # Import Cyberpunk Auth Window
        from auth_ui_cyberpunk import CyberpunkAuthWindow
        
        # Create splash screen
        splash = CyberpunkSplashScreen()
        
        # Center on screen
        screen_geo = QtWidgets.QApplication.desktop().screenGeometry()
        center_pos = screen_geo.center() - splash.rect().center()
        splash.move(center_pos)
        
        # Show splash
        splash.show()
        
        # Create main window
        main_window = CyberpunkAuthWindow()
        
        # Function to switch windows
        def show_main_window():
            splash.loading_timer.stop()
            splash.progress_timer.stop()
            splash.close()
            
            # Center main window
            screen_geo = QtWidgets.QApplication.desktop().screenGeometry()
            center_pos = screen_geo.center() - main_window.rect().center()
            main_window.move(center_pos)
            
            main_window.show()

        # Switch after 3 seconds
        QTimer.singleShot(3000, show_main_window)
        
        sys.exit(app.exec_())
        
    except ImportError as e:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Import Error")
        msg.setText(f"Failed to import required modules:\n\n{str(e)}\n\n"
                   "Required files:\n"
                   "- auth_ui_cyberpunk.py\n"
                   "- app_db_fixed.py\n"
                   "- modern_notification.py\n"
                   "- dashboard_ui.py\n"
                   "- user_dashboard.py")
        msg.exec_()
        sys.exit(1)
        
    except Exception as e:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(f"An error occurred:\n\n{str(e)}")
        msg.exec_()
        sys.exit(1)

if __name__ == "__main__":
    main()
