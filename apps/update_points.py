"""
update_points.py
既存ユーザーのポイントを計算するスクリプト

計算式:
- 投稿数 × 10pt
- 「役に立った」数 × 5pt

使用方法:
1. PowerShellで仮想環境に入る
   cd C:\systems\apps
   .\venv\Scripts\Activate.ps1

2. このスクリプトを実行
   python update_points.py
"""

import sys
import os

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_app import app, db
    from models import User, Post
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("main_app または models が見つかりません")
    sys.exit(1)


def update_all_points():
    """全ユーザーのポイントを再計算"""
    
    print("=" * 60)
    print("ユーザーポイント計算スクリプト")
    print("=" * 60)
    print("計算式: 投稿数×10pt + 役に立った数×5pt")
    print("=" * 60)
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("ユーザーが見つかりません")
            return
        
        print(f"\n{len(users)}人のユーザーのポイントを計算中...\n")
        
        total_updated = 0
        
        for user in users:
            # ユーザーの投稿を取得
            posts = Post.query.filter_by(user_id=user.id).all()
            
            # ポイント計算
            post_points = len(posts) * 10
            helpful_points = sum((post.helpful_count or 0) for post in posts) * 5
            total_points = post_points + helpful_points
            
            # DB更新
            user.total_points = total_points
            total_updated += 1
            
            # 表示
            status = ""if total_points >= 500 else "  "
            print(f"{status} {user.username:20s} | {len(posts):3d}投稿 | {total_points:4d}pt")
        
        # 一括コミット
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"{total_updated}人のユーザーのポイントを更新しました")
        print("=" * 60)
        
        # 500pt以上のユーザーを表示
        high_point_users = [u for u in users if (u.total_points or 0) >= 500]
        if high_point_users:
            print(f"\nバナー設定可能なユーザー（500pt以上）: {len(high_point_users)}人")
            for user in high_point_users:
                print(f"   - {user.username}: {user.total_points}pt")
        else:
            print("\n現在、500pt以上のユーザーはいません")
        
        print("=" * 60)


if __name__ == '__main__':
    try:
        update_all_points()
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
