#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRYPTO INSIGHT - Login & Dashboard System
Cyberpunk Theme - FIXED VERSION
"""

import os
import sys
import warnings

# ===== FIX: SUPPRESS QT GEOMETRY WARNINGS =====
warnings.filterwarnings("ignore")
os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false;*.warning=false"
os.environ["QT_DEBUG_PLUGINS"] = "0"

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect, QTimer
)

# Backend
from app_db_fixed import (
    verify_user, create_user, user_exists, setup_database,
    start_session, health_check
)

# Modern notification
from modern_notification import ModernNotification

APP_NAME = "Crypto Insight"


class CyberpunkAuthWindow(QtWidgets.QWidget):
    """Cyberpunk-themed authentication window"""
    
    ANIMATION_DURATION = 600
    EASING_CURVE = QEasingCurve.InOutCubic

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State tracking
        self.is_login_mode = True
        self.is_animating = False
        self.current_lang = "English"
        
        self._define_translations()
        self._setup_ui()
        self._apply_cyberpunk_style()
        self.retranslateUi()
        self._init_database()
        
        # Glitch animation timer
        self.glitch_timer = QTimer(self)
        self.glitch_timer.timeout.connect(self._glitch_effect)
        self.glitch_timer.start(5000)  # Glitch every 5 seconds
        
    def _define_translations(self):
        """Define translations"""
        self.translations = {
            "English": {
                "window_title": "Crypto Insight • Cyberpunk Access",
                "welcome_title": "Welcome to\nthe Future",
                "welcome_subtitle": "New to the system?",
                "btn_register": "Initialize",
                "welcome_back_title": "System\nOnline",
                "welcome_back_subtitle": "Already registered?",
                "btn_login": "Access",
                "login_title": "System Access",
                "placeholder_username": "Username",
                "placeholder_password": "Password",
                "forgot_password": "Recovery Protocol",
                "register_title": "Initialize User",
                "placeholder_email": "Email Address",
                "role_label": "Access Level:",
                "toast_fill_fields": "Input required: Username and Password",
                "toast_session_failed": "Session initialization failed",
                "toast_dashboard_not_found": "Dashboard module not found:",
                "toast_wrong_user_pass": "Authentication failed: Invalid credentials",
                "toast_fill_all_fields": "All fields required",
                "toast_username_min": "Username must be minimum 3 characters",
                "toast_password_min": "Password must be minimum 4 characters",
                "toast_username_taken": "Username already exists in system",
                "toast_register_success": "User '{0}' initialized successfully",
                "toast_register_failed": "User initialization failed",
                "toast_db_failed": "Database connection failed",
                "toast_db_error": "Database error:",
                "notif_success": "Success",
                "notif_error": "Error",
                "notif_warning": "Warning",
                "notif_info": "Info"
            },
            "Indonesia": {
                "window_title": "Crypto Insight • Akses Cyberpunk",
                "welcome_title": "Selamat Datang\ndi Masa Depan",
                "welcome_subtitle": "Pengguna baru?",
                "btn_register": "Inisialisasi",
                "welcome_back_title": "Sistem\nAktif",
                "welcome_back_subtitle": "Sudah terdaftar?",
                "btn_login": "Akses",
                "login_title": "Akses Sistem",
                "placeholder_username": "Nama Pengguna",
                "placeholder_password": "Kata Sandi",
                "forgot_password": "Protokol Pemulihan",
                "register_title": "Inisialisasi Pengguna",
                "placeholder_email": "Alamat Email",
                "role_label": "Tingkat Akses:",
                "toast_fill_fields": "Input diperlukan: Username dan Password",
                "toast_session_failed": "Inisialisasi sesi gagal",
                "toast_dashboard_not_found": "Modul dashboard tidak ditemukan:",
                "toast_wrong_user_pass": "Otentikasi gagal: Kredensial tidak valid",
                "toast_fill_all_fields": "Semua field harus diisi",
                "toast_username_min": "Username minimal 3 karakter",
                "toast_password_min": "Password minimal 4 karakter",
                "toast_username_taken": "Username sudah ada di sistem",
                "toast_register_success": "Pengguna '{0}' berhasil diinisialisasi",
                "toast_register_failed": "Inisialisasi pengguna gagal",
                "toast_db_failed": "Koneksi database gagal",
                "toast_db_error": "Error database:",
                "notif_success": "Berhasil",
                "notif_error": "Error",
                "notif_warning": "Peringatan",
                "notif_info": "Info"
            }
        }

    def _setup_ui(self):
        """Setup UI with cyberpunk elements"""
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Main container
        self.card_container = QtWidgets.QFrame()
        self.card_container.setObjectName("cardContainer")
        self.card_container.setFixedSize(900, 550)
        
        # Scan line effect overlay
        self.scan_line = QtWidgets.QFrame(self.card_container)
        self.scan_line.setObjectName("scanLine")
        self.scan_line.setGeometry(0, 0, 900, 4)
        self.scan_line.raise_()
        
        # Animate scan line
        self.scan_anim = QPropertyAnimation(self.scan_line, b"geometry")
        self.scan_anim.setDuration(3000)
        self.scan_anim.setStartValue(QRect(0, 0, 900, 4))
        self.scan_anim.setEndValue(QRect(0, 546, 900, 4))
        self.scan_anim.setEasingCurve(QEasingCurve.Linear)
        self.scan_anim.setLoopCount(-1)  # Infinite loop
        self.scan_anim.start()
        
        # ===== LEFT WELCOME PANEL (for Login mode) =====
        self.welcome_left = QtWidgets.QFrame(self.card_container)
        self.welcome_left.setObjectName("welcomePanel")
        self.welcome_left.setGeometry(0, 0, 450, 550)
        
        welcome_left_layout = QtWidgets.QVBoxLayout(self.welcome_left)
        welcome_left_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_left_layout.setSpacing(30)
        welcome_left_layout.setContentsMargins(50, 60, 50, 60)
        
        # Neon icon
        icon_left = QtWidgets.QLabel("◢")
        icon_left.setObjectName("neonIcon")
        icon_left.setAlignment(QtCore.Qt.AlignCenter)
        welcome_left_layout.addWidget(icon_left)
        
        self.welcome_left_title = QtWidgets.QLabel()
        self.welcome_left_title.setObjectName("welcomeTitle")
        self.welcome_left_title.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_left_title.setWordWrap(True)
        
        self.welcome_left_subtitle = QtWidgets.QLabel()
        self.welcome_left_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_left_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_register = QtWidgets.QPushButton()
        self.btn_switch_to_register.setObjectName("neonBtn")
        self.btn_switch_to_register.setFixedSize(220, 50)
        self.btn_switch_to_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_register.clicked.connect(self.switch_to_register)
        
        welcome_left_layout.addWidget(self.welcome_left_title)
        welcome_left_layout.addWidget(self.welcome_left_subtitle)
        welcome_left_layout.addSpacing(20)
        welcome_left_layout.addWidget(self.btn_switch_to_register, 0, QtCore.Qt.AlignCenter)
        
        # ===== RIGHT WELCOME PANEL (for Register mode) =====
        self.welcome_right = QtWidgets.QFrame(self.card_container)
        self.welcome_right.setObjectName("welcomePanel")
        self.welcome_right.setGeometry(450, 0, 450, 550)
        self.welcome_right.hide()
        
        welcome_right_layout = QtWidgets.QVBoxLayout(self.welcome_right)
        welcome_right_layout.setAlignment(QtCore.Qt.AlignCenter)
        welcome_right_layout.setSpacing(30)
        welcome_right_layout.setContentsMargins(50, 60, 50, 60)
        
        icon_right = QtWidgets.QLabel("◣")
        icon_right.setObjectName("neonIcon")
        icon_right.setAlignment(QtCore.Qt.AlignCenter)
        welcome_right_layout.addWidget(icon_right)
        
        self.welcome_right_title = QtWidgets.QLabel()
        self.welcome_right_title.setObjectName("welcomeTitle")
        self.welcome_right_title.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_right_title.setWordWrap(True)
        
        self.welcome_right_subtitle = QtWidgets.QLabel()
        self.welcome_right_subtitle.setObjectName("welcomeSubtitle")
        self.welcome_right_subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_switch_to_login = QtWidgets.QPushButton()
        self.btn_switch_to_login.setObjectName("neonBtn")
        self.btn_switch_to_login.setFixedSize(220, 50)
        self.btn_switch_to_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_switch_to_login.clicked.connect(self.switch_to_login)
        
        welcome_right_layout.addWidget(self.welcome_right_title)
        welcome_right_layout.addWidget(self.welcome_right_subtitle)
        welcome_right_layout.addSpacing(20)
        welcome_right_layout.addWidget(self.btn_switch_to_login, 0, QtCore.Qt.AlignCenter)
        
        # ===== LOGIN FORM PANEL =====
        self.login_panel = QtWidgets.QFrame(self.card_container)
        self.login_panel.setObjectName("formPanel")
        self.login_panel.setGeometry(450, 0, 450, 550)
        
        login_layout = QtWidgets.QVBoxLayout(self.login_panel)
        login_layout.setContentsMargins(50, 50, 50, 50)
        login_layout.setSpacing(24)
        
        self.login_title = QtWidgets.QLabel()
        self.login_title.setObjectName("formTitle")
        self.login_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.login_username_container = self._create_cyber_input(icon="▸")
        self.login_password_container = self._create_cyber_input(icon="◈", is_password=True)
        
        self.forgot_password_label = QtWidgets.QLabel()
        self.forgot_password_label.setObjectName("linkText")
        self.forgot_password_label.setAlignment(QtCore.Qt.AlignRight)
        self.forgot_password_label.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.btn_login = QtWidgets.QPushButton()
        self.btn_login.setObjectName("primaryBtn")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.do_login)
        
        login_layout.addWidget(self.login_title)
        login_layout.addSpacing(10)
        login_layout.addWidget(self.login_username_container)
        login_layout.addWidget(self.login_password_container)
        login_layout.addWidget(self.forgot_password_label)
        login_layout.addSpacing(10)
        login_layout.addWidget(self.btn_login)
        login_layout.addStretch()
        
        # ===== REGISTER FORM PANEL =====
        self.register_panel = QtWidgets.QFrame(self.card_container)
        self.register_panel.setObjectName("formPanel")
        self.register_panel.setGeometry(0, 0, 450, 550)
        self.register_panel.hide()
        
        register_layout = QtWidgets.QVBoxLayout(self.register_panel)
        register_layout.setContentsMargins(50, 40, 50, 40)
        register_layout.setSpacing(20)
        
        self.register_title = QtWidgets.QLabel()
        self.register_title.setObjectName("formTitle")
        self.register_title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.register_username_container = self._create_cyber_input(icon="▸")
        self.register_email_container = self._create_cyber_input(icon="@")
        self.register_password_container = self._create_cyber_input(icon="◈", is_password=True)
        
        role_container = QtWidgets.QWidget()
        role_layout = QtWidgets.QHBoxLayout(role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        self.role_label = QtWidgets.QLabel()
        self.role_label.setObjectName("roleLabel")
        self.register_role = QtWidgets.QComboBox()
        self.register_role.addItems(["user", "penerbit"])
        self.register_role.setObjectName("cyberCombo")
        role_layout.addWidget(self.role_label)
        role_layout.addWidget(self.register_role, 1)
        
        self.btn_register = QtWidgets.QPushButton()
        self.btn_register.setObjectName("primaryBtn")
        self.btn_register.setFixedHeight(50)
        self.btn_register.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self.do_register)
        
        register_layout.addWidget(self.register_title)
        register_layout.addSpacing(5)
        register_layout.addWidget(self.register_username_container)
        register_layout.addWidget(self.register_email_container)
        register_layout.addWidget(self.register_password_container)
        register_layout.addWidget(role_container)
        register_layout.addSpacing(10)
        register_layout.addWidget(self.btn_register)
        register_layout.addStretch()
        
        main_layout.addWidget(self.card_container)
        
        # Language selector (top right)
        self.lang_combo = QtWidgets.QComboBox(self.card_container)
        self.lang_combo.setObjectName("langCombo")
        self.lang_combo.addItems(self.translations.keys())
        self.lang_combo.setFixedSize(110, 36)
        self.lang_combo.move(self.card_container.width() - 125, 15)
        self.lang_combo.activated[str].connect(self.switch_language)
        self.lang_combo.raise_()

    def _create_cyber_input(self, icon="", is_password=False):
        """Create cyberpunk-styled input field"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        if icon:
            icon_label = QtWidgets.QLabel(icon)
            icon_label.setObjectName("inputIcon")
            layout.addWidget(icon_label)
        
        input_field = QtWidgets.QLineEdit()
        input_field.setObjectName("cyberInput")
        input_field.setFixedHeight(50)
        if is_password:
            input_field.setEchoMode(QtWidgets.QLineEdit.Password)
        
        layout.addWidget(input_field)
        
        container.setObjectName("inputContainer")
        return container

    def switch_language(self, lang_text):
        """Switch language"""
        self.current_lang = lang_text
        self.retranslateUi()

    def retranslateUi(self):
        """Apply translations"""
        t = self.translations.get(self.current_lang, self.translations["English"])
        
        self.setWindowTitle(t["window_title"])
        
        self.welcome_left_title.setText(t["welcome_title"])
        self.welcome_left_subtitle.setText(t["welcome_subtitle"])
        self.btn_switch_to_register.setText(t["btn_register"])
        
        self.welcome_right_title.setText(t["welcome_back_title"])
        self.welcome_right_subtitle.setText(t["welcome_back_subtitle"])
        self.btn_switch_to_login.setText(t["btn_login"])
        
        self.login_title.setText(t["login_title"])
        self.login_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.login_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.forgot_password_label.setText(t["forgot_password"])
        self.btn_login.setText(t["btn_login"])
        
        self.register_title.setText(t["register_title"])
        self.register_username_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_username"])
        self.register_email_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_email"])
        self.register_password_container.findChild(QtWidgets.QLineEdit).setPlaceholderText(t["placeholder_password"])
        self.role_label.setText(t["role_label"])
        self.btn_register.setText(t["btn_register"])

    def _glitch_effect(self):
        """Subtle glitch effect on welcome panels"""
        if not self.is_animating:
            import random
            if self.is_login_mode:
                current_geo = self.welcome_left.geometry()
                offset = random.choice([-2, -1, 0, 1, 2])
                self.welcome_left.setGeometry(
                    current_geo.x() + offset,
                    current_geo.y(),
                    current_geo.width(),
                    current_geo.height()
                )
                QtCore.QTimer.singleShot(50, lambda: self.welcome_left.setGeometry(0, 0, 450, 550))

    def switch_to_register(self):
        """Animate to register panel"""
        if not self.is_login_mode or self.is_animating:
            return
        
        self.is_login_mode = False
        self.is_animating = True
        
        anim_group_hide = QParallelAnimationGroup(self)
        
        anim_hide_1 = QPropertyAnimation(self.welcome_left, b"geometry")
        anim_hide_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_1.setStartValue(QRect(0, 0, 450, 550))
        anim_hide_1.setEndValue(QRect(225, 0, 0, 550))
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(450, 0, 450, 550))
        anim_hide_2.setEndValue(QRect(675, 0, 0, 550))
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_register)
        anim_group_hide.start()

    def _finish_flip_to_register(self):
        """Complete register transition"""
        self.welcome_left.hide()
        self.login_panel.hide()
        
        self.register_panel.setGeometry(225, 0, 0, 550)
        self.welcome_right.setGeometry(675, 0, 0, 550)
        self.register_panel.show()
        self.welcome_right.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.register_panel, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(225, 0, 0, 550))
        anim_show_1.setEndValue(QRect(0, 0, 450, 550))
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(675, 0, 0, 550))
        anim_show_2.setEndValue(QRect(450, 0, 450, 550))
        anim_show_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_show.addAnimation(anim_show_1)
        anim_group_show.addAnimation(anim_show_2)
        anim_group_show.finished.connect(lambda: setattr(self, 'is_animating', False))
        anim_group_show.start()

    def switch_to_login(self):
        """Animate to login panel"""
        if self.is_login_mode or self.is_animating:
            return
        
        self.is_login_mode = True
        self.is_animating = True
        
        anim_group_hide = QParallelAnimationGroup(self)
        
        anim_hide_1 = QPropertyAnimation(self.register_panel, b"geometry")
        anim_hide_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_1.setStartValue(QRect(0, 0, 450, 550))
        anim_hide_1.setEndValue(QRect(225, 0, 0, 550))
        anim_hide_1.setEasingCurve(self.EASING_CURVE)
        
        anim_hide_2 = QPropertyAnimation(self.welcome_right, b"geometry")
        anim_hide_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_hide_2.setStartValue(QRect(450, 0, 450, 550))
        anim_hide_2.setEndValue(QRect(675, 0, 0, 550))
        anim_hide_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_hide.addAnimation(anim_hide_1)
        anim_group_hide.addAnimation(anim_hide_2)
        anim_group_hide.finished.connect(self._finish_flip_to_login)
        anim_group_hide.start()

    def _finish_flip_to_login(self):
        """Complete login transition"""
        self.register_panel.hide()
        self.welcome_right.hide()
        
        self.welcome_left.setGeometry(225, 0, 0, 550)
        self.login_panel.setGeometry(675, 0, 0, 550)
        self.welcome_left.show()
        self.login_panel.show()
        
        anim_group_show = QParallelAnimationGroup(self)
        
        anim_show_1 = QPropertyAnimation(self.welcome_left, b"geometry")
        anim_show_1.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_1.setStartValue(QRect(225, 0, 0, 550))
        anim_show_1.setEndValue(QRect(0, 0, 450, 550))
        anim_show_1.setEasingCurve(self.EASING_CURVE)
        
        anim_show_2 = QPropertyAnimation(self.login_panel, b"geometry")
        anim_show_2.setDuration(self.ANIMATION_DURATION // 2)
        anim_show_2.setStartValue(QRect(675, 0, 0, 550))
        anim_show_2.setEndValue(QRect(450, 0, 450, 550))
        anim_show_2.setEasingCurve(self.EASING_CURVE)
        
        anim_group_show.addAnimation(anim_show_1)
        anim_group_show.addAnimation(anim_show_2)
        anim_group_show.finished.connect(lambda: setattr(self, 'is_animating', False))
        anim_group_show.start()

    def _get_trans_text(self, key):
        """Get translation text"""
        return self.translations[self.current_lang].get(key, f"<{key}>")

    def _get_trans_text_fmt(self, key, *args):
        """Get formatted translation text"""
        text = self.translations[self.current_lang].get(key, f"<{key}>")
        try:
            return text.format(*args)
        except:
            return text

    def do_login(self):
        """Handle login - FIXED VERSION"""
        if self.is_animating:
            return
            
        username_input = self.login_username_container.findChild(QtWidgets.QLineEdit)
        password_input = self.login_password_container.findChild(QtWidgets.QLineEdit)
        
        if not username_input or not password_input:
            return
        
        u = username_input.text().strip()
        p = password_input.text()
        
        if not u or not p:
            return self.toast(self._get_trans_text("toast_fill_fields"), "warning")
        
        role = verify_user(u, p)
        if role:
            sid = start_session(u)
            if sid is None:
                return self.toast(self._get_trans_text("toast_session_failed"), "error")
            
            # Hide auth window first
            self.hide()
            
            # Then import and show dashboard
            try:
                from dashboard_ui import Dashboard
                # Prepare user data dict
                user_data = {
                    'username': u,
                    'role': role,
                    'id': 1  # This will be fetched from DB in Dashboard
                }
                self.dashboard = Dashboard(user_data, sid)
                self.dashboard.destroyed.connect(self.show)
                self.dashboard.show()
            except ImportError as e:
                self.show()
                return self.toast(f"{self._get_trans_text('toast_dashboard_not_found')} {str(e)}", "error")
            except Exception as e:
                self.show()
                return self.toast(f"Dashboard error: {str(e)}", "error")
        else:
            return self.toast(self._get_trans_text("toast_wrong_user_pass"), "error")
    
    def do_register(self):
        """Handle registration"""
        if self.is_animating:
            return
            
        username_input = self.register_username_container.findChild(QtWidgets.QLineEdit)
        email_input = self.register_email_container.findChild(QtWidgets.QLineEdit)
        password_input = self.register_password_container.findChild(QtWidgets.QLineEdit)
        
        if not username_input or not email_input or not password_input:
            return
        
        u = username_input.text().strip()
        e = email_input.text().strip()
        p = password_input.text()
        role = self.register_role.currentText()
        
        if not u or not e or not p:
            return self.toast(self._get_trans_text("toast_fill_all_fields"), "warning")
        if len(u) < 3:
            return self.toast(self._get_trans_text("toast_username_min"), "warning")
        if len(p) < 4:
            return self.toast(self._get_trans_text("toast_password_min"), "warning")
        if user_exists(u):
            return self.toast(self._get_trans_text("toast_username_taken"), "error")
        
        ok = create_user(u, p, role)
        if ok:
            self.toast(self._get_trans_text_fmt("toast_register_success", u), "success")
            username_input.clear()
            email_input.clear()
            password_input.clear()
            QtCore.QTimer.singleShot(1500, self.switch_to_login)
        else:
            self.toast(self._get_trans_text("toast_register_failed"), "error")
    
    def toast(self, text: str, notification_type="info"):
        """Show notification"""
        if notification_type == "success":
            title = self._get_trans_text("notif_success")
            notif = ModernNotification.success(self, title, text)
        elif notification_type == "error":
            title = self._get_trans_text("notif_error")
            notif = ModernNotification.error(self, title, text)
        elif notification_type == "warning":
            title = self._get_trans_text("notif_warning")
            notif = ModernNotification.warning(self, title, text)
        else:
            title = self._get_trans_text("notif_info")
            notif = ModernNotification.info(self, title, text)
        notif.show_notification()
    
    def _init_database(self):
        """Initialize database"""
        try:
            if not health_check():
                self.toast(self._get_trans_text("toast_db_failed"), "error")
                return
            setup_database()
        except Exception as e:
            self.toast(f"{self._get_trans_text('toast_db_error')} {str(e)}", "error")
    
    def _apply_cyberpunk_style(self):
        """Apply cyberpunk theme with neon colors and monospace font"""
        self.setStyleSheet("""
            /* Root */
            QWidget {
                background: #0a0a0f;
                color: #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            
            #cardContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10, 10, 15, 0.95),
                    stop:0.5 rgba(20, 10, 30, 0.95),
                    stop:1 rgba(10, 10, 15, 0.95));
                border: 2px solid #ff00ff;
                border-radius: 0;
            }
            
            /* Scan line effect */
            #scanLine {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 transparent,
                    stop:0.5 rgba(0, 255, 255, 0.3),
                    stop:1 transparent);
                border: none;
            }
            
            /* Welcome Panel */
            #welcomePanel {
                background: transparent;
                border-right: 2px solid rgba(0, 255, 255, 0.3);
            }
            
            #neonIcon {
                font-size: 72px;
                color: #ff00ff;
                text-shadow: 0 0 20px #ff00ff,
                            0 0 40px #ff00ff,
                            0 0 60px #ff00ff;
            }
            
            #welcomeTitle {
                color: #00ffff;
                font-size: 42px;
                font-weight: 900;
                letter-spacing: 3px;
                text-shadow: 0 0 10px #00ffff,
                            0 0 20px #00ffff,
                            0 0 30px #00ffff,
                            0 0 40px #00ffff;
            }
            
            #welcomeSubtitle {
                color: #ff00ff;
                font-size: 14px;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #ff00ff;
            }
            
            #neonBtn {
                background: transparent;
                color: #00ffff;
                border: 3px solid #00ffff;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 2px;
                text-shadow: 0 0 10px #00ffff;
            }
            
            #neonBtn:hover {
                background: rgba(0, 255, 255, 0.1);
                color: #ff00ff;
                border-color: #ff00ff;
                text-shadow: 0 0 10px #ff00ff;
            }
            
            /* Form Panel */
            #formPanel {
                background: rgba(10, 10, 15, 0.8);
                border-left: 2px solid rgba(255, 0, 255, 0.3);
            }
            
            #formTitle {
                color: #ff00ff;
                font-size: 32px;
                font-weight: 900;
                letter-spacing: 3px;
                text-shadow: 0 0 10px #ff00ff,
                            0 0 20px #ff00ff,
                            0 0 30px #ff00ff;
            }
            
            /* Input Container */
            #inputContainer {
                background: rgba(0, 0, 0, 0.5);
                border: 2px solid #00ffff;
                border-radius: 0;
            }
            
            #inputContainer:focus-within {
                border: 2px solid #ff00ff;
            }
            
            #inputIcon {
                color: #00ffff;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 0 0 10px #00ffff;
            }
            
            #cyberInput {
                background: transparent;
                border: none;
                color: #00ffff;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 1px;
                padding: 0;
            }
            
            #cyberInput::placeholder {
                color: rgba(0, 255, 255, 0.4);
                letter-spacing: 1px;
            }
            
            /* ComboBox */
            #cyberCombo {
                background: rgba(0, 0, 0, 0.5);
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 0;
                padding: 12px;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            
            #cyberCombo:focus {
                border: 2px solid #ff00ff;
            }
            
            #cyberCombo::drop-down {
                border: none;
            }
            
            #cyberCombo QAbstractItemView {
                background: #0a0a0f;
                color: #00ffff;
                border: 2px solid #ff00ff;
                selection-background-color: rgba(255, 0, 255, 0.3);
                selection-color: #ff00ff;
            }
            
            #roleLabel {
                color: #ff00ff;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            
            /* Primary Button */
            #primaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 0, 255, 0.3),
                    stop:0.5 rgba(0, 255, 255, 0.3),
                    stop:1 rgba(255, 0, 255, 0.3));
                color: #00ffff;
                border: 3px solid #00ffff;
                border-radius: 0;
                font-size: 16px;
                font-weight: 900;
                letter-spacing: 3px;
                text-shadow: 0 0 10px #00ffff;
            }
            
            #primaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 0, 255, 0.5),
                    stop:0.5 rgba(0, 255, 255, 0.5),
                    stop:1 rgba(255, 0, 255, 0.5));
                color: #ff00ff;
                border-color: #ff00ff;
                text-shadow: 0 0 15px #ff00ff;
            }
            
            #primaryBtn:pressed {
                background: rgba(255, 0, 255, 0.7);
            }
            
            /* Link Text */
            #linkText {
                color: #ff00ff;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                text-shadow: 0 0 5px #ff00ff;
            }
            
            #linkText:hover {
                color: #00ffff;
                text-shadow: 0 0 10px #00ffff;
            }
            
            /* Language Combo */
            #langCombo {
                background: rgba(0, 0, 0, 0.7);
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 0;
                padding: 8px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            
            #langCombo::drop-down {
                border: none;
            }
            
            #langCombo QAbstractItemView {
                background: #0a0a0f;
                color: #00ffff;
                border: 2px solid #ff00ff;
                selection-background-color: rgba(255, 0, 255, 0.3);
                selection-color: #ff00ff;
            }
        """)
        
        font = QtGui.QFont("Consolas", 10)
        font.setBold(True)
        self.setFont(font)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = CyberpunkAuthWindow()
    w.show()
    sys.exit(app.exec_())
