from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ModernNotification(QWidget):
    def __init__(self, parent, title, message, notif_type="info"):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.title = title
        self.message = message
        self.notif_type = notif_type
        
        self.setup_ui()
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        
        if self.notif_type == "success":
            icon = "✓"
            color = "#00ff88"
        elif self.notif_type == "error":
            icon = "✕"
            color = "#ff4444"
        elif self.notif_type == "warning":
            icon = "⚠"
            color = "#ffaa00"
        else:
            icon = "ℹ"
            color = "#00ffff"
        
        icon_label.setText(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 16px;
            }}
        """)
        
        # Text
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }}
        """)
        
        message_label = QLabel(self.message)
        message_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }
        """)
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(300)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_widget, 1)
        
        self.setStyleSheet(f"""
            QWidget {{
                background: rgba(10, 10, 15, 0.95);
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)
        
        # FIX: Set fixed size to avoid geometry issues
        self.setFixedWidth(350)
        self.setFixedHeight(80)
    
    def show_notification(self, duration=3000):
        # FIX: Calculate position AFTER widget is sized
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + 50
            
            # FIX: Ensure position is valid
            if x < 0:
                x = 50
            if y < 0:
                y = 50
            
            self.move(x, y)
        else:
            # FIX: If no parent, show at screen center
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = 50
            self.move(x, y)
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Fade in
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.start()
        
        # Auto hide
        QTimer.singleShot(duration, self.hide_notification)
    
    def hide_notification(self):
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.finished.connect(self.close)
        fade_out.start()
    
    @staticmethod
    def success(parent, title, message):
        return ModernNotification(parent, title, message, "success")
    
    @staticmethod
    def error(parent, title, message):
        return ModernNotification(parent, title, message, "error")
    
    @staticmethod
    def warning(parent, title, message):
        return ModernNotification(parent, title, message, "warning")
    
    @staticmethod
    def info(parent, title, message):
        return ModernNotification(parent, title, message, "info")
