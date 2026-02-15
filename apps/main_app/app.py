# このファイルはFlaskアプリのエントリーポイントで、アプリの初期化とルートの登録を行います。
# このファイルはアプリ全体の設定と構成を担う重要な役割を持っています。
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
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash # パスワードハッシュ化用

# プロジェクトルートをパスに追加します
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# .env を読みます(DBや秘密鍵など)
load_dotenv()

# 循環参照回避のため、まずdbをインポートし、その後にmodelsを読み込みます
from apps.main_app.db import db
from apps.main_app.models import User, Post

# Flaskアプリを生成します
app = Flask(__name__, template_folder="../top_page/templates", static_folder="../top_page/static")

# 設定
# 絶対パスを取得します
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 画像のアップロード先を設定します
UPLOAD_FOLDER = os.path.join(basedir, "apps", "main_app", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# データベースは post_data.db に統一します。
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') or f'sqlite:///{os.path.join(basedir, "post_data.db")}'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースとアプリを紐付け
db.init_app(app)

# Flask-Login 設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# ユーザーローダーを定義します。ユーザーIDからユーザーオブジェクトを取得するために使用されます。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintを登録
# 画面/機能ごとに Blueprint を分割しています（ルートが肥大化しないように）。
from apps.main_app.main_routes import main_bp
from apps.post_page.post_routes import post_bp
from apps.topics_page.topics_routes import topics_bp
app.register_blueprint(main_bp)
app.register_blueprint(post_bp)
app.register_blueprint(topics_bp)

# データベーステーブル作成と管理者アカウント初期化
# 初回起動でテーブル作成＆管理者の用意をします。
with app.app_context():
    db.create_all()
    # 管理者アカウントが存在しない場合は作成します。
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(
            username='admin', 
            password=generate_password_hash('admin123'), # パスワードを安全にハッシュ化 
            is_admin=True, 
            icon_path='uploads/icons/default.png',  
            bio='管理者アカウントです'              
        )
        # 管理者アカウントをデータベースに追加します。
        db.session.add(admin)
        db.session.commit()
        print("統合DB(post_data.db)に管理者アカウント(admin/admin123)を作成しました")

if __name__ == "__main__":
    app.run(debug=True)