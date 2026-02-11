import sqlite3
from werkzeug.security import generate_password_hash
import os

print("=" * 60)
print("データベース初期化スクリプト")
print("=" * 60)

# 既存のデータベースをバックアップ
if os.path.exists('post_data.db'):
    if os.path.getsize('post_data.db') > 0:
        backup_name = 'post_data_backup.db'
        if os.path.exists(backup_name):
            os.remove(backup_name)
        os.rename('post_data.db', backup_name)
        print(f"既存のデータベースを {backup_name} にバックアップしました")

# 新しいデータベースを作成
conn = sqlite3.connect('post_data.db')
c = conn.cursor()

print("テーブルを作成中...")

# usersテーブル作成
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        icon_path TEXT,
        bio TEXT
    )
''')
print("usersテーブル作成")

# postsテーブル作成
c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        crowd_level TEXT NOT NULL,
        comment TEXT,
        timestamp TEXT NOT NULL
    )
''')
print("postsテーブル作成")

# ratingsテーブル作成
c.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        rating_type TEXT NOT NULL,
        UNIQUE(post_id, user_name)
    )
''')
print("ratingsテーブル作成")

# reservationsテーブル作成
c.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        people INTEGER NOT NULL,
        comment TEXT
    )
''')
print("reservationsテーブル作成")

print("\nユーザーアカウントを作成中...")

# adminアカウントを作成
admin_password = 'admin123'
admin_hash = generate_password_hash(admin_password)

c.execute('''
    INSERT INTO users (username, password, is_admin, icon_path, bio)
    VALUES (?, ?, ?, ?, ?)
''', ('admin', admin_hash, 1, 'uploads/icons/default.png', '管理者アカウント'))
print(f"adminアカウント作成")

# testアカウントを作成
test_password = 'test123'
test_hash = generate_password_hash(test_password)

c.execute('''
    INSERT INTO users (username, password, is_admin, icon_path, bio)
    VALUES (?, ?, ?, ?, ?)
''', ('test', test_hash, 0, 'uploads/icons/default.png', 'テストユーザー'))
print(f"testアカウント作成")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("データベースの初期化が完了しました！")
print("=" * 60)
print("\n作成されたアカウント:")
print("-" * 60)
print("【管理者アカウント】")
print(f"  ユーザー名: admin")
print(f"  パスワード: {admin_password}")
print(f"  権限: 管理者")
print("\n【テストアカウント】")
print(f"  ユーザー名: test")
print(f"  パスワード: {test_password}")
print(f"  権限: 一般ユーザー")
print("=" * 60)
print("\nログインURL: http://127.0.0.1:5000/login")
print("=" * 60)