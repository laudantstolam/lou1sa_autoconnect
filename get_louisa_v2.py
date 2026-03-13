import sys
import json
import subprocess
import csv
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFrame,
    QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QFontDatabase, QPalette, QColor


# ---------------------------------------------------------------------------
# Resource path helper (PyInstaller compatibility)
# ---------------------------------------------------------------------------

def get_resource_path(relative_path):
    """Return the absolute path to a bundled (read-only) resource."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_writable_path(filename):
    """Return a writable path next to the exe (or cwd in dev mode)."""
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, filename)
    # Auto-create settings.json if missing
    if filename == "settings.json" and not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            import json
            json.dump({"preference": []}, f)
    return path


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------

BG        = "#1A1614"
CARD      = "#2A201C"
CARD_ALT  = "#332820"
ACCENT    = "#C4A882"
ACCENT_HV = "#D4B896"
TEXT      = "#F5F0EB"
MUTED     = "#8B9098"
BORDER    = "#3D2E26"
SUCCESS   = "#7CBF8E"
ERROR     = "#E07070"

RADIUS = "8px"

APP_QSS = f"""
/* ── Root ─────────────────────────────────────────────────────────────── */
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Inter", "Segoe UI", "Microsoft JhengHei", sans-serif;
    font-size: 13px;
}}

/* ── Generic frame / card ─────────────────────────────────────────────── */
QFrame#card {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
}}

/* ── Title area ───────────────────────────────────────────────────────── */
QLabel#appTitle {{
    font-size: 22px;
    font-weight: 700;
    color: {ACCENT};
    letter-spacing: 1px;
}}
QLabel#appSubtitle {{
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 0.5px;
}}

/* ── Carousel / favorites card ────────────────────────────────────────── */
QFrame#carouselCard {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 4px;
}}
QLabel#carouselStoreName {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT};
    background-color: transparent;
}}
QLabel#carouselAddress {{
    font-size: 11px;
    color: {MUTED};
    background-color: transparent;
}}
QLabel#carouselEmpty {{
    font-size: 12px;
    color: {MUTED};
    font-style: italic;
    background-color: transparent;
    qproperty-alignment: AlignCenter;
}}
QLabel#carouselCounter {{
    font-size: 10px;
    color: {MUTED};
    background-color: transparent;
}}

/* Arrow nav buttons */
QPushButton#arrowBtn {{
    background-color: transparent;
    color: {MUTED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-size: 14px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    padding: 0px;
}}
QPushButton#arrowBtn:hover {{
    background-color: {CARD_ALT};
    color: {ACCENT};
    border-color: {ACCENT};
}}
QPushButton#arrowBtn:pressed {{
    background-color: {BORDER};
}}
QPushButton#arrowBtn:disabled {{
    color: {BORDER};
    border-color: {BORDER};
}}

/* ── Section label ────────────────────────────────────────────────────── */
QLabel#sectionLabel {{
    font-size: 10px;
    font-weight: 600;
    color: {MUTED};
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* ── Search field ─────────────────────────────────────────────────────── */
QLineEdit#searchField {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 8px 12px;
    color: {TEXT};
    font-size: 13px;
    selection-background-color: {ACCENT};
    selection-color: {BG};
}}
QLineEdit#searchField:focus {{
    border-color: {ACCENT};
    background-color: {CARD_ALT};
}}
QLineEdit#searchField::placeholder {{
    color: {MUTED};
}}

/* ── Dropdown ──────────────────────────────────────────────────────────── */
QComboBox#storeDropdown {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    padding: 8px 12px;
    color: {TEXT};
    font-size: 13px;
    selection-background-color: {ACCENT};
}}
QComboBox#storeDropdown:hover {{
    border-color: {ACCENT};
}}
QComboBox#storeDropdown:focus {{
    border-color: {ACCENT};
    background-color: {CARD_ALT};
}}
QComboBox#storeDropdown::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox#storeDropdown::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border-left:  5px solid transparent;
    border-right: 5px solid transparent;
    border-top:   6px solid {MUTED};
    margin-right: 8px;
}}
QComboBox#storeDropdown QAbstractItemView {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {BG};
    outline: none;
    padding: 2px;
}}
QComboBox#storeDropdown QAbstractItemView::item {{
    min-height: 28px;
    padding: 4px 8px;
    border-radius: 4px;
}}
QComboBox#storeDropdown QAbstractItemView::item:hover {{
    background-color: {CARD_ALT};
    color: {ACCENT};
}}

/* ── Favorite star button ─────────────────────────────────────────────── */
QPushButton#starBtn {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
    color: {MUTED};
    font-size: 18px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    padding: 0px;
}}
QPushButton#starBtn:hover {{
    background-color: {CARD_ALT};
    border-color: {ACCENT};
    color: {ACCENT};
}}
QPushButton#starBtn:pressed {{
    background-color: {BORDER};
}}
QPushButton#starBtn[active="true"] {{
    color: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Confirm button ───────────────────────────────────────────────────── */
