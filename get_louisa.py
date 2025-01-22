import sys
import json
import subprocess
import csv
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


def get_resource_path(relative_path):
    """獲取資源文件的絕對路徑"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class StoreSearchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LouisaPro")
        self.setGeometry(200, 200, 400, 300)

        # 主佈局
        layout = QVBoxLayout()

        # 歡迎文字
        welcome_label = QLabel("歡迎使用路*莎密碼變更工具\npowered by @laudantstolam")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(welcome_label)

        # 偏好設定顯示與按鈕（水平佈局）
        settings_layout = QHBoxLayout()
        settings_layout.setAlignment(Qt.AlignCenter)

        self.left_button = QPushButton("◀")
        self.left_button.clicked.connect(lambda: self.change_setting(-1))

        self.setting_label = QLabel("")
        self.setting_label.setAlignment(Qt.AlignCenter)
        self.setting_label.setStyleSheet("font-size: 18px; margin: 0 10px;")

        self.right_button = QPushButton("▶")
        self.right_button.clicked.connect(lambda: self.change_setting(1))

        settings_layout.addWidget(self.left_button)
        settings_layout.addWidget(self.setting_label)
        settings_layout.addWidget(self.right_button)
        layout.addLayout(settings_layout)

        # 搜尋框
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("輸入門市名稱或地址以搜尋")
        self.search_field.textChanged.connect(self.update_dropdown)
        layout.addWidget(self.search_field)

        # 下拉選單和收藏按鈕的水平佈局
        dropdown_layout = QHBoxLayout()
        
        # 下拉選單
        self.dropdown = QComboBox()
        dropdown_layout.addWidget(self.dropdown)
        
        # 收藏按鈕
        self.favorite_button = QPushButton("☆")
        self.favorite_button.setFixedWidth(30)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        dropdown_layout.addWidget(self.favorite_button)
        
        layout.addLayout(dropdown_layout)

        # 確認按鈕
        confirm_button = QPushButton("確認")
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

        # 初始化數據
        self.current_setting_index = 0
        self.preferences = []
        self.settings_path = get_resource_path("settings.json")
        self.load_settings()
        
        self.store_list = []
        try:
            data_path = get_resource_path("data.csv")
            with open(data_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.store_list = [row for row in reader]
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取資料檔案: {e}")

        self.update_setting_display()
        self.update_dropdown()
        self.update_favorite_button()

    def load_settings(self):
        """載入設定檔"""
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.preferences = settings.get("preference", [])
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取設定文件: {e}")

    def save_settings(self):
        """儲存設定檔"""
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            settings["preference"] = self.preferences
            
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法儲存設定文件: {e}")

    def is_current_store_favorite(self):
        """檢查目前選擇的門市是否在收藏清單中"""
        if not self.dropdown.currentText():
            return False
        
        current_store = self.dropdown.currentText().split(" (")[0]
        return any(pref["name"] == current_store for pref in self.preferences)

    def update_favorite_button(self):
        """更新收藏按鈕的狀態"""
        if self.is_current_store_favorite():
            self.favorite_button.setText("★")
        else:
            self.favorite_button.setText("☆")

    def toggle_favorite(self):
        """切換當前選擇的門市的收藏狀態"""
        if not self.dropdown.currentText():
            return
            
        current_store = self.dropdown.currentText().split(" (")[0]
        
        try:
            # 直接讀取最新的 settings.json
            with open(self.settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            # 檢查是否已在收藏清單中
            is_favorite = any(pref["name"] == current_store for pref in settings["preference"])
            
            if is_favorite:
                # 從收藏清單中移除
                settings["preference"] = [pref for pref in settings["preference"] if pref["name"] != current_store]
                self.preferences = settings["preference"]
                QMessageBox.information(self, "提示", f"已將 {current_store} 從收藏清單中移除")
            else:
                new_preference = {"name": current_store}
                settings["preference"].append(new_preference)
                self.preferences = settings["preference"]
                QMessageBox.information(self, "提示", f"已將 {current_store} 加入收藏清單")
            
            # 直接寫入更新後的設定
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # 更新顯示
            self.update_setting_display()
            self.update_favorite_button()
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法更新收藏設定: {e}")
            return

    def change_setting(self, direction):
        self.current_setting_index = (self.current_setting_index + direction) % len(self.preferences)
        self.update_setting_display()
        self.sync_search_with_preference()

    def update_setting_display(self):
        if self.preferences:
            current_preference = self.preferences[self.current_setting_index]
            store_name = current_preference["name"]

            matched_store = next((store for store in self.store_list if store["門市名稱"] == store_name), None)
            if matched_store:
                addr = matched_store["地址"]
            else:
                addr = "未找到地址"

            self.setting_label.setText(f"<{store_name}>\n{addr}")
        else:
            self.setting_label.setText("尚未加入任何門市")

    def sync_search_with_preference(self):
        if self.preferences:
            current_preference = self.preferences[self.current_setting_index]
            self.search_field.setText(current_preference["name"])

    def update_dropdown(self):
        search_text = self.search_field.text().strip().lower()
        if search_text:
            filtered_stores = [
                store for store in self.store_list
                if search_text in store["門市名稱"].lower() or search_text in store["地址"].lower()
            ]
        else:
            filtered_stores = self.store_list

        current_text = self.dropdown.currentText()
        self.dropdown.clear()
        for store in filtered_stores:
            display_text = f"{store['門市名稱']} ({store['地址']})"
            self.dropdown.addItem(display_text)
            
        # 保持選擇狀態
        index = self.dropdown.findText(current_text)
        if index >= 0:
            self.dropdown.setCurrentIndex(index)
            
        self.update_favorite_button()

    def confirm_selection(self):
        selected_store = self.dropdown.currentText()
        if selected_store:
            store_name = selected_store.split(" (")[0]
            matched_store = next((store for store in self.store_list if store["門市名稱"] == store_name), None)
            if matched_store:
                phone = matched_store["電話"].replace("-", "")           
                if len(phone) == 10:
                    new_password = phone[-8:]
                elif len(phone) == 9:
                    new_password = phone[-9:]
                else:
                    new_password = None

                self.update_wifi_password("LouisaCoffee", new_password)
            else:
                QMessageBox.warning(self, "提示", f"未找到 {store_name} 的電話號碼")
        else:
            QMessageBox.warning(self, "提示", "請先選擇門市")

    def update_wifi_password(self, network_name, new_password):
        try:
            subprocess.run(['netsh', 'wlan', 'delete', 'profile', network_name], check=True)
            
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

            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(profile_template)
            
            try:
                subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename="{temp_filename}"'], check=True)
                QMessageBox.information(self, "真是個成功的密碼小偷", f"目前Louisa的密碼為{new_password}")
                print(f"Successfully updated password for network: {network_name}")
            finally:
                try:
                    os.unlink(temp_filename)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {e}")
                    
        except subprocess.CalledProcessError as e:
            print(f"Error updating network profile: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StoreSearchApp()
    window.show()
    sys.exit(app.exec_())