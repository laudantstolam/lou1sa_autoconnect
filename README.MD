### Intro
平常在不同的路*莎總需要清除網路設定再重新連線有點麻煩，所以搞了一個可以輸入店名或地址後自動設定wifi密碼的小工具
![](https://i.imgur.com/OOLF0L8.jpeg)

### Usage
python搞下去或是用packed/Lo*isaPro.exe執行
可以設定`settings.json`裡面的常用店名

`pip install -r requirements.txt`
`python get_louisa.py`

### RELEASE HISTORY
`V1.0` 2024.01.19 
`V1.1` 2024.01.22 加入"最愛門市"功能

### Interface
![](https://raw.githubusercontent.com/Ash0645/image_remote/main/20250122125138.png)

### CONFIRM
`netsh wlan show profiles` 顯示介面 Wi-Fi 上的設定檔

`netsh wlan show profile name="LouisaCoffee" key=clear` 查看路*莎目前的wifi密碼
### TODO
- 美化介面ERRRRR 現在好醜
- 支援MAC用戶
- 如果本身有連網的話其實可以直接從經緯度去抓(更自動了)

---

### SOMETHING I USED : D
`pyreq .` 生成requirements.txt

`pyinstaller --onefile --windowed --add-data "settings.json;." --add-data "data.csv;." get_louisa.py` 打包exe的指令

- 打包的時候注意一下環境不要有pendas不然會包不起來(包太大)