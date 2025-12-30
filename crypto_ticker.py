import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

class CryptoTicker(QWidget):
    def __init__(self):
        super().__init__()
        self.prices = {}
        self.setup_ui()
        
        # Timer untuk update harga
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_prices)
        self.update_timer.start(30000)  # Update setiap 30 detik
        
        self.fetch_prices()  # Load pertama kali
    
    def setup_ui(self):
        # ULTRA SIMPLE - NO SIZE CONSTRAINTS!
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.setStyleSheet("""
            QWidget {
                background: #1a1a2e;
                border-bottom: 2px solid #00ff88;
            }
            QLabel {
                color: white;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        # Live indicator
        live_label = QLabel("🔴 LIVE PRICES:")
        live_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        layout.addWidget(live_label)
        
        # Crypto labels
        self.btc_label = QLabel("BTC: Loading...")
        self.eth_label = QLabel("ETH: Loading...")
        self.bnb_label = QLabel("BNB: Loading...")
        
        layout.addWidget(self.btc_label)
        layout.addWidget(QLabel("│"))
        layout.addWidget(self.eth_label)
        layout.addWidget(QLabel("│"))
        layout.addWidget(self.bnb_label)
        layout.addStretch()
        
        # Update time
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
    
    def fetch_prices(self):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,binancecoin',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Bitcoin
                btc = data['bitcoin']
                btc_color = "#00ff88" if btc['usd_24h_change'] > 0 else "#ff4444"
                self.btc_label.setText(f"BTC: ${btc['usd']:,.0f} ({btc['usd_24h_change']:+.2f}%)")
                self.btc_label.setStyleSheet(f"color: {btc_color}; font-weight: bold;")
                
                # Ethereum
                eth = data['ethereum']
                eth_color = "#00ff88" if eth['usd_24h_change'] > 0 else "#ff4444"
                self.eth_label.setText(f"ETH: ${eth['usd']:,.2f} ({eth['usd_24h_change']:+.2f}%)")
                self.eth_label.setStyleSheet(f"color: {eth_color}; font-weight: bold;")
                
                # BNB
                bnb = data['binancecoin']
                bnb_color = "#00ff88" if bnb['usd_24h_change'] > 0 else "#ff4444"
                self.bnb_label.setText(f"BNB: ${bnb['usd']:,.2f} ({bnb['usd_24h_change']:+.2f}%)")
                self.bnb_label.setStyleSheet(f"color: {bnb_color}; font-weight: bold;")
                
                # Update time
                now = datetime.now().strftime("%H:%M:%S")
                self.time_label.setText(now)
                
        except Exception as e:
            print(f"Error fetching prices: {e}")
            self.btc_label.setText("BTC: Error")
            self.eth_label.setText("ETH: Error")
            self.bnb_label.setText("BNB: Error")
