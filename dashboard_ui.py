from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from app_db_fixed import *
import sys

class Dashboard(QMainWindow):
    def __init__(self, user_data, session_id):
        super().__init__()
        self.user_data = user_data
        self.session_id = session_id
        self.setWindowTitle("🔷 CRYPTO INSIGHT - DASHBOARD 🔷")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup UI
        central = QWidget()
        self.main_layout = QVBoxLayout()
        
        # Header
        self.create_header()
        
        # Navigation
        self.create_navigation()
        
        # Content
        self.stacked_widget = QStackedWidget()
        self.setup_pages()
        self.main_layout.addWidget(self.stacked_widget)
        
        central.setLayout(self.main_layout)
        self.setCentralWidget(central)
        
        # Styles
        self.apply_styles()
        
        # Load data
        self.show_dashboard()
    
    # ... (SEMUA METHOD YANG SAMA SEPERTI SEBELUMNYA)

        # ===== CRYPTO TICKER =====
        try:
            self.crypto_ticker = CryptoTicker()
            main_container.addWidget(self.crypto_ticker)
        except Exception as e:
            print(f"Ticker error: {e}")
        
        # ===== CONTENT AREA =====
        content_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        # Header
        self.create_header()
        
        # Navigation tabs
        self.create_navigation()
        
        # Content area
        self.stacked_widget = QStackedWidget()
        self.setup_pages()
        self.main_layout.addWidget(self.stacked_widget)
        
        content_widget.setLayout(self.main_layout)
        main_container.addWidget(content_widget)
        
        # Set central widget
        central = QWidget()
        central.setLayout(main_container)
        self.setCentralWidget(central)
        
        # Apply styles
        self.apply_styles()
        
        # Load initial data
        self.show_dashboard()
    
    def create_header(self):
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout()
        
        # Logo
        logo = QLabel("🔷 CRYPTO INSIGHT")
        logo.setObjectName("logo")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # User info
        user_info = QLabel(f"👤 {self.user_data['username']} | ◈ {self.user_data['role'].upper()}")
        user_info.setObjectName("userInfo")
        user_info.setFont(QFont("Consolas", 12))
        layout.addWidget(user_info)
        
        # Logout button
        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(logout_btn)
        
        header.setLayout(layout)
        self.main_layout.addWidget(header)
    
    def create_navigation(self):
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")
        nav_frame.setFixedHeight(60)
        
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        buttons_config = [
            ("📊 Dashboard", "dashboard"),
            ("📰 News", "news"),
            ("➕ Create News", "create_news"),
        ]
        
        # Add admin-only buttons
        if self.user_data['role'] == 'admin':
            buttons_config.extend([
                ("👥 Users", "users"),
                ("💻 SQL Terminal", "sql")
            ])
        
        for text, page_name in buttons_config:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, p=page_name: self.switch_page(p))
            nav_layout.addWidget(btn)
            self.nav_buttons[page_name] = btn
        
        nav_layout.addStretch()
        nav_frame.setLayout(nav_layout)
        self.main_layout.addWidget(nav_frame)
    
    def setup_pages(self):
        # Dashboard page
        self.dashboard_page = self.create_dashboard_page()
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # News page
        self.news_page = self.create_news_page()
        self.stacked_widget.addWidget(self.news_page)
        
        # Create news page
        self.create_news_page_widget = self.create_news_creation_page()
        self.stacked_widget.addWidget(self.create_news_page_widget)
        
        # Admin pages
        if self.user_data['role'] == 'admin':
            self.users_page = self.create_users_page()
            self.stacked_widget.addWidget(self.users_page)
            
            self.sql_page = self.create_sql_page()
            self.stacked_widget.addWidget(self.sql_page)
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Welcome section
        welcome = QLabel(f"Welcome back, {self.user_data['username']}! 👋")
        welcome.setFont(QFont("Arial", 18, QFont.Bold))
        welcome.setStyleSheet("color: #00ff88; padding: 20px;")
        layout.addWidget(welcome)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Total users
        users_card = self.create_stat_card("👥 Total Users", self.get_total_users())
        stats_layout.addWidget(users_card)
        
        # Total news
        news_card = self.create_stat_card("📰 Total News", self.get_total_news())
        stats_layout.addWidget(news_card)
        
        # Active sessions
        sessions_card = self.create_stat_card("🟢 Active Sessions", self.get_active_sessions())
        stats_layout.addWidget(sessions_card)
        
        # Your posts (if penerbit)
        if self.user_data['role'] in ['penerbit', 'admin']:
            my_posts_card = self.create_stat_card("📝 My Posts", self.get_my_posts_count())
            stats_layout.addWidget(my_posts_card)
        
        layout.addLayout(stats_layout)
        
        # Recent activity
        recent_label = QLabel("📋 Recent News")
        recent_label.setFont(QFont("Arial", 16, QFont.Bold))
        recent_label.setStyleSheet("color: white; padding: 20px 0 10px 0;")
        layout.addWidget(recent_label)
        
        # News list
        self.dashboard_news_list = QListWidget()
        self.dashboard_news_list.setObjectName("newsList")
        self.dashboard_news_list.itemDoubleClicked.connect(self.view_news_detail)
        self.load_recent_news(self.dashboard_news_list)
        layout.addWidget(self.dashboard_news_list)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(120)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: #888;")
        layout.addWidget(title_label)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 32, QFont.Bold))
        value_label.setStyleSheet("color: #00ff88;")
        layout.addWidget(value_label)
        
        layout.addStretch()
        card.setLayout(layout)
        return card
    
    def create_news_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📰 All News")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff88; padding: 20px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("actionBtn")
        refresh_btn.clicked.connect(lambda: self.load_all_news(self.news_list_widget))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # News list
        self.news_list_widget = QListWidget()
        self.news_list_widget.setObjectName("newsList")
        self.news_list_widget.itemDoubleClicked.connect(self.view_news_detail)
        self.load_all_news(self.news_list_widget)
        layout.addWidget(self.news_list_widget)
        
        page.setLayout(layout)
        return page
    
    def create_news_creation_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Check role
        if self.user_data['role'] not in ['penerbit', 'admin']:
            error_label = QLabel("❌ Access Denied\n\nOnly Penerbit and Admin can create news.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setFont(QFont("Arial", 16))
            error_label.setStyleSheet("color: #ff4444; padding: 50px;")
            layout.addWidget(error_label)
            page.setLayout(layout)
            return page
        
        # Title
        title = QLabel("➕ Create New Article")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff88; padding: 20px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        self.news_title_input = QLineEdit()
        self.news_title_input.setPlaceholderText("Enter news title...")
        self.news_title_input.setObjectName("formInput")
        form_layout.addRow("📝 Title:", self.news_title_input)
        
        self.news_content_input = QTextEdit()
        self.news_content_input.setPlaceholderText("Write your article content here...")
        self.news_content_input.setObjectName("formInput")
        self.news_content_input.setMinimumHeight(300)
        form_layout.addRow("📄 Content:", self.news_content_input)
        
        # Image upload
        image_layout = QHBoxLayout()
        self.news_image_path = QLineEdit()
        self.news_image_path.setPlaceholderText("No image selected")
        self.news_image_path.setReadOnly(True)
        self.news_image_path.setObjectName("formInput")
        image_layout.addWidget(self.news_image_path)
        
        upload_btn = QPushButton("📁 Choose Image")
        upload_btn.setObjectName("actionBtn")
        upload_btn.clicked.connect(self.select_image)
        upload_btn.setCursor(Qt.PointingHandCursor)
        image_layout.addWidget(upload_btn)
        
        form_layout.addRow("🖼️ Image:", image_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.clicked.connect(self.clear_news_form)
        clear_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(clear_btn)
        
        submit_btn = QPushButton("🚀 Publish News")
        submit_btn.setObjectName("submitBtn")
        submit_btn.clicked.connect(self.create_news)
        submit_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(submit_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        page.setLayout(layout)
        return page
    
    def create_users_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 User Management")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff88; padding: 20px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("actionBtn")
        refresh_btn.clicked.connect(lambda: self.load_users(self.users_table))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setObjectName("dataTable")
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Created", "Status", "Online"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.load_users(self.users_table)
        layout.addWidget(self.users_table)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ban_btn = QPushButton("🚫 Ban User")
        ban_btn.setObjectName("dangerBtn")
        ban_btn.clicked.connect(self.ban_user)
        ban_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(ban_btn)
        
        unban_btn = QPushButton("✅ Unban User")
        unban_btn.setObjectName("actionBtn")
        unban_btn.clicked.connect(self.unban_user)
        unban_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(unban_btn)
        
        layout.addLayout(btn_layout)
        
        page.setLayout(layout)
        return page
    
    def create_sql_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("💻 SQL Terminal")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00ff88; padding: 20px;")
        layout.addWidget(title)
        
        # Warning
        warning = QLabel("⚠️ WARNING: Direct database access. Use with caution!")
        warning.setStyleSheet("color: #ff8800; font-weight: bold; padding: 10px; background: rgba(255,136,0,0.1); border-radius: 5px;")
        layout.addWidget(warning)
        
        # SQL input
        input_label = QLabel("SQL Query:")
        input_label.setStyleSheet("color: white; font-weight: bold; margin-top: 20px;")
        layout.addWidget(input_label)
        
        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("SELECT * FROM users;")
        self.sql_input.setObjectName("formInput")
        self.sql_input.setMaximumHeight(150)
        self.sql_input.setFont(QFont("Consolas", 11))
        layout.addWidget(self.sql_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        execute_btn = QPushButton("▶️ Execute Query")
        execute_btn.setObjectName("submitBtn")
        execute_btn.clicked.connect(self.execute_sql)
        execute_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(execute_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setObjectName("secondaryBtn")
        clear_btn.clicked.connect(lambda: self.sql_input.clear())
        clear_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Results
        result_label = QLabel("Results:")
        result_label.setStyleSheet("color: white; font-weight: bold; margin-top: 20px;")
        layout.addWidget(result_label)
        
        self.sql_result = QTableWidget()
        self.sql_result.setObjectName("dataTable")
        layout.addWidget(self.sql_result)
        
        page.setLayout(layout)
        return page
    
    def switch_page(self, page_name):
        # Reset all button styles
        for btn in self.nav_buttons.values():
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # Set active button
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].setProperty("active", True)
            self.nav_buttons[page_name].style().unpolish(self.nav_buttons[page_name])
            self.nav_buttons[page_name].style().polish(self.nav_buttons[page_name])
        
        # Switch page
        page_index = {
            "dashboard": 0,
            "news": 1,
            "create_news": 2,
            "users": 3,
            "sql": 4
        }
        
        if page_name in page_index:
            self.stacked_widget.setCurrentIndex(page_index[page_name])
    
    def show_dashboard(self):
        self.switch_page("dashboard")
    
    # ===== DATA LOADING FUNCTIONS =====
    
    def get_total_users(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            release_connection(conn)
            return count
        except:
            return "N/A"
    
    def get_total_news(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM news")
            count = cur.fetchone()[0]
            release_connection(conn)
            return count
        except:
            return "N/A"
    
    def get_active_sessions(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM user_sessions 
                WHERE is_active = TRUE 
                AND login_time > NOW() - INTERVAL '1 hour'
            """)
            count = cur.fetchone()[0]
            release_connection(conn)
            return count
        except:
            return "N/A"
    
    def get_my_posts_count(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM news WHERE author_id = %s", (self.user_data['id'],))
            count = cur.fetchone()[0]
            release_connection(conn)
            return count
        except:
            return "N/A"
    
    def load_recent_news(self, list_widget):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT n.id, n.title, n.created_at, u.username, 
                       (SELECT COUNT(*) FROM comments WHERE news_id = n.id) as comment_count
                FROM news n
                JOIN users u ON n.author_id = u.id
                ORDER BY n.created_at DESC
                LIMIT 10
            """)
            news = cur.fetchall()
            
            list_widget.clear()
            for news_id, title, created, author, comments in news:
                item_text = f"📰 {title}\n   👤 {author} | 🕒 {created} | 💬 {comments} comments"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, news_id)
                list_widget.addItem(item)
            
            release_connection(conn)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load news: {str(e)}")
    
    def load_all_news(self, list_widget):
        self.load_recent_news(list_widget)
    
    def load_users(self, table):
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # FIX: Session dianggap online jika login dalam 1 jam terakhir DAN is_active=TRUE
            cur.execute("""
                SELECT 
                    u.id, 
                    u.username, 
                    u.role, 
                    u.created_at, 
                    u.is_banned,
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 FROM user_sessions s2
                            WHERE s2.user_id = u.id 
                            AND s2.is_active = TRUE
                            AND s2.login_time > NOW() - INTERVAL '1 hour'
                        ) THEN 1
                        ELSE 0
                    END as is_online
                FROM users u
                ORDER BY u.created_at DESC
            """)
            
            users = cur.fetchall()
            table.setRowCount(len(users))
            
            for row, (id, username, role, created, banned, is_online) in enumerate(users):
                table.setItem(row, 0, QTableWidgetItem(str(id)))
                table.setItem(row, 1, QTableWidgetItem(username))
                table.setItem(row, 2, QTableWidgetItem(f"◈ {role.upper()}"))
                table.setItem(row, 3, QTableWidgetItem(str(created)[:19]))
                
                status = "❌ BANNED" if banned else "✓ ACTIVE"
                table.setItem(row, 4, QTableWidgetItem(status))
                
                online = "🟢 ONLINE" if is_online == 1 else "⚫ OFFLINE"
                table.setItem(row, 5, QTableWidgetItem(online))
            
            release_connection(conn)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def view_news_detail(self, item):
        news_id = item.data(Qt.UserRole)
        dialog = NewsDetailDialog(news_id, self.user_data, self)
        dialog.exec_()
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            self.news_image_path.setText(file_path)
    
    def clear_news_form(self):
        self.news_title_input.clear()
        self.news_content_input.clear()
        self.news_image_path.clear()
    
    def create_news(self):
        title = self.news_title_input.text().strip()
        content = self.news_content_input.toPlainText().strip()
        image_path = self.news_image_path.text().strip()
        
        if not title or not content:
            QMessageBox.warning(self, "Warning", "Please fill in title and content!")
            return
        
        try:
            # Handle image upload
            image_data = None
            if image_path:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            
            # Insert news
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO news (title, content, author_id, image_data)
                VALUES (%s, %s, %s, %s)
            """, (title, content, self.user_data['id'], image_data))
            conn.commit()
            release_connection(conn)
            
            QMessageBox.information(self, "Success", "✅ News published successfully!")
            self.clear_news_form()
            self.load_all_news(self.news_list_widget)
            self.switch_page("news")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create news: {str(e)}")
    
    def ban_user(self):
        selected = self.users_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a user!")
            return
        
        row = selected[0].row()
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Ban", 
            f"Ban user '{username}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("UPDATE users SET is_banned = TRUE WHERE id = %s", (user_id,))
                conn.commit()
                release_connection(conn)
                
                QMessageBox.information(self, "Success", f"✅ User '{username}' banned!")
                self.load_users(self.users_table)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to ban user: {str(e)}")
    
    def unban_user(self):
        selected = self.users_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a user!")
            return
        
        row = selected[0].row()
        user_id = int(self.users_table.item(row, 0).text())
        username = self.users_table.item(row, 1).text()
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET is_banned = FALSE WHERE id = %s", (user_id,))
            conn.commit()
            release_connection(conn)
            
            QMessageBox.information(self, "Success", f"✅ User '{username}' unbanned!")
            self.load_users(self.users_table)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unban user: {str(e)}")
    
    def execute_sql(self):
        query = self.sql_input.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query!")
            return
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(query)
            
            # If SELECT query
            if query.strip().upper().startswith("SELECT"):
                results = cur.fetchall()
                if results:
                    columns = [desc[0] for desc in cur.description]
                    
                    self.sql_result.setRowCount(len(results))
                    self.sql_result.setColumnCount(len(columns))
                    self.sql_result.setHorizontalHeaderLabels(columns)
                    
                    for row, data in enumerate(results):
                        for col, value in enumerate(data):
                            self.sql_result.setItem(row, col, QTableWidgetItem(str(value)))
                    
                    self.sql_result.resizeColumnsToContents()
                else:
                    self.sql_result.setRowCount(0)
                    self.sql_result.setColumnCount(0)
                    QMessageBox.information(self, "Info", "Query executed. No results returned.")
            else:
                # For INSERT, UPDATE, DELETE
                conn.commit()
                QMessageBox.information(self, "Success", f"✅ Query executed! Rows affected: {cur.rowcount}")
                self.sql_result.setRowCount(0)
                self.sql_result.setColumnCount(0)
            
            release_connection(conn)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"SQL Error:\n{str(e)}")
    
    def logout(self):
        reply = QMessageBox.question(
            self, 
            "Logout", 
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Deactivate session
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE user_sessions 
                    SET is_active = FALSE, logout_time = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (self.session_id,))
                conn.commit()
                release_connection(conn)
            except:
                pass
            
            self.close()
            from auth_ui_cyberpunk import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
            }
            
            QFrame#header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-bottom: 3px solid #00ff88;
                padding: 10px;
            }
            
            QLabel#logo {
                color: #00ff88;
                font-weight: bold;
            }
            
            QLabel#userInfo {
                color: white;
                background: rgba(0, 255, 136, 0.1);
                padding: 8px 15px;
                border-radius: 20px;
                border: 1px solid #00ff88;
            }
            
            QPushButton#logoutBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #cc0000);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#logoutBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6666, stop:1 #ff0000);
            }
            
            QFrame#navFrame {
                background: #16213e;
                border-bottom: 2px solid #00ff88;
                padding: 10px;
            }
            
            QPushButton#navBtn {
                background: transparent;
                color: #888;
                border: 2px solid transparent;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#navBtn:hover {
                color: #00ff88;
                border: 2px solid #00ff88;
                background: rgba(0, 255, 136, 0.1);
            }
            
            QPushButton#navBtn[active="true"] {
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                border: 2px solid #00ff88;
            }
            
            QFrame#statCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: 2px solid #00ff88;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }
            
            QListWidget#newsList {
                background: #16213e;
                color: white;
                border: 2px solid #00ff88;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            
            QListWidget#newsList::item {
                padding: 15px;
                border-bottom: 1px solid #2a2a3e;
            }
            
            QListWidget#newsList::item:hover {
                background: rgba(0, 255, 136, 0.1);
                border-left: 4px solid #00ff88;
            }
            
            QLineEdit#formInput, QTextEdit#formInput {
                background: #1a1a2e;
                color: white;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
            
            QLineEdit#formInput:focus, QTextEdit#formInput:focus {
                border: 2px solid #00ff88;
            }
            
            QPushButton#actionBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#actionBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffaa, stop:1 #00ff88);
            }
            
            QPushButton#submitBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#submitBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffaa, stop:1 #00ff88);
            }
            
            QPushButton#secondaryBtn {
                background: #444;
                color: white;
                border: 2px solid #666;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#secondaryBtn:hover {
                background: #555;
                border: 2px solid #00ff88;
            }
            
            QPushButton#dangerBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff4444, stop:1 #cc0000);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#dangerBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6666, stop:1 #ff0000);
            }
            
            QTableWidget#dataTable {
                background: #16213e;
                color: white;
                gridline-color: #2a2a3e;
                border: 2px solid #00ff88;
                border-radius: 5px;
            }
            
            QTableWidget#dataTable::item {
                padding: 8px;
            }
            
            QTableWidget#dataTable::item:selected {
                background: rgba(0, 255, 136, 0.2);
            }
            
            QHeaderView::section {
                background: #1a1a2e;
                color: #00ff88;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #00ff88;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #00ffaa;
            }
        """)


class NewsDetailDialog(QDialog):
    def __init__(self, news_id, user_data, parent=None):
        super().__init__(parent)
        self.news_id = news_id
        self.user_data = user_data
        self.setWindowTitle("📰 News Detail")
        self.setGeometry(200, 100, 900, 700)
        self.setup_ui()
        self.load_news()
        self.apply_styles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Scroll area for news content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("newsScroll")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Title
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #00ff88; padding: 15px;")
        content_layout.addWidget(self.title_label)
        
        # Meta info
        self.meta_label = QLabel()
        self.meta_label.setFont(QFont("Consolas", 10))
        self.meta_label.setStyleSheet("color: #888; padding: 5px 15px;")
        content_layout.addWidget(self.meta_label)
        
        # Image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMaximumHeight(400)
        self.image_label.setScaledContents(False)
        content_layout.addWidget(self.image_label)
        
        # Content
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont("Arial", 12))
        self.content_label.setStyleSheet("color: white; padding: 15px; line-height: 1.6;")
        content_layout.addWidget(self.content_label)
        
        # Comments section
        comments_title = QLabel("💬 Comments")
        comments_title.setFont(QFont("Arial", 14, QFont.Bold))
        comments_title.setStyleSheet("color: #00ff88; padding: 20px 15px 10px 15px;")
        content_layout.addWidget(comments_title)
        
        self.comments_list = QListWidget()
        self.comments_list.setObjectName("commentsList")
        self.comments_list.setMaximumHeight(200)
        content_layout.addWidget(self.comments_list)
        
        # Add comment
        comment_layout = QHBoxLayout()
        
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Write a comment...")
        self.comment_input.setObjectName("commentInput")
        comment_layout.addWidget(self.comment_input)
        
        send_btn = QPushButton("📤 Send")
        send_btn.setObjectName("sendBtn")
        send_btn.clicked.connect(self.add_comment)
        send_btn.setCursor(Qt.PointingHandCursor)
        comment_layout.addWidget(send_btn)
        
        content_layout.addLayout(comment_layout)
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("✖️ Close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def load_news(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Load news
            cur.execute("""
                SELECT n.title, n.content, n.created_at, n.image_data, u.username
                FROM news n
                JOIN users u ON n.author_id = u.id
                WHERE n.id = %s
            """, (self.news_id,))
            
            news = cur.fetchone()
            if news:
                title, content, created, image_data, author = news
                
                self.title_label.setText(title)
                self.meta_label.setText(f"👤 By {author} | 🕒 {created}")
                self.content_label.setText(content)
                
                # Load image if exists
                if image_data:
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    scaled = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled)
            
            # Load comments
            cur.execute("""
                SELECT c.comment_text, c.created_at, u.username
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.news_id = %s
                ORDER BY c.created_at DESC
            """, (self.news_id,))
            
            comments = cur.fetchall()
            self.comments_list.clear()
            
            for comment_text, created, username in comments:
                item_text = f"👤 {username} - {created}\n{comment_text}"
                item = QListWidgetItem(item_text)
                self.comments_list.addItem(item)
            
            release_connection(conn)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load news: {str(e)}")
    
    def add_comment(self):
        comment_text = self.comment_input.text().strip()
        
        if not comment_text:
            QMessageBox.warning(self, "Warning", "Comment cannot be empty!")
            return
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO comments (news_id, user_id, comment_text)
                VALUES (%s, %s, %s)
            """, (self.news_id, self.user_data['id'], comment_text))
            conn.commit()
            release_connection(conn)
            
            self.comment_input.clear()
            self.load_news()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add comment: {str(e)}")
    
    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
            }
            
            QScrollArea#newsScroll {
                border: 2px solid #00ff88;
                border-radius: 5px;
                background: #16213e;
            }
            
            QListWidget#commentsList {
                background: #1a1a2e;
                color: white;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            
            QListWidget#commentsList::item {
                padding: 10px;
                border-bottom: 1px solid #2a2a3e;
            }
            
            QLineEdit#commentInput {
                background: #1a1a2e;
                color: white;
                border: 2px solid #444;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 13px;
            }
            
            QLineEdit#commentInput:focus {
                border: 2px solid #00ff88;
            }
            
            QPushButton#sendBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 #00cc66);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 20px;
                font-weight: bold;
            }
            
            QPushButton#sendBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffaa, stop:1 #00ff88);
            }
            
            QPushButton#closeBtn {
                background: #444;
                color: white;
                border: 2px solid #666;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#closeBtn:hover {
                background: #555;
                border: 2px solid #ff4444;
                color: #ff4444;
            }
        """)
# ===== CRYPTO TICKER (DISABLED) =====
# try:
#     self.crypto_ticker = CryptoTicker()
#     main_container.addWidget(self.crypto_ticker)
# except Exception as e:
#     print(f"Ticker error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test data
    test_user = {
        'id': 1,
        'username': 'admin',
        'role': 'admin'
    }
    
    window = Dashboard(test_user, 'test-session-123')
    window.show()
    sys.exit(app.exec_())
