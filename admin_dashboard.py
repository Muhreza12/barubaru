# enhanced_admin_dashboard_v2.py - Admin Dashboard dengan User Moderation + UI Keren
from PyQt5 import QtWidgets, QtCore, QtGui
from app_db_fixed import (
    connect, ban_user, unban_user, change_user_role, 
    delete_user, get_user_stats, get_all_users_with_ban_status
)
import datetime
import sqlite3
import json
from pathlib import Path


class EnhancedAdminDashboardV2(QtWidgets.QMainWindow):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username
        self.setWindowTitle("Crypto Insight — Enhanced Admin Dashboard V2 🔥")
        self.resize(1400, 900)
        
        # Setup logging database
        self.setup_monitoring_db()
        
        # Timer untuk auto-refresh
        self.auto_refresh_timer = QtCore.QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_check_new_users)
        self.auto_refresh_enabled = True
        self.last_user_count = 0
        
        # Store all users for filtering
        self.all_users = []
        
        # Setup UI
        self.setup_ui()
        
        # Muat data awal dan mulai auto-refresh
        self.load_users()
        self.load_monitoring_data()
        self.start_auto_refresh()
        self.add_log("✅ Enhanced Admin dashboard V2 dimulai - Monitoring + Moderation aktif")
        
        # Log admin login
        self.log_admin_activity("ADMIN_LOGIN", f"Admin {username} logged into dashboard")
        
    def setup_monitoring_db(self):
        """Setup database untuk monitoring."""
        self.monitoring_db = "admin_monitoring.db"
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    username TEXT,
                    action TEXT,
                    details TEXT,
                    ip_address TEXT DEFAULT 'localhost',
                    success BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    logout_time DATETIME,
                    session_duration INTEGER,
                    role TEXT,
                    ip_address TEXT DEFAULT 'localhost'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    admin_username TEXT,
                    action TEXT,
                    target_user TEXT,
                    details TEXT
                )
            """)
        
    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        # Main layout dengan tab widget
        main_layout = QtWidgets.QVBoxLayout(central)
        
        # Header dengan gradient
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4f46e5, stop:0.5 #7c3aed, stop:1 #ec4899);
                border-radius: 10px; padding: 20px;
            }
        """)
        header_layout = QtWidgets.QVBoxLayout(header_frame)
        
        title = QtWidgets.QLabel(f"👑 Enhanced Admin Dashboard V2")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        
        subtitle = QtWidgets.QLabel(f"Logged in as: {self.username} | Full Control Panel 🔥")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #e0e7ff; margin-top: 5px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addWidget(header_frame)
        
        # Tab widget untuk berbagai fungsi
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f1f5f9;
                color: #475569;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #4f46e5;
                border-bottom: 3px solid #4f46e5;
            }
            QTabBar::tab:hover {
                background: #e2e8f0;
            }
        """)
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: User Management dengan Moderation
        self.setup_user_management_tab()
        
        # Tab 2: Activity Monitoring
        self.setup_monitoring_tab()
        
        # Tab 3: Statistics & Reports
        self.setup_statistics_tab()
        
        # Tab 4: System Logs
        self.setup_logs_tab()
        
        # Bottom buttons
        bottom_layout = QtWidgets.QHBoxLayout()
        
        # Database Manager button
        db_manager_btn = QtWidgets.QPushButton("🗄️ Database Manager")
        db_manager_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #7c3aed, stop:1 #6d28d9);
                color: white; font-weight: 600;
                padding: 12px 24px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6d28d9, stop:1 #5b21b6);
            }
        """)
        db_manager_btn.clicked.connect(self.open_database_manager)
        bottom_layout.addWidget(db_manager_btn)
        
        bottom_layout.addStretch()
        
        # Logout button
        self.logout_btn = QtWidgets.QPushButton("🚪 Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #dc2626, stop:1 #b91c1c);
                color: white; font-weight: 600;
                padding: 12px 24px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        bottom_layout.addWidget(self.logout_btn)
        main_layout.addLayout(bottom_layout)
        
    def setup_user_management_tab(self):
        """Tab untuk manajemen user dengan moderation controls."""
        user_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(user_tab)
        
        # Status bar untuk monitoring
        self.status_label = QtWidgets.QLabel("🟢 Auto-monitoring aktif - Menunggu user baru...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #059669; font-weight: 600; padding: 14px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ecfdf5, stop:1 #d1fae5);
                border-radius: 8px; margin: 4px 0;
                border-left: 4px solid #059669;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Search & Filter Panel dengan style keren
        search_panel = QtWidgets.QFrame()
        search_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 10px; padding: 16px;
            }
        """)
        search_layout = QtWidgets.QHBoxLayout(search_panel)
        
        # Search box
        search_label = QtWidgets.QLabel("🔍 Search:")
        search_label.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 13px;")
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Type username to search...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px; border: 2px solid #cbd5e1;
                border-radius: 8px; background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4f46e5; background: #fefefe;
            }
        """)
        self.search_input.textChanged.connect(self.filter_users)
        
        # Role filter
        role_label = QtWidgets.QLabel("👤 Role:")
        role_label.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 13px;")
        self.role_filter = QtWidgets.QComboBox()
        self.role_filter.addItems(["All", "user", "penerbit", "admin"])
        self.role_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 14px; border: 2px solid #cbd5e1;
                border-radius: 8px; background: white;
                min-width: 120px; font-size: 13px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.role_filter.currentTextChanged.connect(self.filter_users)
        
        # Ban status filter
        ban_label = QtWidgets.QLabel("🚫 Status:")
        ban_label.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 13px;")
        self.ban_filter = QtWidgets.QComboBox()
        self.ban_filter.addItems(["All", "Active", "Banned"])
        self.ban_filter.setStyleSheet("""
            QComboBox {
                padding: 10px 14px; border: 2px solid #cbd5e1;
                border-radius: 8px; background: white;
                min-width: 120px; font-size: 13px;
            }
            QComboBox:hover {
                border-color: #94a3b8;
            }
        """)
        self.ban_filter.currentTextChanged.connect(self.filter_users)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 2)
        search_layout.addWidget(role_label)
        search_layout.addWidget(self.role_filter)
        search_layout.addWidget(ban_label)
        search_layout.addWidget(self.ban_filter)
        
        layout.addWidget(search_panel)
        
        # Toolbar dengan buttons keren
        toolbar = QtWidgets.QHBoxLayout()
        
        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4f46e5, stop:1 #4338ca);
                color: white; font-weight: 700; padding: 11px 22px;
                border-radius: 8px; border: none; font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4338ca, stop:1 #3730a3);
            }
            QPushButton:pressed { padding-top: 13px; }
        """)
        self.refresh_btn.clicked.connect(self.manual_refresh)
        
        # Copy button
        self.copy_btn = QtWidgets.QPushButton("📋 Copy Selected")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #10b981, stop:1 #059669);
                color: white; font-weight: 700; padding: 11px 22px;
                border-radius: 8px; border: none; font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        self.copy_btn.clicked.connect(self.copy_selected_rows)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QtWidgets.QPushButton("⏸️ Pause Auto-Check")
        self.auto_refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white; font-weight: 700; padding: 11px 22px;
                border-radius: 8px; border: none; font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #d97706, stop:1 #b45309);
            }
        """)
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        
        # Interval setting
        interval_layout = QtWidgets.QHBoxLayout()
        interval_label = QtWidgets.QLabel("⏱️ Check every:")
        interval_label.setStyleSheet("font-weight: 600; color: #475569; font-size: 13px;")
        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        self.interval_spin.setSuffix(" sec")
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px; border: 2px solid #cbd5e1;
                border-radius: 6px; background: white;
                min-width: 80px; font-size: 13px;
            }
        """)
        self.interval_spin.valueChanged.connect(self.update_refresh_interval)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spin)
        
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.copy_btn)
        toolbar.addLayout(interval_layout)
        toolbar.addWidget(self.auto_refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # User table dengan style modern
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Ban Status", "Actions", "Info"])
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                color: #1e293b; padding: 12px; border: none;
                font-weight: 700; font-size: 13px;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
        """)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 350)
        layout.addWidget(self.table)
        
        self.tab_widget.addTab(user_tab, "👥 User Management & Moderation")
        
    def setup_monitoring_tab(self):
        """Tab untuk monitoring aktivitas real-time."""
        monitoring_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(monitoring_tab)
        
        # Control panel
        control_panel = QtWidgets.QHBoxLayout()
        
        refresh_monitoring_btn = QtWidgets.QPushButton("🔄 Refresh Monitoring")
        refresh_monitoring_btn.clicked.connect(self.load_monitoring_data)
        refresh_monitoring_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #059669, stop:1 #047857);
                color: white; font-weight: 700;
                padding: 11px 22px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #047857, stop:1 #065f46);
            }
        """)
        
        export_btn = QtWidgets.QPushButton("📊 Export Data")
        export_btn.clicked.connect(self.export_monitoring_data)
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #7c3aed, stop:1 #6d28d9);
                color: white; font-weight: 700;
                padding: 11px 22px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6d28d9, stop:1 #5b21b6);
            }
        """)
        
        control_panel.addWidget(refresh_monitoring_btn)
        control_panel.addWidget(export_btn)
        control_panel.addStretch()
        layout.addLayout(control_panel)
        
        # Statistics cards
        stats_layout = QtWidgets.QGridLayout()
        
        self.stats_cards = {}
        stats_info = [
            ("total_logins", "Total Logins", "#3b82f6"),
            ("active_today", "Active Today", "#10b981"),
            ("failed_attempts", "Failed Attempts", "#dc2626"),
            ("admin_actions", "Admin Actions", "#7c3aed")
        ]
        
        for i, (key, label, color) in enumerate(stats_info):
            card = self.create_stat_card(label, "0", color)
            self.stats_cards[key] = card['value_label']
            stats_layout.addWidget(card['widget'], i // 2, i % 2)
        
        layout.addLayout(stats_layout)
        
        # Recent activities table
        activities_group = QtWidgets.QGroupBox("📋 Recent User Activities")
        activities_group.setStyleSheet("""
            QGroupBox {
                font-weight: 700; font-size: 14px; color: #1e293b;
                border: 2px solid #e2e8f0; border-radius: 8px;
                margin-top: 12px; padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px; padding: 0 8px;
            }
        """)
        activities_layout = QtWidgets.QVBoxLayout(activities_group)
        
        self.activities_table = QtWidgets.QTableWidget(0, 5)
        self.activities_table.setHorizontalHeaderLabels(["Time", "Username", "Action", "Details", "Success"])
        self.activities_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                color: #1e293b; padding: 10px; border: none;
                font-weight: 700;
            }
        """)
        
        header = self.activities_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 100)
        header.resizeSection(1, 120)
        header.resizeSection(2, 150)
        header.resizeSection(4, 80)
        
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
            }
        """)
        activities_layout.addWidget(self.activities_table)
        
        layout.addWidget(activities_group)
        
        self.tab_widget.addTab(monitoring_tab, "📊 Activity Monitor")
        
    def setup_statistics_tab(self):
        """Tab untuk statistik dan laporan."""
        stats_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(stats_tab)
        
        # Period selector
        period_layout = QtWidgets.QHBoxLayout()
        period_label = QtWidgets.QLabel("📅 Period:")
        period_label.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 14px;")
        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["Last 24 hours", "Last 7 days", "Last 30 days"])
        self.period_combo.setCurrentText("Last 7 days")
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 16px; border: 2px solid #cbd5e1;
                border-radius: 8px; background: white;
                min-width: 150px; font-size: 13px; font-weight: 600;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.update_statistics)
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_combo)
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Statistics display
        self.stats_text = QtWidgets.QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QtGui.QFont("Consolas", 10))
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background: #f8fafc; border: 2px solid #e2e8f0;
                border-radius: 8px; padding: 16px;
            }
        """)
        layout.addWidget(self.stats_text)
        
        # Generate report button
        report_btn = QtWidgets.QPushButton("📋 Generate Detailed Report")
        report_btn.clicked.connect(self.generate_detailed_report)
        report_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #dc2626, stop:1 #b91c1c);
                color: white; font-weight: 700;
                padding: 12px 24px; border-radius: 8px; border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        layout.addWidget(report_btn)
        
        self.tab_widget.addTab(stats_tab, "📈 Statistics & Reports")
        
    def setup_logs_tab(self):
        """Tab untuk system logs."""
        logs_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(logs_tab)
        
        # Log area header
        log_header = QtWidgets.QHBoxLayout()
        log_label = QtWidgets.QLabel("📋 System & Admin Activity Logs")
        log_label.setStyleSheet("font-weight: 700; font-size: 16px; color: #1e293b;")
        log_header.addWidget(log_label)
        log_header.addStretch()
        
        # Clear logs button
        clear_btn = QtWidgets.QPushButton("🗑️ Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6b7280, stop:1 #4b5563);
                color: white; font-weight: 700;
                padding: 10px 20px; border-radius: 8px; border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4b5563, stop:1 #374151);
            }
        """)
        log_header.addWidget(clear_btn)
        layout.addLayout(log_header)
        
        # Log text area
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #1e293b; color: #e2e8f0;
                border: 2px solid #475569;
                border-radius: 8px; padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.log_text)
        
        self.tab_widget.addTab(logs_tab, "📝 System Logs")
        
    def create_stat_card(self, title, value, color):
        """Create a statistics card widget."""
        card_widget = QtWidgets.QFrame()
        card_widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 white, stop:1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 12px; padding: 20px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout(card_widget)
        
        value_label = QtWidgets.QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px; font-weight: 900; color: {color};
            margin-bottom: 8px;
        """)
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-weight: 700; font-size: 14px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return {'widget': card_widget, 'value_label': value_label}
        
    # ========== USER MODERATION METHODS ==========
    
    def load_users(self):
        """Load all users with ban status and create action buttons."""
        try:
            rows = get_all_users_with_ban_status()
            self.all_users = rows  # Store for filtering
            
            self.display_users(rows)
            
            if rows:
                self.last_user_count = len(rows)
                
            self.add_log(f"📊 Loaded {len(rows)} users")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
            self.add_log(f"❌ Error loading users: {str(e)}")
            
    def display_users(self, rows):
        """Display users in table with moderation buttons."""
        self.table.setRowCount(0)
        
        for r, (uid, uname, role, is_banned) in enumerate(rows):
            self.table.insertRow(r)
            
            # ID
            id_item = QtWidgets.QTableWidgetItem(str(uid))
            id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(r, 0, id_item)
            
            # Username
            username_item = QtWidgets.QTableWidgetItem(uname)
            username_item.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
            self.table.setItem(r, 1, username_item)
            
            # Role dengan badge color
            role_item = QtWidgets.QTableWidgetItem(role.upper())
            role_item.setTextAlignment(QtCore.Qt.AlignCenter)
            role_item.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
            if role == 'admin':
                role_item.setBackground(QtGui.QColor("#fef3c7"))
                role_item.setForeground(QtGui.QColor("#92400e"))
            elif role == 'penerbit':
                role_item.setBackground(QtGui.QColor("#dbeafe"))
                role_item.setForeground(QtGui.QColor("#1e40af"))
            else:
                role_item.setBackground(QtGui.QColor("#f3f4f6"))
                role_item.setForeground(QtGui.QColor("#374151"))
            self.table.setItem(r, 2, role_item)
            
            # Ban Status
            status_item = QtWidgets.QTableWidgetItem("🚫 BANNED" if is_banned else "✅ Active")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
            if is_banned:
                status_item.setBackground(QtGui.QColor("#fee2e2"))
                status_item.setForeground(QtGui.QColor("#991b1b"))
            else:
                status_item.setBackground(QtGui.QColor("#d1fae5"))
                status_item.setForeground(QtGui.QColor("#065f46"))
            self.table.setItem(r, 3, status_item)
            
            # Actions (buttons dalam widget)
            if uname != 'admin':  # Can't moderate admin
                actions_widget = QtWidgets.QWidget()
                actions_layout = QtWidgets.QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(6)
                
                # Ban/Unban button
                ban_btn = QtWidgets.QPushButton("🚫 Ban" if not is_banned else "✅ Unban")
                ban_btn.setFixedSize(80, 30)
                ban_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {'#dc2626' if not is_banned else '#10b981'};
                        color: white; font-weight: 700;
                        border-radius: 6px; border: none;
                        font-size: 11px;
                    }}
                    QPushButton:hover {{
                        background: {'#b91c1c' if not is_banned else '#059669'};
                    }}
                """)
                ban_btn.clicked.connect(lambda checked, u=uname, b=is_banned: self.toggle_ban_user(u, b))
                actions_layout.addWidget(ban_btn)
                
                # Change Role button
                role_btn = QtWidgets.QPushButton("🔄 Role")
                role_btn.setFixedSize(70, 30)
                role_btn.setStyleSheet("""
                    QPushButton {
                        background: #3b82f6; color: white; font-weight: 700;
                        border-radius: 6px; border: none;
                        font-size: 11px;
                    }
                    QPushButton:hover { background: #2563eb; }
                """)
                role_btn.clicked.connect(lambda checked, u=uname, r=role: self.change_role_dialog(u, r))
                actions_layout.addWidget(role_btn)
                
                # Delete button
                delete_btn = QtWidgets.QPushButton("🗑️ Delete")
                delete_btn.setFixedSize(80, 30)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background: #ef4444; color: white; font-weight: 700;
                        border-radius: 6px; border: none;
                        font-size: 11px;
                    }
                    QPushButton:hover { background: #dc2626; }
                """)
                delete_btn.clicked.connect(lambda checked, u=uname: self.delete_user_confirm(u))
                actions_layout.addWidget(delete_btn)
                
                actions_layout.addStretch()
                self.table.setCellWidget(r, 4, actions_widget)
            else:
                admin_label = QtWidgets.QLabel("⚡ PROTECTED")
                admin_label.setAlignment(QtCore.Qt.AlignCenter)
                admin_label.setStyleSheet("""
                    color: #7c3aed; font-weight: 700;
                    background: #f3e8ff; padding: 6px;
                    border-radius: 6px;
                """)
                self.table.setCellWidget(r, 4, admin_label)
            
            # Info button
            info_btn = QtWidgets.QPushButton("ℹ️ View Stats")
            info_btn.setStyleSheet("""
                QPushButton {
                    background: #6366f1; color: white; font-weight: 700;
                    border-radius: 6px; padding: 8px 16px;
                    border: none; font-size: 11px;
                }
                QPushButton:hover { background: #4f46e5; }
            """)
            info_btn.clicked.connect(lambda checked, u=uname: self.show_user_stats(u))
            self.table.setCellWidget(r, 5, info_btn)
            
        self.table.resizeColumnsToContents()
        
    def toggle_ban_user(self, username, currently_banned):
        """Ban or unban a user."""
        action = "unban" if currently_banned else "ban"
        
        reply = QtWidgets.QMessageBox.question(
            self, 
            f"{action.title()} User",
            f"Are you sure you want to {action} user '{username}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            if currently_banned:
                success = unban_user(username, self.username)
                msg = "unbanned"
            else:
                success = ban_user(username, self.username)
                msg = "banned"
            
            if success:
                QtWidgets.QMessageBox.information(self, "Success", f"User '{username}' has been {msg}!")
                self.add_log(f"{'🚫' if not currently_banned else '✅'} User '{username}' {msg} by admin")
                self.log_admin_activity(f"{'BAN' if not currently_banned else 'UNBAN'}_USER", 
                                       f"{msg.title()} user: {username}", username)
                self.load_users()
                self.load_monitoring_data()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to {action} user '{username}'")
                
    def change_role_dialog(self, username, current_role):
        """Show dialog to change user role."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Change Role: {username}")
        dialog.resize(400, 200)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        info_label = QtWidgets.QLabel(f"Current role: <b>{current_role}</b>")
        info_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(info_label)
        
        role_label = QtWidgets.QLabel("Select new role:")
        role_label.setStyleSheet("font-weight: 700; font-size: 13px;")
        layout.addWidget(role_label)
        
        role_combo = QtWidgets.QComboBox()
        role_combo.addItems(["user", "penerbit"])
        role_combo.setCurrentText(current_role if current_role in ["user", "penerbit"] else "user")
        role_combo.setStyleSheet("""
            QComboBox {
                padding: 10px; border: 2px solid #cbd5e1;
                border-radius: 6px; font-size: 13px;
            }
        """)
        layout.addWidget(role_combo)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.setStyleSheet("""
            QPushButton {
                padding: 8px 20px; border-radius: 6px;
                font-weight: 700;
            }
        """)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_role = role_combo.currentText()
            if new_role != current_role:
                success = change_user_role(username, new_role, self.username)
                if success:
                    QtWidgets.QMessageBox.information(
                        self, "Success", 
                        f"User '{username}' role changed to '{new_role}'!"
                    )
                    self.add_log(f"🔄 User '{username}' role changed: {current_role} → {new_role}")
                    self.log_admin_activity("CHANGE_ROLE", 
                                           f"Changed role: {current_role} → {new_role}", username)
                    self.load_users()
                    self.load_monitoring_data()
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to change role for '{username}'")
                    
    def delete_user_confirm(self, username):
        """Confirm and delete user."""
        reply = QtWidgets.QMessageBox.warning(
            self, 
            "⚠️ Delete User",
            f"<b>WARNING!</b><br><br>"
            f"You are about to delete user '<b>{username}</b>' and <b>ALL</b> their data:<br>"
            f"• All articles<br>"
            f"• All comments<br>"
            f"• All likes & bookmarks<br>"
            f"• User sessions<br><br>"
            f"<b>This action CANNOT be undone!</b><br><br>"
            f"Are you absolutely sure?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Double confirmation
            confirm = QtWidgets.QInputDialog.getText(
                self,
                "Final Confirmation",
                f"Type '{username}' to confirm deletion:"
            )
            
            if confirm[1] and confirm[0] == username:
                success = delete_user(username, self.username)
                if success:
                    QtWidgets.QMessageBox.information(
                        self, "Deleted", 
                        f"User '{username}' and all data have been deleted."
                    )
                    self.add_log(f"🗑️ User '{username}' DELETED by admin (with all data)")
                    self.log_admin_activity("DELETE_USER", 
                                           f"Deleted user and all data", username)
                    self.load_users()
                    self.load_monitoring_data()
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete user '{username}'")
            else:
                QtWidgets.QMessageBox.information(self, "Cancelled", "User deletion cancelled.")
                
    def show_user_stats(self, username):
        """Show detailed user statistics in a dialog."""
        stats = get_user_stats(username)
        
        if not stats:
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not retrieve stats for '{username}'")
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"📊 User Stats: {username}")
        dialog.resize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Header
        header = QtWidgets.QLabel(f"👤 {stats['username']}")
        header.setStyleSheet("""
            font-size: 20px; font-weight: 700; color: #1e293b;
            padding: 16px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #f1f5f9, stop:1 #e2e8f0);
            border-radius: 8px; margin-bottom: 16px;
        """)
        header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(header)
        
        # Stats grid
        stats_grid = QtWidgets.QGridLayout()
        
        stat_items = [
            ("Role", stats['role'].upper(), "#4f46e5"),
            ("Status", "🚫 BANNED" if stats['is_banned'] else "✅ Active", "#ef4444" if stats['is_banned'] else "#10b981"),
            ("Articles", str(stats['article_count']), "#3b82f6"),
            ("Comments", str(stats['comment_count']), "#8b5cf6"),
            ("Likes Received", str(stats['likes_received']), "#ec4899"),
            ("Bookmarks", str(stats['bookmarks_received']), "#f59e0b"),
            ("Total Views", str(stats['total_views']), "#06b6d4"),
        ]
        
        for i, (label, value, color) in enumerate(stat_items):
            row, col = i // 2, i % 2
            
            stat_frame = QtWidgets.QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            
            stat_layout = QtWidgets.QVBoxLayout(stat_frame)
            
            value_label = QtWidgets.QLabel(value)
            value_label.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {color};")
            value_label.setAlignment(QtCore.Qt.AlignCenter)
            
            label_widget = QtWidgets.QLabel(label)
            label_widget.setStyleSheet("color: #64748b; font-weight: 700; font-size: 12px;")
            label_widget.setAlignment(QtCore.Qt.AlignCenter)
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_widget)
            
            stats_grid.addWidget(stat_frame, row, col)
        
        layout.addLayout(stats_grid)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6b7280; color: white; font-weight: 700;
                padding: 10px; border-radius: 6px;
            }
            QPushButton:hover { background: #4b5563; }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
        self.log_admin_activity("VIEW_USER_STATS", f"Viewed stats for user", username)
        
    def filter_users(self):
        """Filter users based on search and filters."""
        search_text = self.search_input.text().lower()
        role_filter = self.role_filter.currentText()
        ban_filter = self.ban_filter.currentText()
        
        filtered_users = []
        
        for uid, uname, role, is_banned in self.all_users:
            # Search filter
            if search_text and search_text not in uname.lower():
                continue
            
            # Role filter
            if role_filter != "All" and role != role_filter:
                continue
            
            # Ban filter
            if ban_filter == "Active" and is_banned:
                continue
            if ban_filter == "Banned" and not is_banned:
                continue
            
            filtered_users.append((uid, uname, role, is_banned))
        
        self.display_users(filtered_users)
        self.add_log(f"🔍 Filtered users: {len(filtered_users)} results")
        
    # ========== EXISTING METHODS (KEEP AS IS) ==========
    
    def log_admin_activity(self, action, details="", target_user=""):
        """Log admin activities untuk monitoring."""
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                INSERT INTO admin_actions (admin_username, action, target_user, details)
                VALUES (?, ?, ?, ?)
            """, (self.username, action, target_user, details))
        
        self.add_log(f"🔧 ADMIN: {action} - {details}")
        
    def log_user_activity(self, username, action, details="", success=True):
        """Log user activities."""
        with sqlite3.connect(self.monitoring_db) as conn:
            conn.execute("""
                INSERT INTO user_activities (username, action, details, success)
                VALUES (?, ?, ?, ?)
            """, (username, action, details, success))
            
    def load_monitoring_data(self):
        """Load monitoring data untuk tab monitoring."""
        try:
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # Total logins
                cursor.execute("SELECT COUNT(*) FROM user_activities WHERE action LIKE '%LOGIN%'")
                total_logins = cursor.fetchone()[0]
                
                # Active today
                cursor.execute("""
                    SELECT COUNT(DISTINCT username) FROM user_activities 
                    WHERE date(timestamp) = date('now') AND action LIKE '%LOGIN%'
                """)
                active_today = cursor.fetchone()[0]
                
                # Failed attempts
                cursor.execute("""
                    SELECT COUNT(*) FROM user_activities 
                    WHERE action LIKE '%LOGIN%' AND success = 0
                """)
                failed_attempts = cursor.fetchone()[0]
                
                # Admin actions
                cursor.execute("SELECT COUNT(*) FROM admin_actions")
                admin_actions = cursor.fetchone()[0]
                
                # Update statistics cards
                self.stats_cards["total_logins"].setText(str(total_logins))
                self.stats_cards["active_today"].setText(str(active_today))
                self.stats_cards["failed_attempts"].setText(str(failed_attempts))
                self.stats_cards["admin_actions"].setText(str(admin_actions))
                
                # Load recent activities
                cursor.execute("""
                    SELECT timestamp, username, action, details, success
                    FROM user_activities 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """)
                
                activities = cursor.fetchall()
                self.activities_table.setRowCount(len(activities))
                
                for row, (timestamp, username, action, details, success) in enumerate(activities):
                    # Format timestamp
                    try:
                        dt = datetime.datetime.fromisoformat(timestamp)
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp.split(' ')[-1] if ' ' in timestamp else timestamp
                    
                    self.activities_table.setItem(row, 0, QtWidgets.QTableWidgetItem(time_str))
                    self.activities_table.setItem(row, 1, QtWidgets.QTableWidgetItem(username or "N/A"))
                    self.activities_table.setItem(row, 2, QtWidgets.QTableWidgetItem(action or "N/A"))
                    self.activities_table.setItem(row, 3, QtWidgets.QTableWidgetItem(details or "N/A"))
                    
                    # Success indicator with color
                    success_item = QtWidgets.QTableWidgetItem("✅" if success else "❌")
                    if not success:
                        success_item.setBackground(QtGui.QColor("#fecaca"))
                    self.activities_table.setItem(row, 4, success_item)
                    
        except Exception as e:
            self.add_log(f"❌ Error loading monitoring data: {str(e)}")
            
    def update_statistics(self):
        """Update statistics based on selected period."""
        period_map = {
            "Last 24 hours": 1,
            "Last 7 days": 7,
            "Last 30 days": 30
        }
        days = period_map.get(self.period_combo.currentText(), 7)
        
        try:
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # Generate statistics report
                cursor.execute(f"""
                    SELECT COUNT(*) FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days')
                """)
                total_activities = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT username) FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days') AND action LIKE '%LOGIN%'
                """)
                unique_users = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT username, COUNT(*) as count FROM user_activities 
                    WHERE timestamp > datetime('now', '-{days} days')
                    GROUP BY username ORDER BY count DESC LIMIT 10
                """)
                top_users = cursor.fetchall()
                
                # Format report
                report = f"""
