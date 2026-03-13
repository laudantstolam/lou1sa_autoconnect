## Intro
平常在不同的路*莎總需要清除網路設定再重新連線有點麻煩，所以搞了一個可以輸入店名或地址後自動設定wifi密碼的小工具

~~畢竟密碼總是門市電話號碼~~
![](https://i.imgur.com/OOLF0L8.jpeg)

## Usage
`LouisaPro_V2.exe` : Basic ver.
`LouisaPro_V2_neat.exe` : Vibed GUI ver.

### RELEASE HISTORY
`V1.0` 2024.01.19 
`V1.1` 2024.01.22 加入"最愛門市"功能
`V2.0` 2026.03.13 更新店鋪與UI

### Interface
#### 舊版:

![](https://raw.githubusercontent.com/Ash0645/image_remote/main/20260313130515.png)

#### 新版:

![](https://raw.githubusercontent.com/Ash0645/image_remote/main/20260313130856.png)

### Manual Confirmation
`netsh wlan show profiles` 顯示介面 Wi-Fi 上的設定檔
`netsh wlan show profile name="LouisaCoffee" key=clear` 查看路*莎目前的wifi密碼

### TODO
- 支援MAC用戶
- 如果本身有連網的話其實可以直接從經緯度去抓(更自動了)


### SOMETHING I USED : D
- `pyreq .` 生成requirements.txt

#### exe packing
- with python `pyinstaller --onefile --windowed --noconsole --icon=loui.ico --add-data "settings.json;." --add-data "data.csv;." get_louisa.py`
- with uv `uv run --with pyinstaller,PyQt5 pyinstaller   --onefile --windowed --name LouisaPro_V2_neat --add-data "query_data/data.csv;query_data"  get_louisa.py`
- 打包的時候注意一下環境不要有pendas不然會包不起來(它引用了太多東西，遞迴深度很深)
