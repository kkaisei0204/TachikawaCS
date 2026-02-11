"""
super_grant_points.py
データベースを自動で修正してポイントを付与する最強スクリプト

特徴:
- カラムがなければ自動で追加
- post_data.db と memo.db の両方に対応
- エラーを自動で修正

使用方法:
1. /systems/ に配置
2. python super_grant_points.py
3. 指示に従うだけ！
"""

import sqlite3
import os
import sys

def check_and_fix_database(db_path, db_name):
    """データベースをチェックして必要なカラムを追加"""
    
    print(f"\n{db_name} をチェック中...")
    
    if not os.path.exists(db_path):
        print(f"{db_path} が見つかりません（スキップ）")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # usersテーブルの存在確認
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print(f"{db_name}にusersテーブルがありません（スキップ）")
            conn.close()
            return False
        
        # 現在のカラムを取得
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        print(f"{db_name}のusersテーブル発見")
        print(f"現在のカラム: {', '.join(columns)}")
        
        # 必要なカラムを追加
        added = []
        
        if 'bonus_points' not in columns:
            try:
                c.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
                added.append('bonus_points')
            except Exception as e:
                print(f"bonus_points追加エラー: {e}")
        
        if 'evaluation_points' not in columns:
            try:
                c.execute('ALTER TABLE users ADD COLUMN evaluation_points INTEGER DEFAULT 0')
                added.append('evaluation_points')
            except Exception as e:
                print(f"evaluation_points追加エラー: {e}")
        
        if 'total_points' not in columns:
            try:
                c.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
                added.append('total_points')
            except Exception as e:
                print(f"total_points追加エラー: {e}")
        
        if 'banner_path' not in columns:
            try:
                c.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
                added.append('banner_path')
            except Exception as e:
                print(f" banner_path追加エラー: {e}")
        
        conn.commit()
        
        if added:
            print(f"追加したカラム: {', '.join(added)}")
        else:
            print(f"すべてのカラムが存在します")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"エラー: {e}")
        conn.close()
        return False


def show_users_from_db(db_path):
    """データベースからユーザー一覧を取得"""
    
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            conn.close()
            return []
        
        # カラムの存在を確認
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        # クエリを構築
        if 'total_points' in columns:
            query = '''
                SELECT 
                    username,
                    COALESCE(bonus_points, 0) as bonus,
                    COALESCE(evaluation_points, 0) as evaluation,
                    COALESCE(total_points, 0) as total
                FROM users
                ORDER BY total DESC
            '''
        elif 'bonus_points' in columns and 'evaluation_points' in columns:
            query = '''
                SELECT 
                    username,
                    COALESCE(bonus_points, 0) as bonus,
                    COALESCE(evaluation_points, 0) as evaluation,
                    COALESCE(bonus_points, 0) + COALESCE(evaluation_points, 0) as total
                FROM users
                ORDER BY total DESC
            '''
        else:
            query = '''
                SELECT 
                    username,
                    0 as bonus,
                    0 as evaluation,
                    0 as total
                FROM users
            '''
        
        c.execute(query)
        users = c.fetchall()
        conn.close()
        return users
    
    except Exception as e:
        print(f"ユーザー取得エラー: {e}")
        conn.close()
        return []


def grant_points_to_db(db_path, username, points):
    """指定したデータベースのユーザーにポイントを付与"""
    
    if not os.path.exists(db_path):
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # ユーザーの存在確認
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            conn.close()
            return False
        
        # カラムの存在確認
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        # ポイントを更新
        if 'bonus_points' in columns:
            c.execute("""
                UPDATE users 
                SET bonus_points = COALESCE(bonus_points, 0) + ? 
                WHERE username = ?
            """, (points, username))
        
        # total_pointsも更新
        if 'total_points' in columns:
            if 'bonus_points' in columns and 'evaluation_points' in columns:
                c.execute("""
                    UPDATE users 
                    SET total_points = COALESCE(bonus_points, 0) + COALESCE(evaluation_points, 0)
                    WHERE username = ?
                """, (username,))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"ポイント付与エラー: {e}")
        conn.close()
        return False