QPushButton#confirmBtn {{
    background-color: {ACCENT};
    color: {BG};
    border: none;
    border-radius: {RADIUS};
    font-size: 14px;
    font-weight: 700;
    padding: 12px 0px;
    letter-spacing: 0.5px;
}}
QPushButton#confirmBtn:hover {{
    background-color: {ACCENT_HV};
}}
QPushButton#confirmBtn:pressed {{
    background-color: {ACCENT};
}}
QPushButton#confirmBtn:disabled {{
    background-color: {BORDER};
    color: {MUTED};
}}

/* ── Status label ─────────────────────────────────────────────────────── */
QFrame#statusCard {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: {RADIUS};
}}
QLabel#statusLabel {{
    font-size: 12px;
    color: {MUTED};
    padding: 2px 0px;
    background-color: transparent;
}}
QLabel#statusLabel[state="success"] {{
    color: {SUCCESS};
}}
QLabel#statusLabel[state="error"] {{
    color: {ERROR};
}}
QLabel#statusPasswd {{
    font-size: 20px;
    font-weight: 700;
    color: {ACCENT};
    letter-spacing: 3px;
    background-color: transparent;
}}

/* ── Divider ──────────────────────────────────────────────────────────── */
QFrame#divider {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}

/* ── Scrollbar (dropdown popup) ───────────────────────────────────────── */
QScrollBar:vertical {{
    background: {CARD};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


# ---------------------------------------------------------------------------
# Main application widget
# ---------------------------------------------------------------------------

class StoreSearchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LouisaPro")
        self.setFixedSize(480, 560)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # ── state ──────────────────────────────────────────────────────────
        self.current_setting_index = 0
        self.preferences = []
        self.store_list = []
        self.settings_path = get_writable_path("settings.json")

        # ── load data ──────────────────────────────────────────────────────
        self.load_settings()
        try:
            data_path = get_resource_path("query_data/data.csv")
            with open(data_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.store_list = [row for row in reader]
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取資料檔案: {e}")

        # ── build UI ───────────────────────────────────────────────────────
        self._build_ui()

        # ── initial display ────────────────────────────────────────────────
        self.update_setting_display()
        self.update_dropdown()
        self.update_favorite_button()

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # ── Title ───────────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title_row.setSpacing(0)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        app_title = QLabel("LouisaPro")
        app_title.setObjectName("appTitle")
        title_col.addWidget(app_title)

        app_subtitle = QLabel("路易莎 WiFi 密碼工具  ·  powered by @laudantstolam")
        app_subtitle.setObjectName("appSubtitle")
        title_col.addWidget(app_subtitle)

        title_row.addLayout(title_col)
        title_row.addStretch()
        root.addLayout(title_row)

        # ── Divider ─────────────────────────────────────────────────────────
        root.addWidget(self._divider())

        # ── Favorites carousel ──────────────────────────────────────────────
        fav_label = QLabel("FAVOURITES")
        fav_label.setObjectName("sectionLabel")
        root.addWidget(fav_label)

        carousel_row = QHBoxLayout()
        carousel_row.setSpacing(8)

        self.left_button = QPushButton("\u25c0")          # ◀
        self.left_button.setObjectName("arrowBtn")
        self.left_button.clicked.connect(lambda: self.change_setting(-1))
        carousel_row.addWidget(self.left_button, 0, Qt.AlignVCenter)

        # card
        self.carousel_card = QFrame()
        self.carousel_card.setObjectName("carouselCard")
        self.carousel_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.carousel_card.setFixedHeight(80)
        card_inner = QVBoxLayout(self.carousel_card)
        card_inner.setContentsMargins(14, 10, 14, 10)
        card_inner.setSpacing(3)

        # Empty state label (shown when no favorites)
        self.carousel_empty = QLabel("尚未加入任何門市")
        self.carousel_empty.setObjectName("carouselEmpty")
        self.carousel_empty.setAlignment(Qt.AlignCenter)
        card_inner.addWidget(self.carousel_empty)

        # Content labels (shown when favorites exist)
        self.carousel_store_name = QLabel("")
        self.carousel_store_name.setObjectName("carouselStoreName")
        self.carousel_store_name.setAlignment(Qt.AlignCenter)
        self.carousel_store_name.setWordWrap(True)
        self.carousel_store_name.hide()
        card_inner.addWidget(self.carousel_store_name)

        self.carousel_address = QLabel("")
        self.carousel_address.setObjectName("carouselAddress")
        self.carousel_address.setAlignment(Qt.AlignCenter)
        self.carousel_address.setWordWrap(True)
        self.carousel_address.hide()
        card_inner.addWidget(self.carousel_address)

        self.carousel_counter = QLabel("")
        self.carousel_counter.setObjectName("carouselCounter")
        self.carousel_counter.setAlignment(Qt.AlignCenter)
        self.carousel_counter.hide()
        card_inner.addWidget(self.carousel_counter)

        carousel_row.addWidget(self.carousel_card)

        self.right_button = QPushButton("\u25b6")         # ▶
        self.right_button.setObjectName("arrowBtn")
        self.right_button.clicked.connect(lambda: self.change_setting(1))
        carousel_row.addWidget(self.right_button, 0, Qt.AlignVCenter)

        root.addLayout(carousel_row)

        # ── Divider ─────────────────────────────────────────────────────────
        root.addWidget(self._divider())

        # ── Search ──────────────────────────────────────────────────────────
        search_label = QLabel("SEARCH STORES")
        search_label.setObjectName("sectionLabel")
        root.addWidget(search_label)

        self.search_field = QLineEdit()
        self.search_field.setObjectName("searchField")
        self.search_field.setPlaceholderText("  \u2315  輸入門市名稱或地址以搜尋")   # ⌵
        self.search_field.setMinimumHeight(40)
        self.search_field.textChanged.connect(self.update_dropdown)
        root.addWidget(self.search_field)

        # ── Dropdown + star ─────────────────────────────────────────────────
        dd_row = QHBoxLayout()
        dd_row.setSpacing(8)

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("storeDropdown")
        self.dropdown.setMinimumHeight(40)
        self.dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dropdown.currentIndexChanged.connect(self.update_favorite_button)
        dd_row.addWidget(self.dropdown)

        self.favorite_button = QPushButton("\u2606")      # ☆
        self.favorite_button.setObjectName("starBtn")
        self.favorite_button.setProperty("active", "false")
        self.favorite_button.clicked.connect(self.toggle_favorite)
        dd_row.addWidget(self.favorite_button)

        root.addLayout(dd_row)

        # ── Confirm ─────────────────────────────────────────────────────────
        self.confirm_btn = QPushButton("套用 WiFi 密碼")
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setMinimumHeight(48)
        self.confirm_btn.clicked.connect(self.confirm_selection)
        root.addWidget(self.confirm_btn)

        # ── Status card ─────────────────────────────────────────────────────
        self.status_card = QFrame()
        self.status_card.setObjectName("statusCard")
        status_inner = QVBoxLayout(self.status_card)
        status_inner.setContentsMargins(16, 10, 16, 10)
        status_inner.setSpacing(4)

        self.status_label = QLabel("準備就緒")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_inner.addWidget(self.status_label)

        self.status_passwd = QLabel("")
        self.status_passwd.setObjectName("statusPasswd")
        self.status_passwd.setAlignment(Qt.AlignCenter)
        self.status_passwd.hide()
        status_inner.addWidget(self.status_passwd)

        root.addWidget(self.status_card)
        root.addStretch()

        self.setLayout(root)

    # -----------------------------------------------------------------------
    # Helper: divider line
    # -----------------------------------------------------------------------

    def _divider(self):
        line = QFrame()
        line.setObjectName("divider")
        line.setFrameShape(QFrame.HLine)
        return line

    # -----------------------------------------------------------------------
    # Settings / data I/O  (identical logic to v1)
    # -----------------------------------------------------------------------

    def load_settings(self):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.preferences = settings.get("preference", [])
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取設定文件: {e}")

    def save_settings(self):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            settings["preference"] = self.preferences
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法儲存設定文件: {e}")

    # -----------------------------------------------------------------------
    # Favorites carousel logic  (identical to v1)
    # -----------------------------------------------------------------------

    def is_current_store_favorite(self):
        if not self.dropdown.currentText():
            return False
        current_store = self.dropdown.currentText().split(" (")[0]
        return any(pref["name"] == current_store for pref in self.preferences)

    def update_favorite_button(self):
        is_fav = self.is_current_store_favorite()
        self.favorite_button.setText("\u2605" if is_fav else "\u2606")   # ★ / ☆
        self.favorite_button.setProperty("active", "true" if is_fav else "false")
        # Re-polish so Qt picks up the dynamic property change
        self.favorite_button.style().unpolish(self.favorite_button)
        self.favorite_button.style().polish(self.favorite_button)

    def toggle_favorite(self):
        if not self.dropdown.currentText():
            return
        current_store = self.dropdown.currentText().split(" (")[0]
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            is_favorite = any(pref["name"] == current_store for pref in settings["preference"])

            if is_favorite:
                settings["preference"] = [
                    p for p in settings["preference"] if p["name"] != current_store
                ]
                self.preferences = settings["preference"]
                self._set_status(f"已將 {current_store} 從收藏清單中移除", "")
            else:
                settings["preference"].append({"name": current_store})
                self.preferences = settings["preference"]
                self._set_status(f"已將 {current_store} 加入收藏清單", "")

            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            self.update_setting_display()
            self.update_favorite_button()

        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法更新收藏設定: {e}")

    def change_setting(self, direction):
        if not self.preferences:
            return
        self.current_setting_index = (self.current_setting_index + direction) % len(self.preferences)
        self.update_setting_display()
        self.sync_search_with_preference()

    def update_setting_display(self):
        if self.preferences:
            pref = self.preferences[self.current_setting_index]
            store_name = pref["name"]
            matched = next(
                (s for s in self.store_list if s["門市名稱"] == store_name), None
            )
            addr = matched["地址"] if matched else "未找到地址"
            total = len(self.preferences)

            self.carousel_empty.hide()
            self.carousel_store_name.setText(store_name)
            self.carousel_store_name.show()
            self.carousel_address.setText(addr)
            self.carousel_address.show()
            self.carousel_counter.setText(f"{self.current_setting_index + 1} / {total}")
            self.carousel_counter.show()

            has_multiple = total > 1
            self.left_button.setEnabled(has_multiple)
            self.right_button.setEnabled(has_multiple)
        else:
            self.carousel_empty.show()
            self.carousel_store_name.hide()
            self.carousel_address.hide()
            self.carousel_counter.hide()
            self.left_button.setEnabled(False)
            self.right_button.setEnabled(False)

    def sync_search_with_preference(self):
        if self.preferences:
            pref = self.preferences[self.current_setting_index]
            self.search_field.setText(pref["name"])

    # -----------------------------------------------------------------------
    # Dropdown  (identical logic to v1)
    # -----------------------------------------------------------------------

    def update_dropdown(self):
        search_text = self.search_field.text().strip().lower()
        if search_text:
            filtered = [
                s for s in self.store_list
                if search_text in s["門市名稱"].lower() or search_text in s["地址"].lower()
            ]
        else:
            filtered = self.store_list

        current_text = self.dropdown.currentText()
        self.dropdown.blockSignals(True)
        self.dropdown.clear()
        for store in filtered:
            self.dropdown.addItem(f"{store['門市名稱']} ({store['地址']})")
        self.dropdown.blockSignals(False)

        idx = self.dropdown.findText(current_text)
        if idx >= 0:
            self.dropdown.setCurrentIndex(idx)

        self.update_favorite_button()

    # -----------------------------------------------------------------------
    # Confirm / WiFi update  (identical logic to v1)
    # -----------------------------------------------------------------------

    def confirm_selection(self):
        selected = self.dropdown.currentText()
        if not selected:
            self._set_status("請先選擇門市", "", state="error")
            return

        store_name = selected.split(" (")[0]
        matched = next((s for s in self.store_list if s["門市名稱"] == store_name), None)
        if matched:
            phone = matched["電話"].replace("-", "")
            if len(phone) == 10:
                new_password = phone[-8:]
            elif len(phone) == 9:
                new_password = phone[-9:]
            else:
                new_password = None
            self.update_wifi_password("LouisaCoffee", new_password)
        else:
            self._set_status(f"未找到 {store_name} 的電話號碼", "", state="error")

    def update_wifi_password(self, network_name, new_password):
        try:
            subprocess.run(
                ['netsh', 'wlan', 'delete', 'profile', network_name],
                check=True
            )

            profile_template = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{network_name}</name>
    <SSIDConfig>
        <SSID>
            <name>{network_name}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{new_password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.xml', delete=False
            ) as tmp:
                tmp_name = tmp.name
                tmp.write(profile_template)

            try:
                subprocess.run(
                    ['netsh', 'wlan', 'add', 'profile', f'filename="{tmp_name}"'],
                    check=True
                )
                self._set_status("WiFi 密碼已成功套用", new_password, state="success")
                print(f"Successfully updated password for network: {network_name}")
            finally:
                try:
                    os.unlink(tmp_name)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {e}")

        except subprocess.CalledProcessError as e:
            self._set_status("netsh 指令執行失敗", "", state="error")
            print(f"Error updating network profile: {e}")
        except Exception as e:
            self._set_status(f"發生錯誤: {e}", "", state="error")
            print(f"An error occurred: {e}")

    # -----------------------------------------------------------------------
    # Status area helper
    # -----------------------------------------------------------------------

    def _set_status(self, message: str, password: str = "", state: str = ""):
        """Update the status card.  state = '' | 'success' | 'error'"""
        self.status_label.setText(message)
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

        if password:
            self.status_passwd.setText(password)
            self.status_passwd.show()
        else:
            self.status_passwd.setText("")
            self.status_passwd.hide()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)

    # Optional: attempt to load Inter if it's installed on the system
    font = QFont("Inter")
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = StoreSearchApp()
    window.show()
    sys.exit(app.exec_())