╔══════════════════════════════════════════════════════════════╗
║          CRYPTO INSIGHT MONITORING REPORT V2 🔥              ║
╠══════════════════════════════════════════════════════════════╣
║ Period: {self.period_combo.currentText():<51} ║
║ Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<49} ║
╚══════════════════════════════════════════════════════════════╝

📊 SUMMARY STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Total Activities      : {total_activities:,}
  • Unique Active Users   : {unique_users}
  • Avg Activities/User   : {total_activities/unique_users if unique_users > 0 else 0:.1f}


👥 TOP 10 MOST ACTIVE USERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                for i, (username, count) in enumerate(top_users, 1):
                    bar = "█" * min(int(count / 5), 40)
                    report += f"  {i:2d}. {username:<20} {bar} {count:>5} activities\n"
                
                report += f"""

📈 INSIGHTS & ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Analysis Period    : {self.period_combo.currentText()}
  • Monitoring Status  : ✅ Active (Real-time)
  • Data Accuracy      : 100%
  • Last Updated       : {datetime.datetime.now().strftime('%H:%M:%S')}


═══════════════════════════════════════════════════════════════
              END OF REPORT - Generated by Admin Panel V2
═══════════════════════════════════════════════════════════════
"""
                
                self.stats_text.setPlainText(report)
                
        except Exception as e:
            self.stats_text.setPlainText(f"Error generating statistics: {str(e)}")
            
    def generate_detailed_report(self):
        """Generate detailed report in new window."""
        try:
            report_dialog = QtWidgets.QDialog(self)
            report_dialog.setWindowTitle("📋 Comprehensive Monitoring Report")
            report_dialog.resize(900, 700)
            
            layout = QtWidgets.QVBoxLayout(report_dialog)
            
            # Generate comprehensive report
            with sqlite3.connect(self.monitoring_db) as conn:
                cursor = conn.cursor()
                
                # All activities
                cursor.execute("""
                    SELECT timestamp, username, action, details, success
                    FROM user_activities 
                    ORDER BY timestamp DESC
                """)
                all_activities = cursor.fetchall()
                
                # Admin actions
                cursor.execute("""
                    SELECT timestamp, admin_username, action, target_user, details
                    FROM admin_actions 
                    ORDER BY timestamp DESC
                """)
                admin_actions = cursor.fetchall()
            
            report_text = QtWidgets.QTextEdit()
            report_text.setFont(QtGui.QFont("Consolas", 9))
            report_text.setStyleSheet("""
                QTextEdit {
                    background: #1e293b; color: #e2e8f0;
                    border: 2px solid #475569; border-radius: 8px;
                    padding: 16px;
                }
            """)
            
            detailed_report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE CRYPTO INSIGHT MONITORING REPORT                 ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<67} ║
