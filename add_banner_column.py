"""
add_banner_columns.py
データベースに banner_path と total_points カラムを追加するスクリプト

使用方法:
1. PowerShellで仮想環境に入る
   cd C:\systems\apps
   .\venv\Scripts\Activate.ps1

2. このスクリプトを実行
   python add_banner_columns.py
"""

import sys
import os

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_app import app, db
    from models import User
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("main_app または models が見つかりません")
    sys.exit(1)


def add_banner_columns():
    """usersテーブルにbanner_pathとtotal_pointsカラムを追加"""
    
    print("=" * 50)
    print("バナーシステム用カラム追加スクリプト")
    print("=" * 50)
    
    with app.app_context():
        # banner_path カラムを追加
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
            print("banner_path カラムを追加しました")
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate column name" in error_msg or "already exists" in error_msg:
                print("banner_path カラムは既に存在します")
            else:
                print(f"banner_path 追加エラー: {e}")
        
        # total_points カラムを追加
        try:
            db.engine.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
            print("total_points カラムを追加しました")
        except Exception as e:
            error_msg = str(e).lower()
            if "duplicate column name" in error_msg or "already exists" in error_msg:
                print("total_points カラムは既に存在します")
            else:
                print(f"total_points 追加エラー: {e}")
        
        # テーブル構造を確認
        print("\n" + "=" * 50)
        print("現在のusersテーブルのカラム:")
        print("=" * 50)
        
        try:
            # SQLiteの場合
            result = db.engine.execute("PRAGMA table_info(users)")
            for row in result:
                col_name = row[1]
                col_type = row[2]
                print(f"  ✓ {col_name:20s} ({col_type})")
        except:
            # MySQLなどの場合
            try:
                result = db.engine.execute("DESCRIBE users")
                for row in result:
                    print(f"  ✓ {row[0]:20s} ({row[1]})")
            except Exception as e:
                print(f"テーブル情報の取得に失敗: {e}")
        
        print("=" * 50)
        print("完了しました！")
        print("=" * 50)


if __name__ == '__main__':
    try:
        add_banner_columns()
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)