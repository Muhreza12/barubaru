# user_dashboard.py — EYE-FRIENDLY CYBERPUNK WITH COMMENTS + CRYPTO TICKER 💬📈
"""
🔮 CYBERPUNK USER DASHBOARD WITH NESTED COMMENTS + CRYPTO TICKER 🔮

Features:
- Eye-friendly colors
- Article viewing with images
- NESTED COMMENT SYSTEM (Reddit-style)
- Reply to comments
- Real-time comment count
- CRYPTO PRICE TICKER (Auto-scrolling)

Author: Claude + Reza
Version: 5.0 - Crypto Edition
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap, QFont
from typing import Optional, List, Tuple
from app_db_fixed import (
    heartbeat, end_session, get_news_detail, get_news_image,
    # Comment functions
    add_comment, get_article_comments, get_comment_count, 
    delete_comment, edit_comment
)
from app_db_interactions import (
    get_trending_articles,
    get_popular_articles,
    get_most_liked_articles,
    get_user_liked_articles,
    get_user_bookmarked_articles,
    get_user_interaction_summary,
    like_article,
    unlike_article,
    bookmark_article,
    unbookmark_article,
    is_article_liked,
    is_article_bookmarked,
    track_article_view
)
from crypto_ticker import CryptoTickerWidget

# 🎨 EYE-FRIENDLY CYBERPUNK COLOR PALETTE
CYBER_CYAN = "#4dd4d4"
CYBER_MAGENTA = "#d946d9"
CYBER_PURPLE = "#8b5cf6"
CYBER_PINK = "#ec4899"
CYBER_BLUE = "#3b82f6"
CYBER_GREEN = "#10b981"
CYBER_RED = "#ef4444"
CYBER_DARK = "#1a1b26"
CYBER_DARKER = "#16161e"
CYBER_GRID = "#24283b"
CYBER_TEXT = "#c0caf5"
CYBER_TEXT_DIM = "#9aa5ce"


class CommentWidget(QtWidgets.QFrame):
    """Single comment widget with reply button"""
    
    reply_clicked = QtCore.pyqtSignal(int, str)  # comment_id, username
    refresh_requested = QtCore.pyqtSignal()
    
    def __init__(self, comment: dict, current_user: str, indent_level: int = 0, parent=None):
        super().__init__(parent)
        self.comment = comment
        self.current_user = current_user
        self.indent_level = indent_level
        
        self.setObjectName("commentWidget")
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup comment UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        
        # Add left margin for nested comments
        if self.indent_level > 0:
            layout.setContentsMargins(30 + (self.indent_level * 20), 8, 10, 8)
        
        # Header: username + date
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(8)
        
        username_label = QtWidgets.QLabel(f"👤 {self.comment['username']}")
        username_label.setObjectName("commentUsername")
        username_font = QFont("Segoe UI", 10, QFont.Bold)
        username_label.setFont(username_font)
        header_layout.addWidget(username_label)
        
        date_label = QtWidgets.QLabel(self.comment['created_at'])
        date_label.setObjectName("commentDate")
        date_font = QFont("Segoe UI", 9)
        date_label.setFont(date_font)
        header_layout.addWidget(date_label)
        
        header_layout.addStretch()
        
        # Reply button
        reply_btn = QtWidgets.QPushButton("💬 Reply")
        reply_btn.setObjectName("replyBtn")
        reply_btn.setFixedHeight(28)
        reply_btn.setCursor(QtCore.Qt.PointingHandCursor)
        reply_btn.clicked.connect(self._on_reply_clicked)
        header_layout.addWidget(reply_btn)
        
        # Delete button (only for own comments)
        if self.comment['username'] == self.current_user:
            delete_btn = QtWidgets.QPushButton("🗑️")
            delete_btn.setObjectName("deleteBtn")
            delete_btn.setFixedSize(28, 28)
            delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
            delete_btn.clicked.connect(self._on_delete_clicked)
            delete_btn.setToolTip("Delete comment")
            header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # Content
        content_label = QtWidgets.QLabel(self.comment['content'])
        content_label.setObjectName("commentContent")
        content_label.setWordWrap(True)
        content_font = QFont("Segoe UI", 10)
        content_label.setFont(content_font)
        layout.addWidget(content_label)
    
    def _on_reply_clicked(self):
        """Emit reply signal"""
        self.reply_clicked.emit(self.comment['id'], self.comment['username'])
    
    def _on_delete_clicked(self):
        """Delete comment"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Comment",
            "Are you sure you want to delete this comment?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            success = delete_comment(self.comment['id'], self.current_user)
            if success:
                QtWidgets.QMessageBox.information(self, "Success", "Comment deleted!")
                self.refresh_requested.emit()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to delete comment!")
    
    def _apply_styles(self):
        """Apply comment styles"""
        # Darker background for nested comments
        bg_color = CYBER_DARKER if self.indent_level == 0 else CYBER_DARK
        border_color = f"{CYBER_CYAN}30" if self.indent_level == 0 else f"{CYBER_MAGENTA}20"
        
        self.setStyleSheet(f"""
            #commentWidget {{
                background: {bg_color};
                border-left: 3px solid {border_color};
                border-radius: 8px;
            }}
            #commentUsername {{
                color: {CYBER_MAGENTA};
            }}
            #commentDate {{
                color: {CYBER_TEXT_DIM};
            }}
            #commentContent {{
                color: {CYBER_TEXT};
                padding: 4px 0;
            }}
            #replyBtn {{
                background: {CYBER_CYAN}20;
                color: {CYBER_CYAN};
                border: 1px solid {CYBER_CYAN}60;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 10px;
                font-weight: 600;
            }}
            #replyBtn:hover {{
                background: {CYBER_CYAN}30;
                border-color: {CYBER_CYAN};
            }}
            #deleteBtn {{
                background: {CYBER_RED}20;
                color: {CYBER_RED};
                border: 1px solid {CYBER_RED}60;
                border-radius: 6px;
                font-size: 14px;
            }}
            #deleteBtn:hover {{
                background: {CYBER_RED}30;
                border-color: {CYBER_RED};
            }}
        """)


