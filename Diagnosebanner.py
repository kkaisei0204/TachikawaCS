"""
diagnose_banner.py
バナー設定ができない問題を診断して修正するスクリプト

使用方法:
1. /systems/ に配置
2. python diagnose_banner.py
"""

import sqlite3
import os
import sys

def check_database(db_path, db_name):
    """データベースの状態をチェック"""
    
    print(f"\n{'='*60}")
    print(f"{db_name} をチェック中...")
    print('='*60)
    
    if not os.path.exists(db_path):
        print(f"{db_path} が見つかりません")
        return None
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # usersテーブルの存在確認
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print(f"usersテーブルが見つかりません")
            conn.close()
            return None
        
        # カラムの確認
        c.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in c.fetchall()}
        
        print(f"\nカラム一覧:")
        for col, typ in columns.items():
            print(f"  ✓ {col:25s} ({typ})")
        
        # ユーザーのポイント情報を取得
        print(f"\nユーザー情報:")
        
        query_parts = []
        if 'bonus_points' in columns:
            query_parts.append('COALESCE(bonus_points, 0) as bonus')
        else:
            query_parts.append('0 as bonus')
        
        if 'evaluation_points' in columns:
            query_parts.append('COALESCE(evaluation_points, 0) as evaluation')
        else:
            query_parts.append('0 as evaluation')
        
        if 'total_points' in columns:
            query_parts.append('COALESCE(total_points, 0) as total')
        else:
            query_parts.append('(COALESCE(bonus_points, 0) + COALESCE(evaluation_points, 0)) as total')
        
        query = f"SELECT username, {', '.join(query_parts)} FROM users ORDER BY total DESC"
        c.execute(query)
        users = c.fetchall()
        
        print(f"{'ユーザー名':<20} {'ボーナス':<10} {'評価':<10} {'合計':<10}")
        print('-'*60)
        for username, bonus, evaluation, total in users:
            banner_mark = "" if total >= 5000 else "  "
            print(f"{username:<20} {bonus:<10} {evaluation:<10} {total:<10} {banner_mark}")
        
        conn.close()
        return users
    
    except Exception as e:
        print(f" エラー: {e}")
        conn.close()
        return None


