# 今回の制作で参考にさせてもらった動画 
# https://www.youtube.com/watch?v=mW0_60SRr3s
# https://www.youtube.com/watch?v=Gyy1tzwenc8
# https://www.youtube.com/watch?v=1EkuLcEneaA&t=2559s
# https://www.youtube.com/watch?v=irP4ZRFXhD0&t=3420s

# 参考サイト
# https://flask-sqlalchemy.readthedocs.io/en/stable/
# 管理者アカウント参考↓
# https://www.reddit.com/r/flask/comments/q8spq6/how_to_restrict_access_to_admin_panel_in_flask/?tl=ja

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

# .env を読む（DBや秘密鍵など）
load_dotenv()

# models.pyからインポート
from apps.main_app.models import db, User

# Flaskアプリを生成
app = Flask(__name__, template_folder="../top_page/templates", static_folder="../top_page/static")

# 絶対パスを取得
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

UPLOAD_FOLDER = os.path.join(basedir, "apps", "main_app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') or f'sqlite:///{os.path.join(basedir, "memo.db")}'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースとアプリを紐付け
db.init_app(app)

# Flask-Login 設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintを登録
# 画面/機能ごとに Blueprint を分割しています（ルートが肥大化しないように）。
from apps.main_app.main_routes import main_bp
from apps.post_page.post_routes import post_bp
from apps.reservation_page.reservation_routes import reservation_bp
from apps.topics_page.topics_routes import topics_bp
from apps.restaurant_page.restaurant_routes import restaurant_bp  # ← 追加
app.register_blueprint(main_bp)
app.register_blueprint(post_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(topics_bp)
app.register_blueprint(restaurant_bp)  # ← 追加

# データベーステーブル作成と管理者アカウント初期化
# 初回起動でテーブル作成＆管理者の用意をします。
# ※運用で不要なら、ここは「手動で作る」に寄せた方が安全です（誤配布を避けるため）。
with app.app_context():
    db.create_all()
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(
            
            username='admin', 
            password='admin', 
            is_admin=True, 
            icon_path='main_app/uploads/icon.png',  
            bio='管理者アカウントです'              
        )
        db.session.add(admin)
        db.session.commit()
        print("管理者アカウント(admin/admin)を作成しました")
        
if __name__ == "__main__":
    app.run(debug=True)
