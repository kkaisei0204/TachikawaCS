# 今回の制作で参考にさせてもらった動画 
# https://youtu.be/8PPvgexhmYg
# https://www.youtube.com/watch?v=6aD024WZfCs
# https://www.youtube.com/watch?v=mwjrtntk0PE

# データベース初期化
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()


# ユーザークラス
# ユーザー（ログイン用）。管理者フラグやプロフィール情報もここで
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    icon_path = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    # リレーション: ユーザーの投稿一覧
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

# 混雑投稿。店舗ごとの状況やコメントを残す
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(200), nullable=False)
    crowd_level = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.String(100), nullable=False)

    # 外部キー（ユーザー削除時の連動などに使う）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<Post {self.shop_name} by {self.user_name}>"

# 店舗マスタ（将来拡張用）。今は説明情報は SHOP_DETAILS 側が中心。
class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # 必要に応じて、Reservationモデルとのリレーションも定義
    reservations = db.relationship('Reservation', backref='shop', lazy=True)
    
    def __repr__(self):
        return f"<Shop {self.name}>"    
       
# 予約（デモ枠）。混雑投稿とは別で、予約の流れを見せるためのテーブルです。
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    people = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 将来的な拡張のため外部キーも残す（nullable=True）
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=True)
    
    def __repr__(self):
        return f'<Post {self.shop_name} by {self.user_name}>'