def fix_databases():
    """両方のデータベースを修正"""
    
    print("\n" + "="*60)
    print("🔧 データベース修正スクリプト")
    print("="*60)
    
    # post_data.db をチェック
    post_users = check_database("post_data.db", "post_data.db")
    
    # memo.db をチェック
    memo_users = check_database("memo.db", "memo.db")
    
    if not post_users:
        print("\n post_data.db からユーザー情報を取得できません")
        return False
    
    # post_data.db のtotal_pointsを修正
    print("\n" + "="*60)
    print("post_data.db のtotal_pointsを修正中...")
    print("="*60)
    
    conn = sqlite3.connect("post_data.db")
    c = conn.cursor()
    
    try:
        # カラムの存在確認
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        # total_pointsカラムがなければ追加
        if 'total_points' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
            print("total_pointsカラムを追加しました")
        
        # banner_pathカラムがなければ追加
        if 'banner_path' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
            print("banner_pathカラムを追加しました")
        
        conn.commit()
        
        # 全ユーザーのtotal_pointsを再計算
        c.execute("SELECT username FROM users")
        usernames = [row[0] for row in c.fetchall()]
        
        for username in usernames:
            c.execute("""
                UPDATE users 
                SET total_points = COALESCE(bonus_points, 0) + COALESCE(evaluation_points, 0)
                WHERE username = ?
            """, (username,))
        
        conn.commit()
        print(f"{len(usernames)}人のtotal_pointsを更新しました")
        
        conn.close()
    except Exception as e:
        print(f"エラー: {e}")
        conn.close()
        return False
    
    # memo.db を同期
    if os.path.exists("memo.db"):
        print("\n" + "="*60)
        print("memo.db を同期中...")
        print("="*60)
        
        conn_memo = sqlite3.connect("memo.db")
        c_memo = conn_memo.cursor()
        
        try:
            # カラムの存在確認
            c_memo.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in c_memo.fetchall()]
            
            # 必要なカラムを追加
            if 'bonus_points' not in columns:
                c_memo.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
                print("bonus_pointsカラムを追加")
            
            if 'evaluation_points' not in columns:
                c_memo.execute('ALTER TABLE users ADD COLUMN evaluation_points INTEGER DEFAULT 0')
                print("evaluation_pointsカラムを追加")
            
            if 'total_points' not in columns:
                c_memo.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
                print("total_pointsカラムを追加")
            
            if 'banner_path' not in columns:
                c_memo.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
                print("banner_pathカラムを追加")
            
            conn_memo.commit()
            
            # post_data.db からポイント情報をコピー
            conn_post = sqlite3.connect("post_data.db")
            c_post = conn_post.cursor()
            
            c_post.execute("""
                SELECT 
                    username,
                    COALESCE(bonus_points, 0) as bonus,
                    COALESCE(evaluation_points, 0) as evaluation,
                    COALESCE(total_points, 0) as total
                FROM users
            """)
            
            post_data = c_post.fetchall()
            conn_post.close()
            
            for username, bonus, evaluation, total in post_data:
                # memo.db のユーザーが存在するか確認
                c_memo.execute("SELECT username FROM users WHERE username = ?", (username,))
                if c_memo.fetchone():
                    c_memo.execute("""
                        UPDATE users 
                        SET bonus_points = ?,
                            evaluation_points = ?,
                            total_points = ?
                        WHERE username = ?
                    """, (bonus, evaluation, total, username))
            
            conn_memo.commit()
            print(f"{len(post_data)}人のポイント情報を同期しました")
            
            conn_memo.close()
        except Exception as e:
            print(f"エラー: {e}")
            conn_memo.close()
    
    # 修正後の状態を表示
    print("\n" + "="*60)
    print("修正後の状態:")
    print("="*60)
    
    check_database("post_data.db", "post_data.db")
    if os.path.exists("memo.db"):
        check_database("memo.db", "memo.db")
    
    return True


def check_flask_code():
    """Flaskのコードをチェック"""
    
    print("\n" + "="*60)
    print("Flaskコードをチェック中...")
    print("="*60)
    
    main_routes_path = "apps/main_app/main_routes.py"
    
    if not os.path.exists(main_routes_path):
        print(f"{main_routes_path} が見つかりません")
        return False
    
    with open(main_routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # profile_edit関数にrank_infoがあるかチェック
    if 'rank_info' in content and 'get_user_total_points' in content:
        print("profile_edit関数にrank_info処理が含まれています")
        return True
    else:
        print("profile_edit関数にrank_info処理がありません")
        print("main_routes.pyを更新する必要があります")
        return False


def main():
    """メイン処理"""
    
    print("="*60)
    print("🩺 バナー設定問題診断ツール")
    print("="*60)
    print("5000ポイントあるのにバナー設定ができない問題を診断します")
    print("="*60)
    
    # データベースを修正
    db_ok = fix_databases()
    
    # Flaskコードをチェック
    code_ok = check_flask_code()
    
    # 結果まとめ
    print("\n" + "="*60)
    print("診断結果:")
    print("="*60)
    
    if db_ok:
        print("データベース: OK")
    else:
        print("データベース: 修正が必要")
    
    if code_ok:
        print("Flaskコード: OK")
    else:
        print("Flaskコード: main_routes.pyの更新が必要")
    
    # 次のステップを表示
    print("\n" + "="*60)
    print("次のステップ:")
    print("="*60)
    
    if not code_ok:
        print("1. main_routes.py を更新してください")
        print("   cp main_routes.py apps/main_app/main_routes.py")
        print("")
    
    print("2. Flaskアプリを再起動してください")
    print("   cd apps/main_app")
    print("   # Ctrl+Cで停止")
    print("   python app.py")
    print("")
    print("3. ブラウザのキャッシュをクリア（Ctrl+Shift+R）")
    print("")
    print("4. プロフィール編集ページにアクセス")
    print("   → バナー設定が表示されるはずです")
    print("="*60)


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