"""
grant_points.py
テスト用：特定のユーザーに直接ポイントを付与するスクリプト

使用方法:
1. このファイルをプロジェクトのルートディレクトリに配置
   /systems/grant_points.py

2. Pythonで実行
   python grant_points.py

3. プロンプトに従ってユーザー名とポイント数を入力
"""

import sys
import os

# systemsディレクトリをPythonパスに追加
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from apps.main_app.app import app, db
from apps.main_app.models import User

def grant_points_to_user():
    """指定したユーザーにポイントを付与"""
    
    print("=" * 60)
    print("ポイント付与スクリプト")
    print("=" * 60)
    
    with app.app_context():
        # 全ユーザーを表示
        users = User.query.all()
        
        if not users:
            print("ユーザーが見つかりません")
            return
        
        print("\n現在のユーザー一覧:")
        print("-" * 60)
        for i, user in enumerate(users, 1):
            current_points = getattr(user, 'total_points', 0) or 0
            admin_mark = " [管理者]" if user.is_admin else ""
            print(f"{i:2d}. {user.username:20s} | {current_points:5d}pt{admin_mark}")
        print("-" * 60)
        
        # ユーザー名を入力
        username = input("\nポイントを付与するユーザー名を入力してください: ").strip()
        
        # ユーザーを検索
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"ユーザー '{username}' が見つかりません")
            return
        
        # 現在のポイントを表示
        current_points = getattr(user, 'total_points', 0) or 0
        print(f"\n現在のポイント: {current_points}pt")
        
        # 付与するポイント数を入力
        print("\n付与するポイント数を入力してください:")
        print("  推奨: 5000pt (バナー設定に必要)")
        try:
            points = int(input("ポイント数: ").strip())
        except ValueError:
            print("無効な数値です")
            return
        
        if points < 0:
            print("0以上の値を入力してください")
            return
        
        # 確認
        new_total = current_points + points
        print("\n" + "=" * 60)
        print(f"ユーザー名: {username}")
        print(f"現在のポイント: {current_points}pt")
        print(f"付与するポイント: +{points}pt")
        print(f"付与後のポイント: {new_total}pt")
        print("=" * 60)
        
        confirm = input("\nこの内容で実行しますか？ (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("キャンセルしました")
            return
        
        # ポイントを付与
        if not hasattr(user, 'total_points'):
            # カラムが存在しない場合は追加が必要
            print("total_pointsカラムが存在しません")
            print("先に add_banner_column.py を実行してください")
            return
        
        user.total_points = new_total
        db.session.commit()
        
        print("\n" + "=" * 60)
        print(f"{username} に {points}pt を付与しました！")
        print(f"現在のポイント: {new_total}pt")
        
        if new_total >= 5000:
            print("\nこのユーザーはバナー設定が可能です！")
            print("   プロフィール編集ページからバナー画像をアップロードできます")
        elif new_total >= 500:
            print(f"\nバナー設定まであと {5000 - new_total}pt です")
        
        print("=" * 60)


def reset_all_points():
    """全ユーザーのポイントをリセット（テスト用）"""
    
    print("=" * 60)
    print("全ユーザーポイントリセット")
    print("=" * 60)
    
    confirm = input("\n全ユーザーのポイントを0にリセットします。本当に実行しますか？ (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("キャンセルしました")
        return
    
    with app.app_context():
        users = User.query.all()
        
        for user in users:
            if hasattr(user, 'total_points'):
                user.total_points = 0
        
        db.session.commit()
        
        print(f"\n{len(users)}人のユーザーのポイントをリセットしました")


def show_menu():
    """メニュー表示"""
    print("\n" + "=" * 60)
    print("ポイント管理メニュー")
    print("=" * 60)
    print("1. ユーザーにポイントを付与")
    print("2. 全ユーザーのポイントをリセット（テスト用）")
    print("3. 終了")
    print("=" * 60)
    
    choice = input("選択してください (1-3): ").strip()
    return choice


if __name__ == '__main__':
    try:
        while True:
            choice = show_menu()
            
            if choice == '1':
                grant_points_to_user()
            elif choice == '2':
                reset_all_points()
            elif choice == '3':
                print("\n終了します")
                break
            else:
                print("無効な選択です")
            
            input("\nEnterキーを押して続行...")
    
    except KeyboardInterrupt:
        print("\n\n中断しました")
        sys.exit(0)
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
