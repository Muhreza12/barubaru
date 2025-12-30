# admin_database_manager.py — Comprehensive Database Manager for Admin
"""
🗄️ Full-Featured Database Management Interface for Crypto Insight Admin
Features:
- Database Explorer (browse all tables)
- SQL Query Runner (execute custom queries)
- User Management (CRUD operations)
- News Management (CRUD operations)
- Database Statistics & Analytics
- Backup & Export (JSON, CSV)
- Database Health Monitoring
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from app_db_fixed import connect
import json
import csv
import datetime
import hashlib
from typing import Optional, List, Tuple

class DatabaseManagerWindow(QtWidgets.QMainWindow):
    """Main Database Manager Window for Admin"""
    
    def __init__(self, admin_username: str, parent=None):
        super().__init__(parent)
        self.admin_username = admin_username
        
        self.setWindowTitle("🗄️ Crypto Insight • Database Manager")
        self.resize(1400, 900)
        
        self._setup_ui()
        self._apply_cyberpunk_style()
        self._load_initial_data()
        
    def _setup_ui(self):
        """Setup main UI with tabs"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QtWidgets.QLabel(f"🗄️ Database Manager • Admin: {self.admin_username}")
        header.setObjectName("mainHeader")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Tab Widget
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup all tabs
        self._setup_explorer_tab()
        self._setup_sql_runner_tab()
        self._setup_users_tab()
        self._setup_news_tab()
        self._setup_statistics_tab()
        self._setup_backup_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("✅ Connected to database")
        
    def _setup_explorer_tab(self):
        """Tab 1: Database Explorer"""
        explorer_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(explorer_tab)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        self.table_combo = QtWidgets.QComboBox()
        self.table_combo.addItems(["users", "news", "user_sessions", "article_likes", 
                                   "article_bookmarks", "article_views"])
        self.table_combo.setObjectName("cyberCombo")
        
        load_btn = QtWidgets.QPushButton("🔄 Load Table")
        load_btn.setObjectName("primaryBtn")
        load_btn.clicked.connect(self._load_table_data)
        
        refresh_btn = QtWidgets.QPushButton("♻️ Refresh")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.clicked.connect(self._load_table_data)
        
        controls.addWidget(QtWidgets.QLabel("Select Table:"))
        controls.addWidget(self.table_combo)
        controls.addWidget(load_btn)
        controls.addWidget(refresh_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Table view
        self.explorer_table = QtWidgets.QTableWidget()
        self.explorer_table.setAlternatingRowColors(True)
        self.explorer_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.explorer_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.explorer_table)
        
        # Info label
        self.explorer_info = QtWidgets.QLabel("Select a table and click Load")
        self.explorer_info.setObjectName("infoLabel")
        layout.addWidget(self.explorer_info)
        
        self.tab_widget.addTab(explorer_tab, "🔍 Database Explorer")
        
    def _setup_sql_runner_tab(self):
        """Tab 2: SQL Query Runner"""
        sql_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(sql_tab)
        
        # Query input
        query_label = QtWidgets.QLabel("📝 SQL Query:")
        query_label.setObjectName("sectionLabel")
        layout.addWidget(query_label)
        
        self.sql_input = QtWidgets.QTextEdit()
        self.sql_input.setObjectName("sqlInput")
        self.sql_input.setPlaceholderText("Enter SQL query here...\nExample: SELECT * FROM users WHERE role = 'admin';")
        self.sql_input.setMaximumHeight(150)
        layout.addWidget(self.sql_input)
        
        # Quick query buttons
        quick_queries = QtWidgets.QHBoxLayout()
        
        btn1 = QtWidgets.QPushButton("All Users")
        btn1.clicked.connect(lambda: self.sql_input.setText("SELECT * FROM users;"))
        
        btn2 = QtWidgets.QPushButton("All News")
        btn2.clicked.connect(lambda: self.sql_input.setText("SELECT * FROM news;"))
        
        btn3 = QtWidgets.QPushButton("Active Sessions")
        btn3.clicked.connect(lambda: self.sql_input.setText("SELECT * FROM user_sessions WHERE status = 'online';"))
        
        btn4 = QtWidgets.QPushButton("User Count by Role")
        btn4.clicked.connect(lambda: self.sql_input.setText("SELECT role, COUNT(*) as count FROM users GROUP BY role;"))
        
        for btn in [btn1, btn2, btn3, btn4]:
            btn.setObjectName("quickBtn")
            quick_queries.addWidget(btn)
        
        quick_queries.addStretch()
        layout.addLayout(quick_queries)
        
        # Execute button
        execute_btn = QtWidgets.QPushButton("⚡ Execute Query")
        execute_btn.setObjectName("primaryBtn")
        execute_btn.clicked.connect(self._execute_sql_query)
        layout.addWidget(execute_btn)
        
        # Results table
        results_label = QtWidgets.QLabel("📊 Query Results:")
        results_label.setObjectName("sectionLabel")
        layout.addWidget(results_label)
        
        self.sql_results_table = QtWidgets.QTableWidget()
        self.sql_results_table.setAlternatingRowColors(True)
        layout.addWidget(self.sql_results_table)
        
        # Status
        self.sql_status = QtWidgets.QLabel("Ready to execute query")
        self.sql_status.setObjectName("infoLabel")
        layout.addWidget(self.sql_status)
        
        self.tab_widget.addTab(sql_tab, "⚡ SQL Runner")
        
    def _setup_users_tab(self):
        """Tab 3: User Management"""
        users_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(users_tab)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        add_user_btn = QtWidgets.QPushButton("➕ Add User")
        add_user_btn.setObjectName("primaryBtn")
        add_user_btn.clicked.connect(self._add_user_dialog)
        
        edit_user_btn = QtWidgets.QPushButton("✏️ Edit User")
        edit_user_btn.setObjectName("secondaryBtn")
        edit_user_btn.clicked.connect(self._edit_user_dialog)
        
        delete_user_btn = QtWidgets.QPushButton("🗑️ Delete User")
        delete_user_btn.setObjectName("dangerBtn")
        delete_user_btn.clicked.connect(self._delete_user)
        
        refresh_users_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_users_btn.setObjectName("secondaryBtn")
        refresh_users_btn.clicked.connect(self._load_users)
        
        controls.addWidget(add_user_btn)
        controls.addWidget(edit_user_btn)
        controls.addWidget(delete_user_btn)
        controls.addWidget(refresh_users_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Users table
        self.users_table = QtWidgets.QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Actions"])
        self.users_table.setAlternatingRowColors(True)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.users_table)
        
        self.tab_widget.addTab(users_tab, "👥 User Management")
        
    def _setup_news_tab(self):
        """Tab 4: News Management"""
        news_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(news_tab)
        
        # Controls
        controls = QtWidgets.QHBoxLayout()
        
        add_news_btn = QtWidgets.QPushButton("➕ Add News")
        add_news_btn.setObjectName("primaryBtn")
        add_news_btn.clicked.connect(self._add_news_dialog)
        
        view_news_btn = QtWidgets.QPushButton("👁️ View News")
        view_news_btn.setObjectName("secondaryBtn")
        view_news_btn.clicked.connect(self._view_news_dialog)
        
        delete_news_btn = QtWidgets.QPushButton("🗑️ Delete News")
        delete_news_btn.setObjectName("dangerBtn")
        delete_news_btn.clicked.connect(self._delete_news)
        
        refresh_news_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_news_btn.setObjectName("secondaryBtn")
        refresh_news_btn.clicked.connect(self._load_news)
        
        controls.addWidget(add_news_btn)
        controls.addWidget(view_news_btn)
        controls.addWidget(delete_news_btn)
        controls.addWidget(refresh_news_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # News table
        self.news_table = QtWidgets.QTableWidget()
        self.news_table.setColumnCount(6)
        self.news_table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status", "Views", "Created"])
        self.news_table.setAlternatingRowColors(True)
        self.news_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.news_table)
        
        self.tab_widget.addTab(news_tab, "📰 News Management")
        
    def _setup_statistics_tab(self):
        """Tab 5: Database Statistics"""
        stats_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(stats_tab)
        
        # Refresh button
        refresh_stats_btn = QtWidgets.QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.setObjectName("primaryBtn")
        refresh_stats_btn.clicked.connect(self._load_statistics)
        layout.addWidget(refresh_stats_btn)
        
        # Stats display
        self.stats_text = QtWidgets.QTextEdit()
        self.stats_text.setObjectName("statsDisplay")
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QtGui.QFont("Consolas", 10))
        layout.addWidget(self.stats_text)
        
        self.tab_widget.addTab(stats_tab, "📊 Statistics")
        
    def _setup_backup_tab(self):
        """Tab 6: Backup & Export"""
        backup_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(backup_tab)
        
        # Export options
        export_group = QtWidgets.QGroupBox("📤 Export Data")
        export_layout = QtWidgets.QVBoxLayout(export_group)
        
        export_json_btn = QtWidgets.QPushButton("💾 Export All to JSON")
        export_json_btn.setObjectName("primaryBtn")
        export_json_btn.clicked.connect(self._export_to_json)
        
        export_csv_users_btn = QtWidgets.QPushButton("📊 Export Users to CSV")
        export_csv_users_btn.setObjectName("secondaryBtn")
        export_csv_users_btn.clicked.connect(lambda: self._export_to_csv("users"))
        
        export_csv_news_btn = QtWidgets.QPushButton("📊 Export News to CSV")
        export_csv_news_btn.setObjectName("secondaryBtn")
        export_csv_news_btn.clicked.connect(lambda: self._export_to_csv("news"))
        
        export_layout.addWidget(export_json_btn)
        export_layout.addWidget(export_csv_users_btn)
        export_layout.addWidget(export_csv_news_btn)
        
        layout.addWidget(export_group)
        
        # Database health
        health_group = QtWidgets.QGroupBox("🏥 Database Health")
        health_layout = QtWidgets.QVBoxLayout(health_group)
        
        check_health_btn = QtWidgets.QPushButton("🔍 Check Database Health")
        check_health_btn.setObjectName("primaryBtn")
        check_health_btn.clicked.connect(self._check_database_health)
        
        self.health_display = QtWidgets.QTextEdit()
        self.health_display.setObjectName("healthDisplay")
        self.health_display.setReadOnly(True)
        self.health_display.setMaximumHeight(200)
        
        health_layout.addWidget(check_health_btn)
        health_layout.addWidget(self.health_display)
        
        layout.addWidget(health_group)
        layout.addStretch()
        
        self.tab_widget.addTab(backup_tab, "💾 Backup & Health")
        
    def _load_initial_data(self):
        """Load initial data for all tabs"""
        self._load_users()
        self._load_news()
        self._load_statistics()
        
    # ==================== Database Explorer ====================
    
    def _load_table_data(self):
        """Load data from selected table"""
        table_name = self.table_combo.currentText()
        
        try:
            conn, _ = connect()
            if not conn:
                self.explorer_info.setText("❌ Failed to connect to database")
                return
                
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            rows = cur.fetchall()
            
            # Get column names
            col_names = [desc[0] for desc in cur.description]
            
            conn.close()
            
            # Display in table
            self.explorer_table.setRowCount(len(rows))
            self.explorer_table.setColumnCount(len(col_names))
            self.explorer_table.setHorizontalHeaderLabels(col_names)
            
            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(cell_data) if cell_data is not None else "NULL")
                    self.explorer_table.setItem(row_idx, col_idx, item)
            
            self.explorer_table.resizeColumnsToContents()
            self.explorer_info.setText(f"✅ Loaded {len(rows)} rows from '{table_name}'")
            
        except Exception as e:
            self.explorer_info.setText(f"❌ Error: {str(e)}")
            
    # ==================== SQL Runner ====================
    
    def _execute_sql_query(self):
        """Execute custom SQL query"""
        query = self.sql_input.toPlainText().strip()
        
        if not query:
            self.sql_status.setText("❌ Please enter a query")
            return
            
        try:
            conn, _ = connect()
            if not conn:
                self.sql_status.setText("❌ Failed to connect to database")
                return
                
            cur = conn.cursor()
            cur.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                col_names = [desc[0] for desc in cur.description]
                
                # Display results
                self.sql_results_table.setRowCount(len(rows))
                self.sql_results_table.setColumnCount(len(col_names))
                self.sql_results_table.setHorizontalHeaderLabels(col_names)
                
                for row_idx, row_data in enumerate(rows):
                    for col_idx, cell_data in enumerate(row_data):
                        item = QtWidgets.QTableWidgetItem(str(cell_data) if cell_data is not None else "NULL")
                        self.sql_results_table.setItem(row_idx, col_idx, item)
                
                self.sql_results_table.resizeColumnsToContents()
                self.sql_status.setText(f"✅ Query executed successfully. {len(rows)} rows returned.")
            else:
                conn.commit()
                self.sql_status.setText(f"✅ Query executed successfully. Rows affected: {cur.rowcount}")
                
            conn.close()
            
        except Exception as e:
            self.sql_status.setText(f"❌ Error: {str(e)}")
            
    # ==================== User Management ====================
    
    def _load_users(self):
        """Load all users"""
        try:
            conn, _ = connect()
            if not conn:
                return
                
            cur = conn.cursor()
            cur.execute("SELECT id, username, role FROM users ORDER BY id DESC")
            rows = cur.fetchall()
            conn.close()
            
            self.users_table.setRowCount(len(rows))
            
            for row_idx, (uid, username, role) in enumerate(rows):
                self.users_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(uid)))
                self.users_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(username))
                self.users_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(role))
                self.users_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(f"User #{uid}"))
            
            self.users_table.resizeColumnsToContents()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
            
    def _add_user_dialog(self):
        """Show dialog to add new user"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("➕ Add New User")
        dialog.resize(400, 250)
        
        layout = QtWidgets.QFormLayout(dialog)
        
        username_input = QtWidgets.QLineEdit()
        password_input = QtWidgets.QLineEdit()
        password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        role_combo = QtWidgets.QComboBox()
        role_combo.addItems(["user", "penerbit", "admin"])
        
        layout.addRow("Username:", username_input)
        layout.addRow("Password:", password_input)
        layout.addRow("Role:", role_combo)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            username = username_input.text().strip()
            password = password_input.text()
            role = role_combo.currentText()
            
            if not username or not password:
                QtWidgets.QMessageBox.warning(self, "Warning", "Username and password are required!")
                return
                
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                hashed = hashlib.sha256(password.encode()).hexdigest()
                cur.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed, role)
                )
                conn.commit()
                conn.close()
                
                QtWidgets.QMessageBox.information(self, "Success", f"User '{username}' added successfully!")
                self._load_users()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")
                
    def _edit_user_dialog(self):
        """Show dialog to edit selected user"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a user to edit!")
            return
            
        user_id = self.users_table.item(selected_row, 0).text()
        username = self.users_table.item(selected_row, 1).text()
        current_role = self.users_table.item(selected_row, 2).text()
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"✏️ Edit User: {username}")
        dialog.resize(400, 200)
        
        layout = QtWidgets.QFormLayout(dialog)
        
        role_combo = QtWidgets.QComboBox()
        role_combo.addItems(["user", "penerbit", "admin"])
        role_combo.setCurrentText(current_role)
        
        new_password_input = QtWidgets.QLineEdit()
        new_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        new_password_input.setPlaceholderText("Leave empty to keep current password")
        
        layout.addRow("Username:", QtWidgets.QLabel(username))
        layout.addRow("Role:", role_combo)
        layout.addRow("New Password:", new_password_input)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_role = role_combo.currentText()
            new_password = new_password_input.text()
            
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                
                if new_password:
                    hashed = hashlib.sha256(new_password.encode()).hexdigest()
                    cur.execute(
                        "UPDATE users SET role = %s, password = %s WHERE id = %s",
                        (new_role, hashed, user_id)
                    )
                else:
                    cur.execute(
                        "UPDATE users SET role = %s WHERE id = %s",
                        (new_role, user_id)
                    )
                
                conn.commit()
                conn.close()
                
                QtWidgets.QMessageBox.information(self, "Success", f"User '{username}' updated successfully!")
                self._load_users()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")
                
    def _delete_user(self):
        """Delete selected user"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a user to delete!")
            return
            
        user_id = self.users_table.item(selected_row, 0).text()
        username = self.users_table.item(selected_row, 1).text()
        
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?\n\nThis action cannot be undone!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                conn.close()
                
                QtWidgets.QMessageBox.information(self, "Success", f"User '{username}' deleted successfully!")
                self._load_users()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
                
    # ==================== News Management ====================
    
    def _load_news(self):
        """Load all news"""
        try:
            conn, _ = connect()
            if not conn:
                return
                
            cur = conn.cursor()
            cur.execute("""
                SELECT id, title, author, status, 
                       COALESCE(views, 0) as views,
                       to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI') as created
                FROM news 
                ORDER BY created_at DESC
                LIMIT 100
            """)
            rows = cur.fetchall()
            conn.close()
            
            self.news_table.setRowCount(len(rows))
            
            for row_idx, (nid, title, author, status, views, created) in enumerate(rows):
                self.news_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(nid)))
                self.news_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(title))
                self.news_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(author))
                self.news_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(status))
                self.news_table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(str(views)))
                self.news_table.setItem(row_idx, 5, QtWidgets.QTableWidgetItem(created))
            
            self.news_table.resizeColumnsToContents()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load news: {str(e)}")
            
    def _add_news_dialog(self):
        """Show dialog to add new news"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("➕ Add New News")
        dialog.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        form = QtWidgets.QFormLayout()
        
        title_input = QtWidgets.QLineEdit()
        author_input = QtWidgets.QLineEdit()
        author_input.setText(self.admin_username)
        
        content_input = QtWidgets.QTextEdit()
        content_input.setPlaceholderText("Enter news content here...")
        
        status_combo = QtWidgets.QComboBox()
        status_combo.addItems(["draft", "published"])
        
        form.addRow("Title:", title_input)
        form.addRow("Author:", author_input)
        form.addRow("Status:", status_combo)
        
        layout.addLayout(form)
        layout.addWidget(QtWidgets.QLabel("Content:"))
        layout.addWidget(content_input)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            title = title_input.text().strip()
            author = author_input.text().strip()
            content = content_input.toPlainText().strip()
            status = status_combo.currentText()
            
            if not title or not content:
                QtWidgets.QMessageBox.warning(self, "Warning", "Title and content are required!")
                return
                
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO news (title, content, author, status) VALUES (%s, %s, %s, %s)",
                    (title, content, author, status)
                )
                conn.commit()
                conn.close()
                
                QtWidgets.QMessageBox.information(self, "Success", "News added successfully!")
                self._load_news()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add news: {str(e)}")
                
    def _view_news_dialog(self):
        """View selected news"""
        selected_row = self.news_table.currentRow()
        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a news to view!")
            return
            
        news_id = self.news_table.item(selected_row, 0).text()
        
        try:
            conn, _ = connect()
            if not conn:
                return
                
            cur = conn.cursor()
            cur.execute("SELECT title, content, author, status FROM news WHERE id = %s", (news_id,))
            row = cur.fetchone()
            conn.close()
            
            if row:
                title, content, author, status = row
                
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle(f"👁️ View News: {title}")
                dialog.resize(700, 500)
                
                layout = QtWidgets.QVBoxLayout(dialog)
                
                info = QtWidgets.QLabel(f"<b>Author:</b> {author} | <b>Status:</b> {status}")
                layout.addWidget(info)
                
                content_display = QtWidgets.QTextEdit()
                content_display.setPlainText(content)
                content_display.setReadOnly(True)
                layout.addWidget(content_display)
                
                close_btn = QtWidgets.QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)
                
                dialog.exec_()
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load news: {str(e)}")
            
    def _delete_news(self):
        """Delete selected news"""
        selected_row = self.news_table.currentRow()
        if selected_row < 0:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a news to delete!")
            return
            
        news_id = self.news_table.item(selected_row, 0).text()
        title = self.news_table.item(selected_row, 1).text()
        
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete news '{title}'?\n\nThis action cannot be undone!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                cur.execute("DELETE FROM news WHERE id = %s", (news_id,))
                conn.commit()
                conn.close()
                
                QtWidgets.QMessageBox.information(self, "Success", "News deleted successfully!")
                self._load_news()
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete news: {str(e)}")
                
    # ==================== Statistics ====================
    
    def _load_statistics(self):
        """Load database statistics"""
        try:
            conn, _ = connect()
            if not conn:
                self.stats_text.setPlainText("❌ Failed to connect to database")
                return
                
            cur = conn.cursor()
            
            stats = f"""
╔══════════════════════════════════════════════════════════════╗
║        🗄️ CRYPTO INSIGHT DATABASE STATISTICS 🗄️            ║
╚══════════════════════════════════════════════════════════════╝

📅 Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Admin: {self.admin_username}

════════════════════════════════════════════════════════════════

📊 USERS
"""
            
            # User stats
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]
            
            cur.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            role_counts = cur.fetchall()
            
            stats += f"   Total Users: {total_users}\n"
            for role, count in role_counts:
                stats += f"   • {role}: {count}\n"
            
            # News stats
            stats += "\n📰 NEWS\n"
            cur.execute("SELECT COUNT(*) FROM news")
            total_news = cur.fetchone()[0]
            
            cur.execute("SELECT status, COUNT(*) FROM news GROUP BY status")
            status_counts = cur.fetchall()
            
            cur.execute("SELECT COALESCE(SUM(views), 0) FROM news")
            total_views = cur.fetchone()[0]
            
            stats += f"   Total Articles: {total_news}\n"
            for status, count in status_counts:
                stats += f"   • {status}: {count}\n"
            stats += f"   Total Views: {total_views}\n"
            
            # Session stats
            stats += "\n🔗 SESSIONS\n"
            cur.execute("SELECT COUNT(*) FROM user_sessions")
            total_sessions = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM user_sessions WHERE status = 'online'")
            online_sessions = cur.fetchone()[0]
            
            stats += f"   Total Sessions: {total_sessions}\n"
            stats += f"   Online Now: {online_sessions}\n"
            
            # Interaction stats (if tables exist)
            try:
                cur.execute("SELECT COUNT(*) FROM article_likes")
                total_likes = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM article_bookmarks")
                total_bookmarks = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM article_views")
                total_article_views = cur.fetchone()[0]
                
                stats += "\n💝 INTERACTIONS\n"
                stats += f"   Total Likes: {total_likes}\n"
                stats += f"   Total Bookmarks: {total_bookmarks}\n"
                stats += f"   Total Article Views: {total_article_views}\n"
            except:
                pass
            
            stats += "\n════════════════════════════════════════════════════════════════\n"
            stats += "✅ Statistics loaded successfully\n"
            
            conn.close()
            
            self.stats_text.setPlainText(stats)
            
        except Exception as e:
            self.stats_text.setPlainText(f"❌ Error loading statistics:\n\n{str(e)}")
            
    # ==================== Backup & Export ====================
    
    def _export_to_json(self):
        """Export all data to JSON"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export to JSON",
            f"crypto_insight_backup_{datetime.date.today()}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                
                # Export users
                cur.execute("SELECT id, username, role FROM users")
                users = [{"id": r[0], "username": r[1], "role": r[2]} for r in cur.fetchall()]
                
                # Export news
                cur.execute("SELECT id, title, content, author, status, created_at FROM news")
                news = [{"id": r[0], "title": r[1], "content": r[2], "author": r[3], 
                        "status": r[4], "created_at": str(r[5])} for r in cur.fetchall()]
                
                conn.close()
                
                export_data = {
                    "export_info": {
                        "exported_at": datetime.datetime.now().isoformat(),
                        "exported_by": self.admin_username,
                        "database": "Crypto Insight"
                    },
                    "users": users,
                    "news": news
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QtWidgets.QMessageBox.information(self, "Success", 
                    f"Data exported successfully to:\n{filename}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", 
                    f"Failed to export data:\n{str(e)}")
                
    def _export_to_csv(self, table_name: str):
        """Export table to CSV"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, f"Export {table_name} to CSV",
            f"{table_name}_{datetime.date.today()}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                conn, _ = connect()
                if not conn:
                    return
                    
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {table_name}")
                rows = cur.fetchall()
                col_names = [desc[0] for desc in cur.description]
                conn.close()
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(col_names)
                    writer.writerows(rows)
                
                QtWidgets.QMessageBox.information(self, "Success", 
                    f"Table '{table_name}' exported successfully to:\n{filename}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", 
                    f"Failed to export table:\n{str(e)}")
                
    def _check_database_health(self):
        """Check database health"""
        try:
            from app_db_fixed import health_check
            
            health = "🏥 DATABASE HEALTH CHECK\n"
            health += "=" * 50 + "\n\n"
            
            if health_check():
                health += "✅ Database connection: OK\n"
                
                conn, _ = connect()
                if conn:
                    cur = conn.cursor()
                    
                    # Check tables exist
                    tables = ["users", "news", "user_sessions"]
                    for table in tables:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cur.fetchone()[0]
                            health += f"✅ Table '{table}': OK ({count} rows)\n"
                        except:
                            health += f"❌ Table '{table}': MISSING\n"
                    
                    conn.close()
                    
                health += "\n" + "=" * 50 + "\n"
                health += "✅ Overall Status: HEALTHY\n"
            else:
                health += "❌ Database connection: FAILED\n"
                health += "\n❌ Overall Status: UNHEALTHY\n"
            
            self.health_display.setPlainText(health)
            
        except Exception as e:
            self.health_display.setPlainText(f"❌ Health check failed:\n\n{str(e)}")
            
    def _apply_cyberpunk_style(self):
        """Apply cyberpunk theme"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow, QWidget {
                background: #0a0a0f;
                color: #00ffff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            
            #mainHeader {
                font-size: 24px;
                font-weight: 900;
                color: #00ffff;
                padding: 15px;
                text-shadow: 0 0 10px #00ffff,
                            0 0 20px #00ffff;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 2px solid #ff00ff;
                background: rgba(10, 10, 15, 0.95);
            }
            
            QTabBar::tab {
                background: rgba(0, 0, 0, 0.5);
                color: #00ffff;
                padding: 10px 20px;
                border: 2px solid #00ffff;
                margin-right: 2px;
                font-weight: 600;
            }
            
            QTabBar::tab:selected {
                background: rgba(255, 0, 255, 0.3);
                color: #ff00ff;
                border-color: #ff00ff;
                text-shadow: 0 0 10px #ff00ff;
            }
            
            QTabBar::tab:hover {
                background: rgba(0, 255, 255, 0.2);
            }
            
            /* Buttons */
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #00ffff;
                border-radius: 0;
                color: #00ffff;
                background: rgba(0, 255, 255, 0.1);
                font-weight: 600;
                text-shadow: 0 0 5px #00ffff;
            }
            
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.2);
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
            }
            
            #primaryBtn {
                border-color: #ff00ff;
                color: #ff00ff;
                background: rgba(255, 0, 255, 0.1);
                text-shadow: 0 0 5px #ff00ff;
            }
            
            #primaryBtn:hover {
                background: rgba(255, 0, 255, 0.3);
                box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
            }
            
            #secondaryBtn {
                border-color: #00ffff;
                color: #00ffff;
            }
            
            #dangerBtn {
                border-color: #ff0055;
                color: #ff0055;
                background: rgba(255, 0, 85, 0.1);
            }
            
            #dangerBtn:hover {
                background: rgba(255, 0, 85, 0.3);
            }
            
            #quickBtn {
                padding: 5px 10px;
                font-size: 11px;
            }
            
            /* Tables */
            QTableWidget {
                background: rgba(0, 0, 0, 0.5);
                color: #00ffff;
                gridline-color: rgba(0, 255, 255, 0.2);
                border: 2px solid #00ffff;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background: rgba(255, 0, 255, 0.3);
                color: #ff00ff;
            }
            
            QHeaderView::section {
                background: rgba(0, 0, 0, 0.7);
                color: #00ffff;
                padding: 8px;
                border: 1px solid #00ffff;
                font-weight: 700;
            }
            
            /* Input Fields */
            QLineEdit, QTextEdit, QComboBox {
                background: rgba(0, 0, 0, 0.5);
                color: #00ffff;
                border: 2px solid #00ffff;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border-color: #ff00ff;
                box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);
            }
            
            #sqlInput {
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            
            #statsDisplay, #healthDisplay {
                background: rgba(0, 0, 0, 0.7);
                color: #00ffff;
                border: 2px solid #00ffff;
                font-family: 'Consolas', monospace;
            }
            
            /* Labels */
            #sectionLabel {
                color: #ff00ff;
                font-weight: 700;
                font-size: 14px;
                text-shadow: 0 0 5px #ff00ff;
                padding: 5px 0;
            }
            
            #infoLabel {
                color: #00ffff;
                padding: 5px;
                background: rgba(0, 255, 255, 0.1);
                border-left: 3px solid #00ffff;
            }
            
            /* Group Box */
            QGroupBox {
                border: 2px solid #ff00ff;
                margin-top: 10px;
                padding-top: 10px;
                color: #ff00ff;
                font-weight: 700;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            /* Status Bar */
            QStatusBar {
                background: rgba(0, 0, 0, 0.8);
                color: #00ffff;
                border-top: 2px solid #00ffff;
            }
        """)


# ==================== Standalone Test ====================

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    
    window = DatabaseManagerWindow("admin_test")
    window.show()
    
    sys.exit(app.exec_())
