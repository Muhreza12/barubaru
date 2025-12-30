# penerbit_dashboard.py — CYBERPUNK STYLE WITH COMPACT IMAGE UPLOAD 🎮📸
"""
🔮 CYBERPUNK PENERBIT DASHBOARD WITH COMPACT IMAGE UPLOAD 🔮

Features:
- Neon glow effects
- Holographic UI elements  
- Futuristic cyberpunk theme
- COMPACT image upload with small thumbnail preview
- Auto resize large images
- Support JPEG, PNG, GIF, BMP
"""

import os
import io
from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QImage

from app_db_fixed import (
    heartbeat, end_session, 
    create_news, create_news_with_image, 
    list_my_news_with_images, list_published_news
)

# Import Pillow for image processing
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ Pillow not installed. Image upload will have limited functionality.")
    print("   Run: pip install Pillow")

# 🎨 CYBERPUNK COLOR PALETTE
CYBER_CYAN = "#00ffff"
CYBER_MAGENTA = "#ff00ff"
CYBER_PURPLE = "#9d00ff"
CYBER_PINK = "#ff007f"
CYBER_BLUE = "#0066ff"
CYBER_GREEN = "#00ff88"
CYBER_YELLOW = "#ffff00"
CYBER_RED = "#ff0040"
CYBER_DARK = "#0a0a0f"
CYBER_DARKER = "#050508"
CYBER_GRID = "#1a1a2e"

# Image settings
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_WIDTH = 1920
IMAGE_QUALITY = 85


class CyberStatCard(QtWidgets.QFrame):
    """Cyberpunk glowing stat card with neon effects"""
    
    def __init__(self, title, value, icon, glow_color, parent=None):
        super().__init__(parent)
        self.glow_color = glow_color
        self.setObjectName("cyberStatCard")
        self.setFixedHeight(140)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Icon with glow
        icon_label = QtWidgets.QLabel(icon)
        icon_label.setObjectName("cyberIcon")
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 42px;
            color: {glow_color};
            text-shadow: 0 0 20px {glow_color},
                         0 0 40px {glow_color},
                         0 0 60px {glow_color};
        """)
        layout.addWidget(icon_label)
        
        # Value with glow
        self.value_label = QtWidgets.QLabel(str(value))
        self.value_label.setObjectName("cyberValue")
        self.value_label.setAlignment(QtCore.Qt.AlignCenter)
        self.value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 900;
            color: {glow_color};
            text-shadow: 0 0 10px {glow_color},
                         0 0 20px {glow_color};
        """)
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("cyberTitle")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {glow_color};
            text-transform: uppercase;
            letter-spacing: 2px;
        """)
        layout.addWidget(title_label)
        
        # Apply glow effect to card
        self.setStyleSheet(f"""
            #cyberStatCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {CYBER_DARKER},
                    stop:1 {CYBER_DARK});
                border: 2px solid {glow_color};
                border-radius: 15px;
            }}
            #cyberStatCard:hover {{
                box-shadow: 0 0 30px {glow_color}60;
            }}
        """)
    
    def update_value(self, value):
        """Update card value"""
        self.value_label.setText(str(value))


class CyberButton(QtWidgets.QPushButton):
    """Cyberpunk style button with glow"""
    
    def __init__(self, text, color=CYBER_CYAN, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._apply_cyber_style()
    
    def _apply_cyber_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_DARKER},
                    stop:1 {CYBER_DARK});
                color: {self.color};
                border: 2px solid {self.color};
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {self.color}20;
                box-shadow: 0 0 20px {self.color},
                            0 0 40px {self.color}80;
            }}
            QPushButton:pressed {{
                background: {self.color}40;
            }}
            QPushButton:disabled {{
                background: {CYBER_DARKER};
                color: {self.color}40;
                border: 2px solid {self.color}40;
            }}
        """)


class CyberTextEdit(QtWidgets.QTextEdit):
    """Cyberpunk text editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cyberEditor")
        self.setPlaceholderText("⚡ ENTER YOUR ARTICLE CONTENT HERE ⚡")
        
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 12px;
                padding: 16px;
                font-size: 15px;
                font-family: 'Consolas', 'Courier New', monospace;
                selection-background-color: {CYBER_CYAN}40;
            }}
            QTextEdit:focus {{
                border: 2px solid {CYBER_CYAN};
                box-shadow: 0 0 20px {CYBER_CYAN}60;
            }}
        """)