class CommentSection(QtWidgets.QWidget):
    """Comment section with nested replies"""
    
    def __init__(self, article_id: int, username: str, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.username = username
        self.reply_to_id = None
        self.reply_to_username = None
        
        self._setup_ui()
        self._load_comments()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header
        header = QtWidgets.QLabel("💬 Comments")
        header.setObjectName("sectionHeader")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header.setFont(header_font)
        header.setStyleSheet(f"color: {CYBER_CYAN}; padding: 10px 0;")
        layout.addWidget(header)
        
        # Comment input area
        input_frame = QtWidgets.QFrame()
        input_frame.setObjectName("commentInputFrame")
        input_layout = QtWidgets.QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # Reply indicator (hidden by default)
        self.reply_indicator = QtWidgets.QLabel()
        self.reply_indicator.setObjectName("replyIndicator")
        self.reply_indicator.setVisible(False)
        reply_indicator_font = QFont("Segoe UI", 9, QFont.Medium, True)
        self.reply_indicator.setFont(reply_indicator_font)
        input_layout.addWidget(self.reply_indicator)
        
        # Input field
        self.comment_input = QtWidgets.QTextEdit()
        self.comment_input.setObjectName("commentInput")
        self.comment_input.setPlaceholderText("Write a comment...")
        self.comment_input.setFixedHeight(80)
        comment_font = QFont("Segoe UI", 10)
        self.comment_input.setFont(comment_font)
        input_layout.addWidget(self.comment_input)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel reply button (hidden by default)
        self.cancel_reply_btn = QtWidgets.QPushButton("✕ Cancel Reply")
        self.cancel_reply_btn.setObjectName("cancelReplyBtn")
        self.cancel_reply_btn.setFixedHeight(36)
        self.cancel_reply_btn.setVisible(False)
        self.cancel_reply_btn.clicked.connect(self._cancel_reply)
        button_layout.addWidget(self.cancel_reply_btn)
        
        button_layout.addStretch()
        
        post_btn = QtWidgets.QPushButton("Post Comment")
        post_btn.setObjectName("postCommentBtn")
        post_btn.setFixedHeight(36)
        post_btn_font = QFont("Segoe UI", 10, QFont.Bold)
        post_btn.setFont(post_btn_font)
        post_btn.clicked.connect(self._post_comment)
        button_layout.addWidget(post_btn)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_frame)
        
        # Comments list
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("commentsScroll")
        
        self.comments_container = QtWidgets.QWidget()
        self.comments_layout = QtWidgets.QVBoxLayout(self.comments_container)
        self.comments_layout.setContentsMargins(0, 0, 0, 0)
        self.comments_layout.setSpacing(10)
        self.comments_layout.addStretch()
        
        scroll.setWidget(self.comments_container)
        layout.addWidget(scroll, 1)
        
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(f"""
            #commentInputFrame {{
                background: {CYBER_GRID};
                border: 1px solid {CYBER_CYAN}30;
                border-radius: 10px;
            }}
            #replyIndicator {{
                color: {CYBER_MAGENTA};
                padding: 5px 10px;
                background: {CYBER_MAGENTA}20;
                border-left: 3px solid {CYBER_MAGENTA};
                border-radius: 5px;
            }}
            #commentInput {{
                background: {CYBER_DARKER};
                border: 1px solid {CYBER_CYAN}40;
                border-radius: 8px;
                padding: 10px;
                color: {CYBER_TEXT};
            }}
            #postCommentBtn {{
                background: {CYBER_CYAN}50;
                color: white;
                border: 2px solid {CYBER_CYAN}70;
                border-radius: 8px;
                padding: 0 24px;
            }}
            #postCommentBtn:hover {{
                background: {CYBER_CYAN}70;
            }}
            #cancelReplyBtn {{
                background: {CYBER_RED}30;
                color: {CYBER_RED};
                border: 1px solid {CYBER_RED}60;
                border-radius: 8px;
                padding: 0 16px;
            }}
            #cancelReplyBtn:hover {{
                background: {CYBER_RED}40;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {CYBER_DARKER};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {CYBER_CYAN}50;
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CYBER_CYAN}70;
            }}
        """)
    
    def _load_comments(self):
        """Load and display comments"""
        # Clear existing
        while self.comments_layout.count() > 1:
            item = self.comments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get comments
        comments = get_article_comments(self.article_id)
        
        if not comments:
            no_comments = QtWidgets.QLabel("No comments yet. Be the first to comment!")
            no_comments.setAlignment(QtCore.Qt.AlignCenter)
            no_comments_font = QFont("Segoe UI", 11)
            no_comments.setFont(no_comments_font)
            no_comments.setStyleSheet(f"color: {CYBER_TEXT_DIM}; padding: 30px;")
            self.comments_layout.insertWidget(0, no_comments)
            return
        
        # Display comments recursively
        for comment in comments:
            self._add_comment_widget(comment, 0)
    
    def _add_comment_widget(self, comment: dict, indent_level: int):
        """Add comment widget recursively (for nested replies)"""
        widget = CommentWidget(comment, self.username, indent_level)
        widget.reply_clicked.connect(self._set_reply_to)
        widget.refresh_requested.connect(self._load_comments)
        self.comments_layout.insertWidget(self.comments_layout.count() - 1, widget)
        
        # Add replies recursively
        for reply in comment.get('replies', []):
            self._add_comment_widget(reply, indent_level + 1)
    
    def _set_reply_to(self, comment_id: int, username: str):
        """Set reply target"""
        self.reply_to_id = comment_id
        self.reply_to_username = username
        
        self.reply_indicator.setText(f"↪️ Replying to @{username}")
        self.reply_indicator.setVisible(True)
        self.cancel_reply_btn.setVisible(True)
        
        self.comment_input.setFocus()
    
    def _cancel_reply(self):
        """Cancel reply mode"""
        self.reply_to_id = None
        self.reply_to_username = None
        
        self.reply_indicator.setVisible(False)
        self.cancel_reply_btn.setVisible(False)
    
    def _post_comment(self):
        """Post comment or reply"""
        content = self.comment_input.toPlainText().strip()
        
        if not content:
            QtWidgets.QMessageBox.warning(self, "Error", "Comment cannot be empty!")
            return
        
        # Add comment
        comment_id = add_comment(
            article_id=self.article_id,
            username=self.username,
            content=content,
            parent_id=self.reply_to_id
        )
        
        if comment_id:
            self.comment_input.clear()
            self._cancel_reply()
            self._load_comments()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to post comment!")


