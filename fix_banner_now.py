"""
fix_banner_now.py
現在の状況を確認して一発で修正するスクリプト

使用方法:
cd /systems
python fix_banner_now.py ユーザー名

例: python fix_banner_now.py admin
"""

import sqlite3
import os
import sys

def fix_user_banner(username):
    """指定したユーザーのバナー設定を有効にする"""
    
    print("="*60)
    print(f"{username} のバナー設定を有効化")
    print("="*60)
    
    # post_data.db を修正
    print("\npost_data.db を修正中...")
    
    if not os.path.exists("post_data.db"):
        print("post_data.db が見つかりません")
        return False
    
    conn = sqlite3.connect("post_data.db")
    c = conn.cursor()
    
    try:
        # ユーザーの存在確認
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            print(f"ユーザー '{username}' が見つかりません")
            conn.close()
            return False
        
        # カラムの存在確認と追加
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        if 'bonus_points' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
            print("bonus_points カラムを追加")
        
        if 'evaluation_points' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN evaluation_points INTEGER DEFAULT 0')
            print("evaluation_points カラムを追加")
        
        if 'total_points' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
            print("total_points カラムを追加")
        
        if 'banner_path' not in columns:
            c.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
            print("banner_path カラムを追加")
        
        conn.commit()
        
        # 現在のポイントを取得
        c.execute("""
            SELECT 
                COALESCE(bonus_points, 0) as bonus,
                COALESCE(evaluation_points, 0) as evaluation,
                COALESCE(total_points, 0) as total
            FROM users 
            WHERE username = ?
        """, (username,))
        
        result = c.fetchone()
        if not result:
            print(f"{username} のデータを取得できません")
            conn.close()
            return False
        
        bonus, evaluation, current_total = result
        correct_total = bonus + evaluation
        
        print(f"\n現在の状態:")
        print(f"  bonus_points:      {bonus}")
        print(f"  evaluation_points: {evaluation}")
        print(f"  total_points:      {current_total}")
        print(f"  正しい合計:        {correct_total}")
        
        # total_pointsが間違っている場合は修正
        if current_total != correct_total:
            c.execute("""
                UPDATE users 
                SET total_points = COALESCE(bonus_points, 0) + COALESCE(evaluation_points, 0)
                WHERE username = ?
            """, (username,))
            conn.commit()
            print(f"total_points を {current_total} → {correct_total} に修正")
        
        # ポイントが5000未満の場合は5000に設定
        if correct_total < 5000:
            print(f"\n現在 {correct_total}pt しかありません")
            print(f"   5000pt に設定しますか？ (yes/no): ", end='')
            response = input().strip().lower()
            
            if response in ['yes', 'y']:
                needed = 5000 - correct_total
                c.execute("""
                    UPDATE users 
                    SET bonus_points = COALESCE(bonus_points, 0) + ?,
                        total_points = 5000
                    WHERE username = ?
                """, (needed, username))
                conn.commit()
                print(f"{needed}pt を追加して合計5000ptにしました")
                correct_total = 5000
        
        conn.close()
        
        # memo.db を同期
        print("\nmemo.db を同期中...")
        
        if not os.path.exists("memo.db"):
            print("memo.db が見つかりません（スキップ）")
        else:
            conn_memo = sqlite3.connect("memo.db")
            c_memo = conn_memo.cursor()
            
            try:
                # ユーザーの存在確認
                c_memo.execute("SELECT username FROM users WHERE username = ?", (username,))
                if not c_memo.fetchone():
                    print(f"{username} は memo.db に存在しません（スキップ）")
                else:
                    # カラムの存在確認と追加
                    c_memo.execute("PRAGMA table_info(users)")
                    columns = [row[1] for row in c_memo.fetchall()]
                    
                    if 'bonus_points' not in columns:
                        c_memo.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
                    if 'evaluation_points' not in columns:
                        c_memo.execute('ALTER TABLE users ADD COLUMN evaluation_points INTEGER DEFAULT 0')
                    if 'total_points' not in columns:
                        c_memo.execute('ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0')
                    if 'banner_path' not in columns:
                        c_memo.execute('ALTER TABLE users ADD COLUMN banner_path VARCHAR(255)')
                    
                    conn_memo.commit()
                    
                    # ポイント情報を同期
                    c_memo.execute("""
                        UPDATE users 
                        SET bonus_points = ?,
                            evaluation_points = ?,
                            total_points = ?
                        WHERE username = ?
                    """, (bonus if correct_total < 5000 else bonus + (5000 - (bonus + evaluation)), 
                          evaluation, 
                          correct_total, 
                          username))
                    
                    conn_memo.commit()
                    print(f"memo.db を同期しました")
                
                conn_memo.close()
            except Exception as e:
                print(f"memo.db の更新エラー: {e}")
                conn_memo.close()
        
        # 結果を表示
        print("\n" + "="*60)
        print(f"完了しました！")
        print("="*60)
        print(f"ユーザー: {username}")
        print(f"合計ポイント: {correct_total}pt")
        
        if correct_total >= 5000:
            print(f"\nバナー設定が有効になりました！")
        else:
            print(f"\nまだ {5000 - correct_total}pt 不足しています")
        
        print("\n次のステップ:")
        print("1. Flaskアプリを再起動")
        print("   cd apps/main_app")
        print("   python app.py")
        print("")
        print("2. ブラウザのキャッシュをクリア（Ctrl+Shift+R）")
        print("")
        print("3. プロフィール編集ページで確認")
        print("="*60)
        
        return True
    
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False


def show_all_users():
    """全ユーザーの状態を表示"""
    
    if not os.path.exists("post_data.db"):
        return
    
    conn = sqlite3.connect("post_data.db")
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT 
                username,
                COALESCE(bonus_points, 0) as bonus,
                COALESCE(evaluation_points, 0) as evaluation,
                COALESCE(total_points, 0) as total
            FROM users
            ORDER BY total DESC
        """)
        
        users = c.fetchall()
        conn.close()
        
        if users:
            print("\n現在のユーザー一覧:")
            print("="*60)
            print(f"{'ユーザー名':<20} {'ボーナス':<10} {'評価':<10} {'合計':<10}")
            print("-"*60)
            
            for username, bonus, evaluation, total in users:
                banner_mark = ""if total >= 5000 else "  "
                print(f"{username:<20} {bonus:<10} {evaluation:<10} {total:<10} {banner_mark}")
            
            print("-"*60)
            print("バナー設定可能（5000pt以上）")
            print("="*60)
    
    except Exception as e:
        print(f"エラー: {e}")
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python fix_banner_now.py ユーザー名")
        print("\n例: python fix_banner_now.py admin")
        show_all_users()
        sys.exit(1)
    
    username = sys.argv[1]
    
    try:
        success = fix_user_banner(username)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n中断しました")
        sys.exit(0)
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)