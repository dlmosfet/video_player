import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'your_secret_key'

VIDEO_DIR = "static/videos"
THUMBNAIL_DIR = "static/thumbnails"
SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv'}

# 確保影片與縮圖資料夾存在
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# 影片上傳表單
class UploadForm(FlaskForm):
    category = SelectField('選擇分類', choices=[], validators=[DataRequired()])
    new_category = StringField('或輸入新分類')
    video = FileField('選擇影片', validators=[DataRequired()])
    submit = SubmitField('上傳')

# 取得分類清單
def get_categories():
    return [d for d in os.listdir(VIDEO_DIR) if os.path.isdir(os.path.join(VIDEO_DIR, d))] or ['無分類']

# 取得影片清單
def get_video_files():
    video_files = {}
    for category in get_categories():
        category_path = os.path.join(VIDEO_DIR, category)
        videos = [f for f in os.listdir(category_path) if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]
        if videos:
            video_files[category] = sorted(videos)
    return video_files

# 產生影片縮圖
def generate_thumbnail(video_path, thumbnail_path):
    if not os.path.exists(thumbnail_path):  # 避免重複生成
        cmd = f"ffmpeg -i \"{video_path}\" -ss 00:00:05 -vframes 1 \"{thumbnail_path}\""
        try:
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"❌ 縮圖生成失敗: {e}")

# 搜尋影片
def search_videos(query):
    result = {}
    query = query.lower()
    for category in get_categories():
        category_path = os.path.join(VIDEO_DIR, category)
        matched_videos = [f for f in os.listdir(category_path) if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS and query in f.lower()]
        if matched_videos:
            result[category] = sorted(matched_videos)
    return result

@app.route('/')
def index():
    return render_template('index.html', video_files=get_video_files())

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    form.category.choices = [(cat, cat) for cat in get_categories()]

    if form.validate_on_submit():
        video = form.video.data
        category = form.category.data.strip()
        new_category = form.new_category.data.strip()

        if new_category:
            category = new_category
            os.makedirs(os.path.join(VIDEO_DIR, category), exist_ok=True)

        filename = secure_filename(video.filename)
        if os.path.splitext(filename)[1].lower() not in SUPPORTED_FORMATS:
            flash('❌ 不支援的影片格式！')
            return redirect(url_for('upload'))

        try:
            video_path = os.path.join(VIDEO_DIR, category, filename)
            video.save(video_path)

            # 產生縮圖
            thumbnail_path = os.path.join(THUMBNAIL_DIR, f"{filename}.jpg")
            generate_thumbnail(video_path, thumbnail_path)

            flash('✅ 影片上傳成功！')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'❌ 上傳失敗: {str(e)}')
            return redirect(url_for('upload'))

    return render_template('upload.html', form=form)

@app.route('/videos/<category>/<filename>')
def video(category, filename):
    return send_from_directory(os.path.join(VIDEO_DIR, category), filename)

@app.route('/play/<category>/<filename>')
def play_video(category, filename):
    return render_template('video_player.html', category=category, filename=filename)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    search_results = get_video_files()  # 預設顯示所有影片

    if query:
        search_results = search_videos(query)

    # 根據選擇的分類篩選影片
    if category_filter:
        search_results = {category: videos for category, videos in search_results.items() if category == category_filter}

    return render_template('index.html', video_files=search_results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