class ArticleDetailDialog(QtWidgets.QDialog):
    """👀 Article Detail Dialog WITH COMMENTS"""
    
    def __init__(self, article_id: int, username: str, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.username = username
        
        self.setWindowTitle("Article Detail")
        self.resize(900, 700)
        self.setModal(True)
        
        font = QFont("Segoe UI", 10)
        font.setHintingPreference(QFont.PreferFullHinting)
        self.setFont(font)
        
        self._load_and_display()
    
    def _load_and_display(self):
        """Load article detail dan display"""
        article = get_news_detail(self.article_id)
        
        if not article:
            QtWidgets.QMessageBox.warning(self, "Error", "Article not found!")
            self.reject()
            return
        
        track_article_view(self.article_id, self.username)
        self._setup_ui(article)
        self._apply_styles()
    
    def _setup_ui(self, article: dict):
        """Setup UI dengan article data"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header bar
        header_bar = QtWidgets.QFrame()
        header_bar.setObjectName("headerBar")
        header_bar.setFixedHeight(60)
        
        header_layout = QtWidgets.QHBoxLayout(header_bar)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        header_title = QtWidgets.QLabel("📰 Article Detail")
        header_title.setObjectName("headerTitle")
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        # Comment count
        comment_count = get_comment_count(self.article_id)
        comment_count_label = QtWidgets.QLabel(f"💬 {comment_count} comments")
        comment_count_label.setObjectName("commentCountLabel")
        comment_count_font = QFont("Segoe UI", 10, QFont.Medium)
        comment_count_label.setFont(comment_count_font)
        header_layout.addWidget(comment_count_label)
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setFixedSize(40, 40)
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header_bar)
        
        # Main content with tabs
        tabs = QtWidgets.QTabWidget()
        tabs.setObjectName("articleTabs")
        
        # Tab 1: Article Content
        content_tab = self._create_content_tab(article)
        tabs.addTab(content_tab, "📄 Article")
        
        # Tab 2: Comments
        comments_tab = CommentSection(self.article_id, self.username)
        tabs.addTab(comments_tab, f"💬 Comments ({get_comment_count(self.article_id)})")
        
        layout.addWidget(tabs)
    
    def _create_content_tab(self, article: dict):
        """Create article content tab"""
        tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("cyberScroll")
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Title
        title_label = QtWidgets.QLabel(article['title'])
        title_label.setObjectName("articleTitle")
        title_label.setWordWrap(True)
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        title_label.setFont(title_font)
        content_layout.addWidget(title_label)
        
        # Meta info
        meta_frame = QtWidgets.QFrame()
        meta_frame.setObjectName("metaFrame")
        meta_layout = QtWidgets.QHBoxLayout(meta_frame)
        meta_layout.setContentsMargins(15, 12, 15, 12)
        
        author_label = QtWidgets.QLabel(f"👤 {article['author']}")
        author_label.setObjectName("metaAuthor")
        author_font = QFont("Segoe UI", 11, QFont.DemiBold)
        author_label.setFont(author_font)
        meta_layout.addWidget(author_label)
        
        meta_layout.addStretch()
        
        date_label = QtWidgets.QLabel(f"📅 {article['created_at']}")
        date_label.setObjectName("metaDate")
        date_font = QFont("Segoe UI", 10)
        date_label.setFont(date_font)
        meta_layout.addWidget(date_label)
        
        content_layout.addWidget(meta_frame)
        
        # IMAGE SECTION
        if article.get('has_image'):
            image_data_tuple = get_news_image(self.article_id)
            if image_data_tuple:
                image_data, filename, mimetype = image_data_tuple
                
                image_frame = QtWidgets.QFrame()
                image_frame.setObjectName("imageFrame")
                image_layout = QtWidgets.QVBoxLayout(image_frame)
                image_layout.setContentsMargins(15, 15, 15, 15)
                image_layout.setAlignment(QtCore.Qt.AlignCenter)
                
                image_label = QtWidgets.QLabel()
                image_label.setAlignment(QtCore.Qt.AlignCenter)
                image_label.setObjectName("articleImage")
                
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        450, 300,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)
                
                image_layout.addWidget(image_label)
                
                caption = QtWidgets.QLabel(f"📸 {filename}")
                caption.setObjectName("imageCaption")
                caption.setAlignment(QtCore.Qt.AlignCenter)
                caption_font = QFont("Segoe UI", 9, QFont.Normal, True)
                caption.setFont(caption_font)
                image_layout.addWidget(caption)
                
                content_layout.addWidget(image_frame)
        
        # Content
        content_frame = QtWidgets.QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame_layout = QtWidgets.QVBoxLayout(content_frame)
        content_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        content_text = QtWidgets.QTextEdit()
        content_text.setPlainText(article['content'])
        content_text.setReadOnly(True)
        content_text.setObjectName("articleContent")
        content_font = QFont("Segoe UI", 11)
        content_font.setLetterSpacing(QFont.PercentageSpacing, 102)
        content_text.setFont(content_font)
        content_frame_layout.addWidget(content_text)
        
        content_layout.addWidget(content_frame, 1)
        
        # Action buttons
        actions_frame = QtWidgets.QFrame()
        actions_frame.setObjectName("actionsFrame")
        actions_layout = QtWidgets.QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(15)
        
        is_liked = is_article_liked(self.article_id, self.username)
        is_bookmarked = is_article_bookmarked(self.article_id, self.username)
        
        btn_font = QFont("Segoe UI", 11, QFont.Bold)
        
        self.btn_like = QtWidgets.QPushButton("❤️ Liked" if is_liked else "🤍 Like")
        self.btn_like.setObjectName("cyberBtnLike" if is_liked else "cyberBtn")
        self.btn_like.setFixedHeight(45)
        self.btn_like.setFont(btn_font)
        self.btn_like.clicked.connect(self._toggle_like)
        self.is_liked = is_liked
        actions_layout.addWidget(self.btn_like, 1)
        
        self.btn_bookmark = QtWidgets.QPushButton("🔖 Saved" if is_bookmarked else "📑 Save")
        self.btn_bookmark.setObjectName("cyberBtnBookmark" if is_bookmarked else "cyberBtn")
        self.btn_bookmark.setFixedHeight(45)
        self.btn_bookmark.setFont(btn_font)
        self.btn_bookmark.clicked.connect(self._toggle_bookmark)
        self.is_bookmarked = is_bookmarked
        actions_layout.addWidget(self.btn_bookmark, 1)
        
        content_layout.addWidget(actions_frame)
        
        scroll.setWidget(content_widget)
        tab_layout.addWidget(scroll)
        
        return tab
    
    def _toggle_like(self):
        """Toggle like status"""
        if self.is_liked:
            success = unlike_article(self.article_id, self.username)
            if success:
                self.is_liked = False
                self.btn_like.setText("🤍 Like")
                self.btn_like.setObjectName("cyberBtn")
                self.btn_like.setStyleSheet("")
        else:
            success = like_article(self.article_id, self.username)
            if success:
                self.is_liked = True
                self.btn_like.setText("❤️ Liked")
                self.btn_like.setObjectName("cyberBtnLike")
                self.btn_like.setStyleSheet("")
    
    def _toggle_bookmark(self):
        """Toggle bookmark status"""
        if self.is_bookmarked:
            success = unbookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = False
                self.btn_bookmark.setText("📑 Save")
                self.btn_bookmark.setObjectName("cyberBtn")
                self.btn_bookmark.setStyleSheet("")
        else:
            success = bookmark_article(self.article_id, self.username)
            if success:
                self.is_bookmarked = True
                self.btn_bookmark.setText("🔖 Saved")
                self.btn_bookmark.setObjectName("cyberBtnBookmark")
                self.btn_bookmark.setStyleSheet("")
    
    def _apply_styles(self):
        """Apply styles"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {CYBER_DARK};
                color: {CYBER_TEXT};
            }}
            #headerBar {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_PURPLE}30,
                    stop:1 {CYBER_CYAN}30);
                border-bottom: 1px solid {CYBER_CYAN}40;
            }}
            #headerTitle {{
                color: {CYBER_CYAN};
                font-weight: 700;
                font-size: 16px;
            }}
            #commentCountLabel {{
                color: {CYBER_MAGENTA};
                background: {CYBER_MAGENTA}20;
                padding: 5px 12px;
                border-radius: 6px;
            }}
            #headerCloseBtn {{
                background: transparent;
                color: {CYBER_RED};
                border: 2px solid {CYBER_RED}60;
                border-radius: 20px;
                font-size: 18px;
                font-weight: 700;
            }}
            #headerCloseBtn:hover {{
                background: {CYBER_RED}20;
                border-color: {CYBER_RED};
            }}
            QTabWidget::pane {{
                border: none;
                background: {CYBER_DARK};
            }}
            QTabBar::tab {{
                background: {CYBER_DARKER};
                color: {CYBER_TEXT_DIM};
                border: 1px solid {CYBER_CYAN}20;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {CYBER_DARK};
                color: {CYBER_CYAN};
                border: 1px solid {CYBER_CYAN}60;
            }}
            #articleTitle {{
                color: {CYBER_TEXT};
            }}
            #metaFrame {{
                background: {CYBER_GRID};
                border: 1px solid {CYBER_CYAN}25;
                border-radius: 10px;
            }}
            #metaAuthor {{
                color: {CYBER_MAGENTA};
            }}
            #metaDate {{
                color: {CYBER_TEXT_DIM};
            }}
            #imageFrame {{
                background: {CYBER_DARKER};
                border: 2px solid {CYBER_MAGENTA}40;
                border-radius: 12px;
            }}
            #articleImage {{
                border-radius: 8px;
            }}
            #imageCaption {{
                color: {CYBER_TEXT_DIM};
            }}
            #contentFrame {{
                background: transparent;
            }}
            #articleContent {{
                background: {CYBER_DARKER};
                border: 1px solid {CYBER_CYAN}25;
                border-radius: 10px;
                padding: 20px;
                color: {CYBER_TEXT};
                line-height: 1.7;
            }}
            #actionsFrame {{
                background: {CYBER_GRID};
                border: 1px solid {CYBER_CYAN}25;
                border-radius: 10px;
            }}
            #cyberBtn {{
                background: {CYBER_DARKER};
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 10px;
            }}
            #cyberBtn:hover {{
                background: {CYBER_CYAN}15;
                border-color: {CYBER_CYAN};
            }}
            #cyberBtnLike {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_RED}50,
                    stop:1 {CYBER_PINK}50);
                color: white;
                border: 2px solid {CYBER_RED}80;
                border-radius: 10px;
            }}
            #cyberBtnLike:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_RED}70,
                    stop:1 {CYBER_PINK}70);
            }}
            #cyberBtnBookmark {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_PURPLE}50,
                    stop:1 {CYBER_MAGENTA}50);
                color: white;
                border: 2px solid {CYBER_PURPLE}80;
                border-radius: 10px;
            }}
            #cyberBtnBookmark:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {CYBER_PURPLE}70,
                    stop:1 {CYBER_MAGENTA}70);
            }}
            QScrollBar:vertical {{
                background: {CYBER_DARKER};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {CYBER_CYAN}50;
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CYBER_CYAN}70;
            }}
        """)


class CyberArticleCard(QtWidgets.QFrame):
    """👀 Article Card"""
    
    article_clicked = QtCore.pyqtSignal(int)
    
    def __init__(self, article_id: int, title: str, author: str, 
                 username: str, views: int = 0, likes: int = 0, 
                 bookmarks: int = 0, parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.title = title
        self.author = author
        self.username = username
        self.views = views
        self.likes = likes
        self.bookmarks = bookmarks
        
        self.setObjectName("cyberCard")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(12)
        
        # Title
        title_label = QtWidgets.QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        title_font = QFont("Segoe UI", 13, QFont.DemiBold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Author
        author_label = QtWidgets.QLabel(f"👤 {self.author}")
        author_label.setObjectName("cardAuthor")
        author_font = QFont("Segoe UI", 10, QFont.Medium)
        author_label.setFont(author_font)
        layout.addWidget(author_label)
        
        # Stats row
        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(15)
        
        stat_font = QFont("Segoe UI", 10)
        
        views_label = QtWidgets.QLabel(f"👁️ {self.views:,}")
        views_label.setObjectName("cardStat")
        views_label.setFont(stat_font)
        stats_row.addWidget(views_label)
        
        likes_label = QtWidgets.QLabel(f"❤️ {self.likes}")
        likes_label.setObjectName("cardStat")
        likes_label.setFont(stat_font)
        stats_row.addWidget(likes_label)
        
        # Get comment count
        comment_count = get_comment_count(self.article_id)
        comments_label = QtWidgets.QLabel(f"💬 {comment_count}")
        comments_label.setObjectName("cardStat")
        comments_label.setFont(stat_font)
        stats_row.addWidget(comments_label)
        
        stats_row.addStretch()
        
        # Read button
        read_btn = QtWidgets.QPushButton("Read →")
        read_btn.setObjectName("cardReadBtn")
        read_btn.setFixedHeight(32)
        read_font = QFont("Segoe UI", 10, QFont.Bold)
        read_btn.setFont(read_font)
        read_btn.clicked.connect(lambda: self.article_clicked.emit(self.article_id))
        stats_row.addWidget(read_btn)
        
        layout.addLayout(stats_row)
    
    def _apply_styles(self):
        """Apply card styles"""
        self.setStyleSheet(f"""
            #cyberCard {{
                background: {CYBER_DARKER};
                border: 1px solid {CYBER_CYAN}30;
                border-radius: 12px;
            }}
            #cyberCard:hover {{
                background: {CYBER_GRID};
                border: 1px solid {CYBER_CYAN}60;
            }}
            #cardTitle {{
                color: {CYBER_TEXT};
            }}
            #cardAuthor {{
                color: {CYBER_MAGENTA};
            }}
            #cardStat {{
                color: {CYBER_TEXT_DIM};
            }}
            #cardReadBtn {{
                background: {CYBER_CYAN}20;
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 8px;
                padding: 0 20px;
            }}
            #cardReadBtn:hover {{
                background: {CYBER_CYAN}30;
                border-color: {CYBER_CYAN};
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == QtCore.Qt.LeftButton:
            self.article_clicked.emit(self.article_id)
        super().mousePressEvent(event)


