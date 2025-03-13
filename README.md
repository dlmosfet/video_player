# Flask Video Player（開發中）

這是一個基於 Flask 的影片瀏覽和播放網站，允許用戶上傳影片並觀看影片內容。該應用會自動生成影片縮圖，並提供簡單的影片播放功能。

## 技術棧

- **Flask**：用於構建後端 API 和前端渲染
- **Werkzeug**：用於安全處理檔名
- **Flask-WTF 和 WTForms**：處理影片上傳的表單
- **FFmpeg**：用於生成影片縮圖

## 安裝依賴

首先，確保安裝了 Python 以及必要的庫。可以使用以下命令安裝 Python 依賴：

```bash
pip install Flask Werkzeug Flask-WTF WTForms

## 文件結構
flask-video-player/
│
├── app.py              # Flask 應用主程式
├── static/             # 用於儲存上傳的影片和縮圖
│   └── uploads/
├── templates/          # 用於存放 HTML 模板
│   ├── upload.html
│   └── play_video.html
├── requirements.txt    # 依賴項列表
└── README.md           # 這個文件