class PenerbitDashboard(QtWidgets.QMainWindow):
    """🎮 CYBERPUNK PENERBIT DASHBOARD WITH COMPACT IMAGE UPLOAD 🎮"""
    
    def __init__(self, username: str, session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        # Image upload state
        self.current_image_data = None
        self.current_image_filename = None
        self.current_image_mimetype = None
        
        self.setWindowTitle(f"⚡ CRYPTO INSIGHT — CYBERPUNK EDITION ⚡")
        self.resize(1500, 950)
        
        self._setup_ui()
        self._apply_cyberpunk_theme()
        self._load_statistics()
        self._load_my_articles()
        
        # Heartbeat
        if self.session_id:
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(self.session_id))
            self.hb_timer.start(20000)
        
        # Auto-refresh
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._load_statistics)
        self.refresh_timer.start(30000)
    
    def _setup_ui(self):
        """Setup CYBERPUNK UI"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # 🎮 CYBER HEADER
        header = self._create_cyber_header()
        main_layout.addWidget(header)
        
        # 📊 GLOWING STATS
        stats = self._create_cyber_stats()
        main_layout.addLayout(stats)
        
        # 📝 CYBER TABS
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("cyberTabs")
        
        # Tab 1: Create Article
        tab_create = self._create_article_tab()
        self.tabs.addTab(tab_create, "⚡ CREATE ARTICLE")
        
        # Tab 2: My Articles
        tab_articles = self._create_articles_tab()
        self.tabs.addTab(tab_articles, "📡 MY ARTICLES")
        
        # Tab 3: Published Feed
        tab_feed = self._create_feed_tab()
        self.tabs.addTab(tab_feed, "🌐 PUBLISHED FEED")
        
        main_layout.addWidget(self.tabs)
    
    def _create_cyber_header(self):
        """Create cyberpunk header"""
        header = QtWidgets.QFrame()
        header.setObjectName("cyberHeader")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with glow
        title = QtWidgets.QLabel(f"⚡ WELCOME {self.username.upper()} ⚡")
        title.setObjectName("cyberHeaderTitle")
        
        subtitle = QtWidgets.QLabel("► PENERBIT CONTROL CENTER ◄")
        subtitle.setObjectName("cyberHeaderSubtitle")
        
        title_layout = QtWidgets.QVBoxLayout()
        title_layout.setSpacing(5)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Logout button
        self.btn_logout = CyberButton("LOGOUT", CYBER_RED)
        self.btn_logout.clicked.connect(self._logout)
        layout.addWidget(self.btn_logout)
        
        return header
    
    def _create_cyber_stats(self):
        """Create glowing statistics cards"""
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(20)
        
        # Cyber stat cards with different glow colors
        self.card_total = CyberStatCard("TOTAL", "0", "📡", CYBER_CYAN)
        self.card_published = CyberStatCard("LIVE", "0", "✨", CYBER_GREEN)
        self.card_draft = CyberStatCard("DRAFT", "0", "💾", CYBER_YELLOW)
        self.card_with_images = CyberStatCard("IMAGES", "0", "🖼️", CYBER_MAGENTA)
        
        row.addWidget(self.card_total)
        row.addWidget(self.card_published)
        row.addWidget(self.card_draft)
        row.addWidget(self.card_with_images)
        
        return row
    
    def _create_article_tab(self):
        """Create article editor with COMPACT IMAGE UPLOAD"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(20)
        
        # Title input
        title_label = QtWidgets.QLabel("⚡ ARTICLE TITLE")
        title_label.setStyleSheet(f"""
            color: {CYBER_CYAN};
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        
        self.input_title = QtWidgets.QLineEdit()
        self.input_title.setObjectName("cyberTitleInput")
        self.input_title.setPlaceholderText("Enter cyberpunk title...")
        self.input_title.setMinimumHeight(55)
        
        layout.addWidget(title_label)
        layout.addWidget(self.input_title)
        
        # === IMAGE UPLOAD SECTION - COMPACT THUMBNAIL ===
        image_section = QtWidgets.QHBoxLayout()
        image_section.setSpacing(15)
        
        # Left: Image preview (SMALLER)
        preview_container = QtWidgets.QWidget()
        preview_container.setMaximumWidth(260)
        preview_layout = QtWidgets.QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QtWidgets.QLabel("📸 THUMBNAIL")
        preview_label.setStyleSheet(f"""
            color: {CYBER_MAGENTA};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        preview_layout.addWidget(preview_label)
        
        # Image preview area - COMPACT SIZE
        self.image_preview = QtWidgets.QLabel()
        self.image_preview.setObjectName("imagePreview")
        self.image_preview.setFixedSize(250, 180)  # ← SMALLER!
        self.image_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.image_preview.setScaledContents(False)
        self.image_preview.setStyleSheet(f"""
            QLabel {{
                background: {CYBER_DARKER};
                border: 2px dashed {CYBER_MAGENTA}60;
                border-radius: 8px;
                color: {CYBER_MAGENTA}60;
                font-size: 12px;
                font-weight: 700;
            }}
        """)
        self.image_preview.setText("📸\n\nNo Image\n\nClick Upload")
        preview_layout.addWidget(self.image_preview)
        
        # Image info label - COMPACT
        self.image_info_label = QtWidgets.QLabel("")
        self.image_info_label.setStyleSheet(f"""
            color: {CYBER_CYAN};
            font-size: 10px;
            padding: 3px;
        """)
        self.image_info_label.setWordWrap(True)
        preview_layout.addWidget(self.image_info_label)
        
        image_section.addWidget(preview_container)
        
        # Right: Upload controls + Requirements
        controls_container = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(controls_container)
        controls_layout.setSpacing(10)
        
        controls_label = QtWidgets.QLabel("⚡ IMAGE CONTROLS")
        controls_label.setStyleSheet(f"""
            color: {CYBER_CYAN};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        controls_layout.addWidget(controls_label)
        
        # Upload button
        self.btn_upload_image = CyberButton("📸 UPLOAD", CYBER_MAGENTA)
        self.btn_upload_image.setFixedHeight(40)
        self.btn_upload_image.clicked.connect(self._upload_image)
        controls_layout.addWidget(self.btn_upload_image)
        
        # Remove button
        self.btn_remove_image = CyberButton("🗑️ REMOVE", CYBER_RED)
        self.btn_remove_image.setFixedHeight(40)
        self.btn_remove_image.clicked.connect(self._remove_image)
        self.btn_remove_image.setEnabled(False)
        controls_layout.addWidget(self.btn_remove_image)
        
        # Requirements - COMPACT
        requirements_text = QtWidgets.QLabel(
            "📋 Requirements:\n"
            "• Max 5 MB\n"
            "• JPEG, PNG, GIF, BMP\n"
            "• Auto resize > 1920px\n"
            "• Compressed 85%"
        )
        requirements_text.setStyleSheet(f"""
            color: {CYBER_CYAN}70;
            font-size: 10px;
            padding: 8px;
            background: {CYBER_DARKER};
            border: 1px solid {CYBER_CYAN}30;
            border-radius: 6px;
            line-height: 1.4;
        """)
        controls_layout.addWidget(requirements_text)
        controls_layout.addStretch()
        
        image_section.addWidget(controls_container, 1)
        
        layout.addLayout(image_section)
        
        # Content editor
        content_label = QtWidgets.QLabel("⚡ ARTICLE CONTENT")
        content_label.setStyleSheet(f"""
            color: {CYBER_MAGENTA};
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        
        self.editor = CyberTextEdit()
        
        layout.addWidget(content_label)
        layout.addWidget(self.editor, 1)
        
        # Action buttons
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(15)
        
        self.btn_save_draft = CyberButton("💾 SAVE DRAFT", CYBER_YELLOW)
        self.btn_save_draft.clicked.connect(lambda: self._save_article(False))
        
        self.btn_publish = CyberButton("🚀 PUBLISH NOW", CYBER_GREEN)
        self.btn_publish.clicked.connect(lambda: self._save_article(True))
        
        self.btn_clear = CyberButton("🗑 CLEAR ALL", CYBER_RED)
        self.btn_clear.clicked.connect(self._clear_form)
        
        action_row.addWidget(self.btn_save_draft, 1)
        action_row.addWidget(self.btn_publish, 2)
        action_row.addWidget(self.btn_clear, 1)
        
        layout.addLayout(action_row)
        
        return widget
    
    def _create_articles_tab(self):
        """Create articles table with IMAGE indicator"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(15)
        
        # Refresh button
        refresh_btn = CyberButton("🔄 REFRESH DATA", CYBER_CYAN)
        refresh_btn.clicked.connect(self._load_my_articles)
        layout.addWidget(refresh_btn)
        
        # Table with IMAGE column
        self.table_articles = QtWidgets.QTableWidget(0, 5)
        self.table_articles.setObjectName("cyberTable")
        self.table_articles.setHorizontalHeaderLabels(["ID", "TITLE", "STATUS", "DATE", "IMAGE"])
        
        header = self.table_articles.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        
        self.table_articles.setAlternatingRowColors(True)
        self.table_articles.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.table_articles)
        
        return widget
    
    def _create_feed_tab(self):
        """Create feed with cyber theme"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(15)
        
        info = QtWidgets.QLabel("🌐 GLOBAL PUBLISHED FEED")
        info.setStyleSheet(f"""
            color: {CYBER_CYAN};
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 15px;
            background: {CYBER_DARKER};
            border: 2px solid {CYBER_CYAN};
            border-radius: 10px;
            text-shadow: 0 0 10px {CYBER_CYAN};
        """)
        layout.addWidget(info)
        
        self.table_feed = QtWidgets.QTableWidget(0, 4)
        self.table_feed.setObjectName("cyberTable")
        self.table_feed.setHorizontalHeaderLabels(["ID", "TITLE", "AUTHOR", "DATE"])
        
        header = self.table_feed.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        
        self.table_feed.setAlternatingRowColors(True)
        self.table_feed.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.table_feed)
        
        refresh = CyberButton("🔄 REFRESH FEED", CYBER_MAGENTA)
        refresh.clicked.connect(self._load_feed)
        layout.addWidget(refresh)
        
        return widget
    
    def _upload_image(self):
        """Upload and process image"""
        if not PILLOW_AVAILABLE:
            QtWidgets.QMessageBox.warning(
                self, "⚠ Pillow Required",
                "Pillow library is not installed!\n\n"
                "Install it with: pip install Pillow"
            )
            return
        
        # File dialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        
        if not filename:
            return
        
        try:
            # Load image with Pillow
            image = Image.open(filename)
            
            # Check file size
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            if file_size_mb > MAX_IMAGE_SIZE_MB:
                QtWidgets.QMessageBox.warning(
                    self, "⚠ File Too Large",
                    f"Image size: {file_size_mb:.2f} MB\n"
                    f"Maximum allowed: {MAX_IMAGE_SIZE_MB} MB\n\n"
                    "Please choose a smaller image or compress it."
                )
                return
            
            # Convert to RGB if needed
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if len(image.split()) > 3 else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            original_size = image.size
            if image.width > MAX_IMAGE_WIDTH:
                ratio = MAX_IMAGE_WIDTH / image.width
                new_height = int(image.height * ratio)
                image = image.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=IMAGE_QUALITY, optimize=True)
            image_bytes = buffer.getvalue()
            
            # Store image data
            self.current_image_data = image_bytes
            self.current_image_filename = os.path.basename(filename)
            self.current_image_mimetype = 'image/jpeg'
            
            # Show preview - COMPACT THUMBNAIL
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            
            # Scale to thumbnail size (max 240x170)
            scaled_pixmap = pixmap.scaled(
                240, 170,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            
            self.image_preview.setPixmap(scaled_pixmap)
            
            # Update info - COMPACT
            compressed_size_kb = len(image_bytes) / 1024
            info_text = (
                f"✓ {self.current_image_filename}\n"
                f"✓ {original_size[0]}x{original_size[1]} → {image.size[0]}x{image.size[1]}\n"
                f"✓ {compressed_size_kb:.1f} KB"
            )
            self.image_info_label.setText(info_text)
            
            # Enable remove button
            self.btn_remove_image.setEnabled(True)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "❌ Error",
                f"Failed to load image:\n{str(e)}"
            )
    
    def _remove_image(self):
        """Remove uploaded image"""
        self.current_image_data = None
        self.current_image_filename = None
        self.current_image_mimetype = None
        
        # Reset preview
        self.image_preview.clear()
        self.image_preview.setText("📸\n\nNo Image\n\nClick Upload")
        self.image_info_label.setText("")
        
        # Disable remove button
        self.btn_remove_image.setEnabled(False)
    
    def _save_article(self, publish=True):
        """Save article WITH or WITHOUT image"""
        title = self.input_title.text().strip()
        content = self.editor.toPlainText().strip()
        
        if not title:
            QtWidgets.QMessageBox.warning(self, "⚠ WARNING", "Please enter article title!")
            self.input_title.setFocus()
            return
        
        if not content:
            QtWidgets.QMessageBox.warning(self, "⚠ WARNING", "Please write article content!")
            self.editor.setFocus()
            return
        
        # Save with or without image
        if self.current_image_data:
            success = create_news_with_image(
                self.username, 
                title, 
                content, 
                publish,
                self.current_image_data,
                self.current_image_filename,
                self.current_image_mimetype
            )
        else:
            success = create_news(self.username, title, content, publish)
        
        if success:
            status = "PUBLISHED" if publish else "SAVED AS DRAFT"
            QtWidgets.QMessageBox.information(self, "✅ SUCCESS", f"Article {status}!")
            self._clear_form()
            self._load_statistics()
            self._load_my_articles()
            if publish:
                self._load_feed()
        else:
            QtWidgets.QMessageBox.critical(self, "❌ ERROR", "Failed to save article!")
    
    def _clear_form(self):
        """Clear form"""
        reply = QtWidgets.QMessageBox.question(
            self, "⚠ CONFIRM",
            "Clear all fields? Unsaved changes will be lost!",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.input_title.clear()
            self.editor.clear()
            self._remove_image()
            self.input_title.setFocus()
    
    def _load_statistics(self):
        """Load stats WITH image count"""
        try:
            articles = list_my_news_with_images(self.username, limit=1000)
            total = len(articles)
            published = len([a for a in articles if a[2] == 'published'])
            draft = total - published
            with_images = len([a for a in articles if a[4]])  # has_image column
            
            self.card_total.update_value(total)
            self.card_published.update_value(published)
            self.card_draft.update_value(draft)
            self.card_with_images.update_value(with_images)
        except Exception as e:
            print(f"Error loading stats: {e}")
    
    def _load_my_articles(self):
        """Load articles table WITH image indicator"""
        try:
            articles = list_my_news_with_images(self.username, limit=100)
            self.table_articles.setRowCount(len(articles))
            
            for row, (aid, title, status, created, has_image) in enumerate(articles):
                self.table_articles.setItem(row, 0, QtWidgets.QTableWidgetItem(str(aid)))
                self.table_articles.setItem(row, 1, QtWidgets.QTableWidgetItem(title))
                
                status_item = QtWidgets.QTableWidgetItem(status.upper())
                if status == 'published':
                    status_item.setForeground(QtGui.QBrush(QtGui.QColor(CYBER_GREEN)))
                else:
                    status_item.setForeground(QtGui.QBrush(QtGui.QColor(CYBER_YELLOW)))
                self.table_articles.setItem(row, 2, status_item)
                
                self.table_articles.setItem(row, 3, QtWidgets.QTableWidgetItem(created or "N/A"))
                
                # Image indicator
                image_item = QtWidgets.QTableWidgetItem("🖼️" if has_image else "-")
                if has_image:
                    image_item.setForeground(QtGui.QBrush(QtGui.QColor(CYBER_MAGENTA)))
                self.table_articles.setItem(row, 4, image_item)
        except Exception as e:
            print(f"Error loading articles: {e}")
    
    def _load_feed(self):
        """Load feed"""
        try:
            articles = list_published_news(limit=100)
            self.table_feed.setRowCount(len(articles))
            
            for row, (aid, title, author, published) in enumerate(articles):
                self.table_feed.setItem(row, 0, QtWidgets.QTableWidgetItem(str(aid)))
                self.table_feed.setItem(row, 1, QtWidgets.QTableWidgetItem(title))
                
                author_item = QtWidgets.QTableWidgetItem(author)
                author_item.setForeground(QtGui.QBrush(QtGui.QColor(CYBER_MAGENTA)))
                self.table_feed.setItem(row, 2, author_item)
                
                self.table_feed.setItem(row, 3, QtWidgets.QTableWidgetItem(published or "N/A"))
        except Exception as e:
            print(f"Error loading feed: {e}")
    
    def _logout(self):
        """Logout"""
        if hasattr(self, 'hb_timer'):
            self.hb_timer.stop()
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        if self.session_id:
            try:
                end_session(self.session_id)
            except:
                pass
        self.close()
    
    def _apply_cyberpunk_theme(self):
        """Apply FULL CYBERPUNK THEME"""
        self.setStyleSheet(f"""
            /* Global Cyberpunk Background */
            QMainWindow, QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {CYBER_DARKER},
                    stop:0.5 {CYBER_DARK},
                    stop:1 {CYBER_DARKER});
                color: {CYBER_CYAN};
                font-family: 'Segoe UI', sans-serif;
            }}
            
            /* Cyber Header */
            #cyberHeaderTitle {{
                font-size: 32px;
                font-weight: 900;
                color: {CYBER_CYAN};
                text-shadow: 0 0 20px {CYBER_CYAN},
                             0 0 40px {CYBER_CYAN},
                             0 0 60px {CYBER_CYAN};
                letter-spacing: 3px;
            }}
            #cyberHeaderSubtitle {{
                font-size: 14px;
                font-weight: 700;
                color: {CYBER_MAGENTA};
                text-shadow: 0 0 10px {CYBER_MAGENTA};
                letter-spacing: 2px;
            }}
            
            /* Cyber Tabs */
            QTabWidget::pane {{
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 15px;
                background: {CYBER_DARKER};
            }}
            QTabBar::tab {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN}80;
                border: 2px solid {CYBER_CYAN}40;
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 12px 30px;
                margin-right: 5px;
                font-weight: 700;
                font-size: 13px;
                letter-spacing: 1px;
            }}
            QTabBar::tab:selected {{
                background: {CYBER_DARK};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN};
                box-shadow: 0 0 20px {CYBER_CYAN}80;
            }}
            QTabBar::tab:hover:!selected {{
                background: {CYBER_CYAN}10;
                color: {CYBER_CYAN};
            }}
            
            /* Cyber Title Input */
            #cyberTitleInput {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 12px;
                padding: 15px 20px;
                font-size: 18px;
                font-weight: 700;
            }}
            #cyberTitleInput:focus {{
                border: 2px solid {CYBER_CYAN};
                box-shadow: 0 0 20px {CYBER_CYAN}60;
            }}
            
            /* Cyber Tables */
            QTableWidget {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 12px;
                gridline-color: {CYBER_CYAN}20;
                selection-background-color: {CYBER_CYAN}30;
                font-family: 'Consolas', monospace;
            }}
            QTableWidget::item {{
                padding: 10px;
            }}
            QTableWidget::item:alternate {{
                background: {CYBER_DARK};
            }}
            QHeaderView::section {{
                background: {CYBER_GRID};
                color: {CYBER_CYAN};
                border: 1px solid {CYBER_CYAN}40;
                padding: 12px;
                font-weight: 700;
                font-size: 12px;
                letter-spacing: 2px;
                text-transform: uppercase;
                text-shadow: 0 0 5px {CYBER_CYAN};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background: {CYBER_DARKER};
                width: 14px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: {CYBER_CYAN}60;
                border-radius: 7px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CYBER_CYAN};
                box-shadow: 0 0 10px {CYBER_CYAN};
            }}
            QScrollBar:horizontal {{
                background: {CYBER_DARKER};
                height: 14px;
                border-radius: 7px;
            }}
            QScrollBar::handle:horizontal {{
                background: {CYBER_CYAN}60;
                border-radius: 7px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {CYBER_CYAN};
                box-shadow: 0 0 10px {CYBER_CYAN};
            }}
            
            /* Message Boxes */
            QMessageBox {{
                background: {CYBER_DARK};
                color: {CYBER_CYAN};
            }}
            QMessageBox QLabel {{
                color: {CYBER_CYAN};
                font-size: 14px;
            }}
            QMessageBox QPushButton {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN};
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 700;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background: {CYBER_CYAN}20;
                box-shadow: 0 0 15px {CYBER_CYAN};
            }}
        """)
        
        # Set cyberpunk font
        font = QtGui.QFont("Segoe UI", 10)
        self.setFont(font)
    
    def closeEvent(self, event):
        """Handle close"""
        self._logout()
        event.accept()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = PenerbitDashboard("CYBER_USER", None)
    window.show()
    sys.exit(app.exec_())