class LoadingWidget(QtWidgets.QWidget):
    """Loading indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        spinner = QtWidgets.QLabel("⏳")
        spinner.setAlignment(QtCore.Qt.AlignCenter)
        spinner.setStyleSheet(f"font-size: 48px; color: {CYBER_CYAN};")
        
        text = QtWidgets.QLabel("Loading...")
        text.setAlignment(QtCore.Qt.AlignCenter)
        text_font = QFont("Segoe UI", 12, QFont.Medium)
        text.setFont(text_font)
        text.setStyleSheet(f"color: {CYBER_TEXT_DIM};")
        
        layout.addWidget(spinner)
        layout.addWidget(text)


class ArticleListWidget(QtWidgets.QWidget):
    """Article list widget"""
    
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.is_loaded = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.stack = QtWidgets.QStackedWidget()
        
        self.loading_widget = LoadingWidget()
        self.stack.addWidget(self.loading_widget)
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("cyberScroll")
        
        self.container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(12)
        self.container_layout.addStretch()
        
        scroll.setWidget(self.container)
        content_layout.addWidget(scroll)
        
        self.stack.addWidget(content_widget)
        layout.addWidget(self.stack)
    
    def show_loading(self):
        self.stack.setCurrentIndex(0)
    
    def show_content(self):
        self.stack.setCurrentIndex(1)
    
    def load_articles(self, articles: List[Tuple], limit: int = 10):
        self.show_loading()
        
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not articles:
            no_data = QtWidgets.QLabel("No articles found")
            no_data.setAlignment(QtCore.Qt.AlignCenter)
            no_data_font = QFont("Segoe UI", 14, QFont.Medium)
            no_data.setFont(no_data_font)
            no_data.setStyleSheet(f"color: {CYBER_TEXT_DIM}; padding: 60px;")
            self.container_layout.insertWidget(0, no_data)
            self.show_content()
            self.is_loaded = True
            return
        
        articles_to_show = articles[:limit]
        
        for article in articles_to_show:
            article_id, title, author, views, likes, bookmarks, _ = article
            
            card = CyberArticleCard(
                article_id=article_id,
                title=title,
                author=author,
                username=self.username,
                views=views,
                likes=likes,
                bookmarks=bookmarks
            )
            card.article_clicked.connect(self._on_article_clicked)
            self.container_layout.insertWidget(self.container_layout.count() - 1, card)
        
        if len(articles) > limit:
            load_more_btn = QtWidgets.QPushButton(f"Load More ({len(articles) - limit} more) →")
            load_more_btn.setObjectName("loadMoreBtn")
            load_more_font = QFont("Segoe UI", 11, QFont.Bold)
            load_more_btn.setFont(load_more_font)
            load_more_btn.clicked.connect(lambda: self.load_articles(articles, limit + 10))
            self.container_layout.insertWidget(self.container_layout.count() - 1, load_more_btn)
        
        self.show_content()
        self.is_loaded = True
    
    def _on_article_clicked(self, article_id: int):
        dialog = ArticleDetailDialog(article_id, self.username, self)
        dialog.exec_()
        # Refresh after closing dialog (in case comments were added)
        self.is_loaded = False


class CyberUserDashboard(QtWidgets.QMainWindow):
    """👀 CYBERPUNK USER DASHBOARD WITH COMMENTS + CRYPTO TICKER"""
    
    def __init__(self, username: str = "user", session_id: Optional[int] = None):
        super().__init__()
        self.username = username
        self.session_id = session_id
        
        self.setWindowTitle(f"Crypto Insight — {username}")
        self.resize(1200, 750)
        
        app_font = QFont("Segoe UI", 10)
        app_font.setHintingPreference(QFont.PreferFullHinting)
        self.setFont(app_font)
        
        self._setup_ui()
        self._apply_theme()
        self._update_stats()
        
        if self.session_id:
            self.hb_timer = QtCore.QTimer(self)
            self.hb_timer.timeout.connect(lambda: heartbeat(self.session_id))
            self.hb_timer.start(20000)
    
    def _setup_ui(self):
        """Setup UI"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ========== CRYPTO TICKER AT TOP ==========
        self.crypto_ticker = CryptoTickerWidget()
        layout.addWidget(self.crypto_ticker)
        # ==========================================
        
        # Add spacing before header
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(25)
        layout.addWidget(spacer)
        
        # Container for rest of content with margins
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 0, 25, 25)
        content_layout.setSpacing(20)
        
        header = self._create_header()
        content_layout.addWidget(header)
        
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setObjectName("cyberTabs")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        self.news_feed_tab = self._create_news_feed_tab()
        self.tabs.addTab(self.news_feed_tab, "📰 News Feed")
        
        self.liked_tab = ArticleListWidget(self.username)
        self.tabs.addTab(self.liked_tab, "❤️ Liked")
        
        self.saved_tab = ArticleListWidget(self.username)
        self.tabs.addTab(self.saved_tab, "🔖 Saved")
        
        content_layout.addWidget(self.tabs)
        
        layout.addWidget(content_widget)
    
    def _create_header(self):
        """Create header"""
        header = QtWidgets.QFrame()
        header.setObjectName("cyberHeader")
        
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QtWidgets.QLabel(f"Welcome, {self.username}!")
        title.setObjectName("cyberHeaderTitle")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        
        layout.addWidget(title)
        layout.addStretch()
        
        self.stats_label = QtWidgets.QLabel("Loading...")
        self.stats_label.setObjectName("cyberHeaderStats")
        stats_font = QFont("Segoe UI", 10, QFont.Medium)
        self.stats_label.setFont(stats_font)
        layout.addWidget(self.stats_label)
        
        refresh_btn = QtWidgets.QPushButton("🔄")
        refresh_btn.setObjectName("cyberIconBtn")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self._refresh_current_tab)
        layout.addWidget(refresh_btn)
        
        logout_btn = QtWidgets.QPushButton("Logout")
        logout_btn.setObjectName("cyberLogoutBtn")
        logout_btn.setFixedHeight(40)
        logout_font = QFont("Segoe UI", 10, QFont.Bold)
        logout_btn.setFont(logout_font)
        logout_btn.clicked.connect(self._logout)
        layout.addWidget(logout_btn)
        
        return header
    
    def _create_news_feed_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 15, 0, 0)
        
        self.sub_tabs = QtWidgets.QTabWidget()
        self.sub_tabs.setObjectName("cyberSubTabs")
        self.sub_tabs.currentChanged.connect(self._on_subtab_changed)
        
        self.trending_list = ArticleListWidget(self.username)
        self.sub_tabs.addTab(self.trending_list, "🔥 Trending")
        
        self.popular_list = ArticleListWidget(self.username)
        self.sub_tabs.addTab(self.popular_list, "⭐ Popular")
        
        self.most_liked_list = ArticleListWidget(self.username)
        self.sub_tabs.addTab(self.most_liked_list, "❤️ Most Liked")
        
        layout.addWidget(self.sub_tabs)
        return tab
    
    def _apply_theme(self):
        """Apply theme"""
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {CYBER_DARK};
                color: {CYBER_TEXT};
            }}
            
            #cyberHeader {{
                background: transparent;
                border-bottom: 1px solid {CYBER_CYAN}40;
                padding-bottom: 15px;
            }}
            #cyberHeaderTitle {{
                color: {CYBER_CYAN};
            }}
            #cyberHeaderStats {{
                color: {CYBER_MAGENTA};
                padding: 8px 16px;
                background: {CYBER_GRID};
                border: 1px solid {CYBER_MAGENTA}40;
                border-radius: 8px;
            }}
            #cyberIconBtn {{
                background: transparent;
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}50;
                border-radius: 20px;
                font-size: 16px;
            }}
            #cyberIconBtn:hover {{
                background: {CYBER_CYAN}15;
                border-color: {CYBER_CYAN};
            }}
            #cyberLogoutBtn {{
                background: {CYBER_RED}50;
                color: white;
                border: 2px solid {CYBER_RED}70;
                border-radius: 10px;
                padding: 0 20px;
            }}
            #cyberLogoutBtn:hover {{
                background: {CYBER_RED}70;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {CYBER_CYAN}30;
                border-radius: 12px;
                background: {CYBER_DARKER};
            }}
            QTabBar::tab {{
                background: {CYBER_DARKER};
                color: {CYBER_TEXT_DIM};
                border: 1px solid {CYBER_CYAN}20;
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 24px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {CYBER_GRID};
                color: {CYBER_CYAN};
                border: 1px solid {CYBER_CYAN}60;
            }}
            QTabBar::tab:hover:!selected {{
                background: {CYBER_CYAN}10;
                color: {CYBER_CYAN};
            }}
            
            #loadMoreBtn {{
                background: {CYBER_CYAN}20;
                color: {CYBER_CYAN};
                border: 2px solid {CYBER_CYAN}60;
                border-radius: 10px;
                padding: 12px;
            }}
            #loadMoreBtn:hover {{
                background: {CYBER_CYAN}30;
                border-color: {CYBER_CYAN};
            }}
            
            QScrollBar:vertical {{
                background: {CYBER_DARKER};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {CYBER_CYAN}50;
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CYBER_CYAN}70;
            }}
        """)
    
    def _update_stats(self):
        def update():
            try:
                summary = get_user_interaction_summary(self.username)
                liked = summary.get('liked', 0)
                bookmarked = summary.get('bookmarked', 0)
                self.stats_label.setText(f"❤️ {liked}  •  🔖 {bookmarked}")
            except:
                self.stats_label.setText("Stats unavailable")
        QtCore.QTimer.singleShot(0, update)
    
    def _load_trending(self):
        if self.trending_list.is_loaded:
            return
        try:
            articles = get_trending_articles(limit=50, days=7)
            self.trending_list.load_articles(articles, limit=10)
        except Exception as e:
            print(f"Error: {e}")
    
    def _load_popular(self):
        if self.popular_list.is_loaded:
            return
        try:
            articles = get_popular_articles(limit=50)
            self.popular_list.load_articles(articles, limit=10)
        except Exception as e:
            print(f"Error: {e}")
    
    def _load_most_liked(self):
        if self.most_liked_list.is_loaded:
            return
        try:
            articles = get_most_liked_articles(limit=50)
            self.most_liked_list.load_articles(articles, limit=10)
        except Exception as e:
            print(f"Error: {e}")
    
    def _load_liked_articles(self):
        if self.liked_tab.is_loaded:
            return
        try:
            articles = get_user_liked_articles(self.username, limit=50)
            self.liked_tab.load_articles(articles, limit=10)
        except Exception as e:
            print(f"Error: {e}")
    
    def _load_saved_articles(self):
        if self.saved_tab.is_loaded:
            return
        try:
            articles = get_user_bookmarked_articles(self.username, limit=50)
            self.saved_tab.load_articles(articles, limit=10)
        except Exception as e:
            print(f"Error: {e}")
    
    def _on_tab_changed(self, index: int):
        if index == 0:
            current_sub = self.sub_tabs.currentIndex()
            if current_sub == 0:
                self._load_trending()
            elif current_sub == 1:
                self._load_popular()
            elif current_sub == 2:
                self._load_most_liked()
        elif index == 1:
            self._load_liked_articles()
        elif index == 2:
            self._load_saved_articles()
        self._update_stats()
    
    def _on_subtab_changed(self, index: int):
        if index == 0:
            self._load_trending()
        elif index == 1:
            self._load_popular()
        elif index == 2:
            self._load_most_liked()
    
    def _refresh_current_tab(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            current_sub = self.sub_tabs.currentIndex()
            if current_sub == 0:
                self.trending_list.is_loaded = False
                self._load_trending()
            elif current_sub == 1:
                self.popular_list.is_loaded = False
                self._load_popular()
            elif current_sub == 2:
                self.most_liked_list.is_loaded = False
                self._load_most_liked()
        elif current_tab == 1:
            self.liked_tab.is_loaded = False
            self._load_liked_articles()
        elif current_tab == 2:
            self.saved_tab.is_loaded = False
            self._load_saved_articles()
        self._update_stats()
    
    def _logout(self):
        if hasattr(self, 'hb_timer') and self.hb_timer.isActive():
            self.hb_timer.stop()
        if self.session_id:
            try:
                end_session(self.session_id)
            except:
                pass
        self.close()
    
    def closeEvent(self, event):
        self._logout()
        
        # Stop crypto ticker
        if hasattr(self, 'crypto_ticker'):
            self.crypto_ticker.stop()
        
        event.accept()
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self.trending_list.is_loaded:
            QtCore.QTimer.singleShot(100, self._load_trending)


# Alias
UserDashboard = CyberUserDashboard

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dashboard = CyberUserDashboard(username="reza")
    dashboard.show()
    sys.exit(app.exec_())
