### Intro
平常在不同的路*莎總需要清除網路設定再重新連線有點麻煩，所以搞了一個可以輸入店名或地址後自動設定wifi密碼的小工具
![](https://i.imgur.com/OOLF0L8.jpeg)

### Usage
python搞下去或是用packed/Lo*isaPro.exe執行
可以設定`settings.json`裡面的常用店名

### Interface
![](https://raw.githubusercontent.com/Ash0645/image_remote/main/20250119232208.png)

### CHECK
`netsh wlan show profiles` 顯示介面 Wi-Fi 上的設定檔
`netsh wlan show profile name="LouisaCoffee" key=clear` 查看路*莎目前的wifi密碼
### TODO
- 美化介面ERRRRR 現在好醜
- 支援MAC用戶
- 如果本身有連網的話其實可以直接從經緯度去抓(更自動了)