║ Admin User: {self.username:<66} ║
╚════════════════════════════════════════════════════════════════════════════╝


📋 ALL USER ACTIVITIES (Total: {len(all_activities)}):
{'═'*80}
"""
            
            for i, (timestamp, username, action, details, success) in enumerate(all_activities[:100], 1):
                status = "✅" if success else "❌"
                detailed_report += f"{i:3d}. [{timestamp}] {username:<15} | {action:<20} | {details[:40]:<40} {status}\n"
            
            if len(all_activities) > 100:
                detailed_report += f"\n... and {len(all_activities) - 100} more activities\n"
            
            detailed_report += f"""


🔧 ADMIN ACTIONS (Total: {len(admin_actions)}):
{'═'*80}
"""
            
            for i, (timestamp, admin_user, action, target, details) in enumerate(admin_actions, 1):
                detailed_report += f"{i:3d}. [{timestamp}] {admin_user:<12} | {action:<25} | Target: {target:<15} | {details[:30]}\n"
            
            detailed_report += """


╔════════════════════════════════════════════════════════════════════════════╗
║                            END OF DETAILED REPORT                           ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
            
            report_text.setPlainText(detailed_report)
            layout.addWidget(report_text)
            
            # Buttons
            btn_layout = QtWidgets.QHBoxLayout()
            
            export_btn = QtWidgets.QPushButton("💾 Export to File")
            export_btn.setStyleSheet("""
                QPushButton {
                    background: #10b981; color: white; font-weight: 700;
                    padding: 10px 20px; border-radius: 6px;
                }
                QPushButton:hover { background: #059669; }
            """)
            export_btn.clicked.connect(lambda: self.export_report_to_file(detailed_report))
            btn_layout.addWidget(export_btn)
            
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #6b7280; color: white; font-weight: 700;
                    padding: 10px 20px; border-radius: 6px;
                }
                QPushButton:hover { background: #4b5563; }
            """)
            close_btn.clicked.connect(report_dialog.accept)
            btn_layout.addWidget(close_btn)
            
            layout.addLayout(btn_layout)
            
            report_dialog.exec_()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def export_report_to_file(self, report_content):
        """Export report to text file."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Report", 
            f"crypto_insight_report_{datetime.date.today()}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                QtWidgets.QMessageBox.information(self, "✅ Success", f"Report exported to:\n{filename}")
                self.log_admin_activity("EXPORT_REPORT", f"Exported monitoring report to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}")
                
    def export_monitoring_data(self):
        """Export monitoring data to JSON."""
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Monitoring Data", 
                f"monitoring_data_{datetime.date.today()}.json",
                "JSON Files (*.json)"
            )
            
            if filename:
                with sqlite3.connect(self.monitoring_db) as conn:
                    cursor = conn.cursor()
                    
                    # Get all data
                    cursor.execute("SELECT * FROM user_activities ORDER BY timestamp DESC")
                    activities = cursor.fetchall()
                    
                    cursor.execute("SELECT * FROM admin_actions ORDER BY timestamp DESC")
                    admin_actions = cursor.fetchall()
                
                export_data = {
                    'export_info': {
                        'generated_at': datetime.datetime.now().isoformat(),
                        'admin_user': self.username,
                        'total_activities': len(activities),
                        'total_admin_actions': len(admin_actions),
                        'version': 'V2'
                    },
                    'user_activities': activities,
                    'admin_actions': admin_actions
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                QtWidgets.QMessageBox.information(self, "✅ Export Complete", f"Data exported to:\n{filename}")
                self.log_admin_activity("EXPORT_DATA", f"Exported monitoring data to JSON: {filename}")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            
    def clear_logs(self):
        """Clear system logs display."""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear Logs", 
            "Are you sure you want to clear the log display?\n(This won't delete database records)",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.log_text.clear()
            self.add_log("🗑️ Log display cleared by admin")
            self.log_admin_activity("CLEAR_LOGS", "Cleared system log display")
            
    def start_auto_refresh(self):
        """Mulai auto-refresh dengan interval yang ditentukan."""
        interval = self.interval_spin.value() * 1000  # Convert to milliseconds
        self.auto_refresh_timer.start(interval)
        self.auto_refresh_enabled = True
        
    def stop_auto_refresh(self):
        """Hentikan auto-refresh."""
        self.auto_refresh_timer.stop()
        self.auto_refresh_enabled = False
        
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off."""
        if self.auto_refresh_enabled:
            self.stop_auto_refresh()
            self.auto_refresh_btn.setText("▶️ Resume Auto-Check")
            self.auto_refresh_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #059669, stop:1 #047857);
                    color: white; font-weight: 700;
                    padding: 11px 22px; border-radius: 8px; border: none; font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #047857, stop:1 #065f46);
                }
            """)
            self.status_label.setText("⏸️ Auto-monitoring dijeda")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #dc2626; font-weight: 600; padding: 14px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #fef2f2, stop:1 #fee2e2);
                    border-radius: 8px; margin: 4px 0;
                    border-left: 4px solid #dc2626;
                    font-size: 13px;
                }
            """)
            self.add_log("⏸️ Auto-monitoring dijeda oleh admin")
            self.log_admin_activity("PAUSE_MONITORING", "Paused auto-refresh monitoring")
        else:
            self.start_auto_refresh()
            self.auto_refresh_btn.setText("⏸️ Pause Auto-Check")
            self.auto_refresh_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #f59e0b, stop:1 #d97706);
                    color: white; font-weight: 700;
                    padding: 11px 22px; border-radius: 8px; border: none; font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #d97706, stop:1 #b45309);
                }
            """)
            self.status_label.setText("🟢 Auto-monitoring aktif - Menunggu user baru...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #059669; font-weight: 600; padding: 14px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #ecfdf5, stop:1 #d1fae5);
                    border-radius: 8px; margin: 4px 0;
                    border-left: 4px solid #059669;
                    font-size: 13px;
                }
            """)
            self.add_log("▶️ Auto-monitoring dilanjutkan")
            self.log_admin_activity("RESUME_MONITORING", "Resumed auto-refresh monitoring")
            
    def update_refresh_interval(self):
        """Update interval auto-refresh."""
        if self.auto_refresh_enabled:
            self.stop_auto_refresh()
            self.start_auto_refresh()
            interval = self.interval_spin.value()
            self.add_log(f"⚙️ Interval auto-check diubah menjadi {interval} detik")
            self.log_admin_activity("CHANGE_INTERVAL", f"Changed refresh interval to {interval} seconds")
            
    def auto_check_new_users(self):
        """Cek otomatis apakah ada user baru."""
        try:
            rows = get_all_users_with_ban_status()
            current_count = len(rows)
            
            if self.last_user_count == 0:
                # First time initialization
                self.last_user_count = current_count
                return
                
            if current_count > self.last_user_count:
                # Ada user baru!
                new_users = current_count - self.last_user_count
                self.add_log(f"🚨 ALERT: {new_users} user baru terdeteksi!")
                self.status_label.setText(f"🔔 {new_users} user baru terdeteksi! Memuat ulang data...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #dc2626; font-weight: 600; padding: 14px; 
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #fef2f2, stop:1 #fee2e2);
                        border-radius: 8px; margin: 4px 0;
                        border-left: 4px solid #dc2626;
                        font-size: 13px;
                        animation: blink 1s;
                    }
                """)
                
                # Log new user detection
                self.log_admin_activity("NEW_USER_DETECTED", f"{new_users} new users detected")
                
                # Refresh table
                self.load_users()
                self.load_monitoring_data()
                self.last_user_count = current_count
                
                # Show notification
                QtWidgets.QMessageBox.information(
                    self, 
                    "🎉 User Baru Terdeteksi!", 
                    f"<b>{new_users} user baru</b> telah mendaftar!<br><br>"
                    f"Tabel telah diperbarui secara otomatis."
                )
                
                # Reset status after 3 seconds
                QtCore.QTimer.singleShot(3000, self.reset_status_message)
                
        except Exception as e:
            self.add_log(f"❌ Error saat auto-check: {str(e)}")
            
    def reset_status_message(self):
        """Reset status message ke normal."""
        if self.auto_refresh_enabled:
            self.status_label.setText("🟢 Auto-monitoring aktif - Menunggu user baru...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #059669; font-weight: 600; padding: 14px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #ecfdf5, stop:1 #d1fae5);
                    border-radius: 8px; margin: 4px 0;
                    border-left: 4px solid #059669;
                    font-size: 13px;
                }
            """)
            
    def manual_refresh(self):
        """Refresh manual oleh admin."""
        self.add_log("🔄 Refresh manual oleh admin")
        self.log_admin_activity("MANUAL_REFRESH", "Performed manual refresh of user data")
        self.load_users()
        self.load_monitoring_data()
        
    def copy_selected_rows(self):
        """Salin baris terpilih ke clipboard."""
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QtWidgets.QMessageBox.information(self, "Info", "Pilih minimal satu baris.")
            return
            
        lines = []
        for idx in sel:
            rid = self.table.item(idx.row(), 0).text()
            uname = self.table.item(idx.row(), 1).text()
            role = self.table.item(idx.row(), 2).text()
            status = self.table.item(idx.row(), 3).text()
            lines.append(f"{rid}\t{uname}\t{role}\t{status}")
            
        QtWidgets.QApplication.clipboard().setText("\n".join(lines))
        QtWidgets.QMessageBox.information(self, "✅ Copied", "Data user sudah disalin ke clipboard.")
        self.add_log(f"📋 Data {len(sel)} user disalin ke clipboard")
        
        # Log copy action
        copied_users = [self.table.item(idx.row(), 1).text() for idx in sel]
        self.log_admin_activity("COPY_USER_DATA", f"Copied data for users: {', '.join(copied_users)}")
        
    def add_log(self, message):
        """Tambahkan pesan ke log aktivitas."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        
        # Auto scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def open_database_manager(self):
        """Open Database Manager window"""
        try:
            from admin_database_manager import DatabaseManagerWindow
            
            self.db_manager = DatabaseManagerWindow(self.username, self)
            self.db_manager.show()
            
            self.add_log("🗄️ Database Manager dibuka")
            self.log_admin_activity("OPEN_DB_MANAGER", "Opened Database Manager")
            
        except ImportError as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Import Error", 
                f"Failed to import Database Manager:\n{str(e)}\n\n"
                "Make sure 'admin_database_manager.py' is in the same directory."
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to open Database Manager:\n{str(e)}"
            )
        
    def closeEvent(self, event):
        """Override close event untuk stop timer dan log logout."""
        self.stop_auto_refresh()
        self.add_log("🔴 Enhanced Admin dashboard V2 ditutup")
        self.log_admin_activity("ADMIN_LOGOUT", f"Admin {self.username} logged out from dashboard")
        event.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = EnhancedAdminDashboardV2("admin")
    window.show()
    
    sys.exit(app.exec_())