def main():
    """メイン処理"""
    
    print("=" * 60)
    print("スーパーポイント付与ツール")
    print("=" * 60)
    print("カラムの自動追加機能付き！")
    print("=" * 60)
    
    # データベースをチェック＆修正
    post_db = "post_data.db"
    memo_db = "memo.db"
    
    post_ok = check_and_fix_database(post_db, "post_data.db")
    memo_ok = check_and_fix_database(memo_db, "memo.db")
    
    if not post_ok and not memo_ok:
        print("\n使用可能なデータベースが見つかりません")
        print("   Flaskアプリを一度起動してデータベースを初期化してください")
        return
    
    # メインで使用するデータベースを決定
    main_db = post_db if post_ok else memo_db
    db_name = "post_data.db" if post_ok else "memo.db"
    
    print(f"\n{db_name} を使用します")
    
    # ユーザー一覧を表示
    users = show_users_from_db(main_db)
    
    if not users:
        print("\nユーザーが見つかりません")
        print("   まずユーザー登録を行ってください")
        return
    
    print("\n現在のユーザー一覧:")
    print("-" * 60)
    print(f"{'No':<4} {'ユーザー名':<20} {'ボーナス':<10} {'評価':<10} {'合計':<10}")
    print("-" * 60)
    
    for i, (username, bonus, evaluation, total) in enumerate(users, 1):
        banner_mark = "" if total >= 5000 else ""
        print(f"{i:<4} {username:<20} {bonus:<10} {evaluation:<10} {total:<10}{banner_mark}")
    
    print("-" * 60)
    print("バナー設定可能（5000pt以上）")
    print("-" * 60)
    
    # ユーザー名を入力
    username = input("\nポイントを付与するユーザー名: ").strip()
    
    if not username:
        print("ユーザー名が入力されていません")
        return
    
    # ユーザーの存在確認
    user_found = False
    current_total = 0
    for u, b, e, t in users:
        if u == username:
            user_found = True
            current_total = t
            break
    
    if not user_found:
        print(f"ユーザー '{username}' が見つかりません")
        return
    
    # ポイント数を入力
    print("\n付与するポイント数を入力してください:")
    print("  推奨: 5000pt (バナー設定に必要)")
    
    try:
        points = int(input("ポイント数: ").strip())
    except ValueError:
        print("無効な数値です")
        return
    
    if points <= 0:
        print("1以上の値を入力してください")
        return
    
    new_total = current_total + points
    
    # 確認
    print("\n" + "=" * 60)
    print(f"データベース: {db_name}")
    print(f"ユーザー名: {username}")
    print(f"現在のポイント: {current_total}pt")
    print(f"付与するポイント: +{points}pt")
    print(f"付与後のポイント: {new_total}pt")
    print("=" * 60)
    
    confirm = input(f"\n{username} に {points}pt を付与しますか？ (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("キャンセルしました")
        return
    
    # ポイントを付与
    print("\n処理中...")
    
    # post_data.dbに付与
    if post_ok:
        if grant_points_to_db(post_db, username, points):
            print(f"post_data.db に {points}pt を付与しました")
        else:
            print(f"post_data.db への付与に失敗")
    
    # memo.dbに付与
    if memo_ok:
        if grant_points_to_db(memo_db, username, points):
            print(f"memo.db に {points}pt を付与しました")
        else:
            print(f"memo.db への付与に失敗")
    
    print("\n" + "=" * 60)
    print(f"完了しました！")
    print(f"{username} の新しいポイント: {new_total}pt")
    
    if new_total >= 5000:
        print("\nこのユーザーはバナー設定が可能です！")
        print("   プロフィール編集ページからバナー画像をアップロードできます")
    else:
        print(f"\nバナー設定まであと {5000 - new_total}pt です")
    
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n中断しました")
        sys.exit(0)
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
