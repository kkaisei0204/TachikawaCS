import sqlite3
from werkzeug.security import generate_password_hash
import os

DB_NAME = 'post_data.db'

print("=" * 60)
print("統合データベース初期化スクリプト (Ver 2.0)")
print("=" * 60)

# バックアップ処理
if os.path.exists(DB_NAME):
    backup_name = DB_NAME + '.bak'
    if os.path.exists(backup_name): os.remove(backup_name)
    os.rename(DB_NAME, backup_name)
    print(f"既存のDBを {backup_name} に退避しました。")

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# 1. usersテーブル (ポイント・バナー・アイコン・管理権限を統合)
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        icon_path TEXT DEFAULT 'uploads/icons/default.png',
        banner_path TEXT,
        bio TEXT,
        total_points INTEGER DEFAULT 0
    )
''')

# 2. postsテーブル (混雑状況投稿)
c.execute('''
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        crowd_level TEXT NOT NULL,
        comment TEXT,
        timestamp TEXT NOT NULL,
        helpful_count INTEGER DEFAULT 0
    )
''')

# 3. ratingsテーブル (👍評価の重複防止用)
c.execute('''
    CREATE TABLE ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        rating_type TEXT NOT NULL,
        UNIQUE(post_id, user_name)
    )
''')

# 4. reservationsテーブル (予約機能用)
c.execute('''
    CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        people INTEGER NOT NULL,
        comment TEXT
    )
''')

# 初期アカウント作成 (admin / test)
accounts = [
    ('admin', 'admin123', 1, '管理者です'),
    ('test', 'test123', 0, 'テストユーザーです')
]

for uname, pwd, admin_flag, bio in accounts:
    hashed_pwd = generate_password_hash(pwd)
    c.execute('''
        INSERT INTO users (username, password, is_admin, bio, icon_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (uname, hashed_pwd, admin_flag, bio, 'uploads/icons/default.png'))

conn.commit()
conn.close()

print("\n[成功] すべてのテーブルを post_data.db に統合しました。")
print("ログイン情報: admin / admin123")