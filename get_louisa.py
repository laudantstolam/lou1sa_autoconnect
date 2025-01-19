import sys
import json
import subprocess
import pandas as pd
import tempfile
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class StoreSearchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("門市查詢系統")
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

        # 下拉選單
        self.dropdown = QComboBox()
        layout.addWidget(self.dropdown)

        # 確認按鈕
        confirm_button = QPushButton("確認")
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

        # 初始化數據
        self.current_setting_index = 0
        self.preferences = []
        try:
            # 讀取 settings.json
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.preferences = settings.get("preference", [])
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取 settings.json 文件: {e}")

        try:
            self.df = pd.read_csv("data.csv")
            self.store_list = self.df[["門市名稱", "地址", "電話"]].fillna("")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法讀取 CSV 檔案: {e}")
            self.store_list = pd.DataFrame(columns=["門市名稱", "地址", "電話"])

        self.update_setting_display()
        self.update_dropdown()

    def change_setting(self, direction):
        self.current_setting_index = (self.current_setting_index + direction) % len(self.preferences)
        self.update_setting_display()
        self.sync_search_with_preference()

    def update_setting_display(self):
        if self.preferences:
            current_preference = self.preferences[self.current_setting_index]
            store_name = current_preference["name"]

            # 查找對應電話號碼
            matched_store = self.df[self.df["門市名稱"] == store_name]
            if not matched_store.empty:
                phone = matched_store["電話"].iloc[0]
            else:
                phone = "未找到電話號碼"

            self.setting_label.setText(f"{store_name} - {phone}")
        else:
            self.setting_label.setText("無偏好設定")

    def sync_search_with_preference(self):
        """將偏好設定同步到搜尋框並更新選項。"""
        if self.preferences:
            current_preference = self.preferences[self.current_setting_index]
            self.search_field.setText(current_preference["name"])

    def update_dropdown(self):
        search_text = self.search_field.text().strip().lower()
        if search_text:
            filtered_stores = self.store_list[
                self.store_list["門市名稱"].str.contains(search_text, case=False, na=False) |
                self.store_list["地址"].str.contains(search_text, case=False, na=False)
            ]
        else:
            filtered_stores = self.store_list

        self.dropdown.clear()
        for _, row in filtered_stores.iterrows():
            display_text = f"{row['門市名稱']} ({row['地址']})"
            self.dropdown.addItem(display_text)

    def confirm_selection(self):
        selected_store = self.dropdown.currentText()
        if selected_store:
            # 取得選擇的門市名稱
            store_name = selected_store.split(" (")[0]
            # 查找對應的電話號碼
            matched_store = self.df[self.df["門市名稱"] == store_name]
            if not matched_store.empty:
                phone = matched_store["電話"].iloc[0].replace("-", "")           
                # WIFI邏輯
                if len(phone) == 10:
                ### 雙北通常是末八碼
                    new_password = phone[-8:]
                elif len(phone) == 9:
                ### 桃園新竹等只有九碼的會是末九碼
                    new_password = phone[-9:]
                else:
                ### 台積電門市等請自己加油
                    new_password = None

                # 呼叫更新 Wi-Fi 密碼的函數
                self.update_wifi_password("LouisaCoffee", new_password)
            else:
                QMessageBox.warning(self, "提示", f"未找到 {store_name} 的電話號碼")
        else:
            QMessageBox.warning(self, "提示", "請先選擇門市")

    def update_wifi_password(self, network_name, new_password):
        try:
            # First remove the existing profile
            subprocess.run(['netsh', 'wlan', 'delete', 'profile', network_name], check=True)
            
            # Create XML template for the new profile
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

            # Create a temporary file that will be automatically deleted
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
                temp_filename = temp_file.name
                temp_file.write(profile_template)
            
            try:
                # Add the new profile using the temporary file
                subprocess.run(['netsh', 'wlan', 'add', 'profile', f'filename="{temp_filename}"'], check=True)
                QMessageBox.information(self, "真是個成功的密碼小偷", f"目前Louisa的密碼為{new_password}")
                print(f"Successfully updated password for network: {network_name}")
            finally:
                # Make sure to remove the temporary file even if an error occurs
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