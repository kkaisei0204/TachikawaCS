# 「投稿データに関するデータベース操作と、それに付随する計算ロジックを一手に引き受ける管理係」です。
import sqlite3
import os
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリを取得
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(basedir, "post_data.db")
# init_db()はアプリ起動時に呼び出され、データベースとテーブルを初期化します。これにより、アプリケーションが必要とするデータ構造が確実に存在するようになります。
def init_db():
    """データベースとテーブルを初期化"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
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
    
    # ratingsテーブル作成（評価機能）
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            rating_type TEXT NOT NULL,
            UNIQUE(post_id, user_name)
        )
    ''')
    # reservationsテーブル作成（予約機能）
    conn.commit()
    conn.close()
    print("[DB初期化完了] post_data.db")

# get_all_posts()は、投稿テーブルから全ての投稿を新しい順に取得する関数です。これにより、ユーザーが最新の投稿を簡単に閲覧できるようになります。
def get_all_posts():
    """全投稿を取得（新しい順）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    #postsテーブルから全投稿を取得
    c.execute('SELECT * FROM posts ORDER BY id DESC')
    # # 実行結果をすべて取得
    posts = c.fetchall()
    conn.close()
    return posts

# add_post()は、新しい投稿をデータベースに追加する関数です。ユーザー名、店舗名、混雑度、コメントを引数として受け取り、現在のタイムスタンプとともに投稿を保存します。これにより、ユーザーが簡単に新しい投稿を作成できるようになります。
def add_post(user_name, shop_name, crowd_level, comment):
    """新規投稿を追加"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    # postsテーブルに新しい投稿を追加するSQL
    c.execute('''
        INSERT INTO posts (user_name, shop_name, crowd_level, comment, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_name, shop_name, crowd_level, comment, timestamp))
    # 変更を保存して接続を閉じる
    conn.commit()
    conn.close()
    print(f"[投稿保存] {user_name} → {shop_name}（{crowd_level}）")

# get_post_by_id()は、投稿IDを引数として受け取り、そのIDに対応する投稿をデータベースから取得する関数です。これにより、特定の投稿の詳細を表示したり、編集したりする際に必要な情報を簡単に取得できるようになります。
def get_post_by_id(post_id):
    """投稿IDから投稿を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    return post

# update_post()は、既存の投稿を更新するための関数です。投稿ID、店舗名、混雑度、コメントを引数として受け取り、指定された投稿の情報をデータベース内で更新します。これにより、ユーザーが誤って投稿した内容を修正したり、最新の情報に更新したりすることができます。
def update_post(post_id, shop_name, crowd_level, comment):
    """投稿を更新"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 店舗名・混雑度・コメントを更新するSQL
    c.execute('''
        UPDATE posts 
        SET shop_name= ?, crowd_level = ?, comment = ?
        WHERE id = ?
    ''', (shop_name, crowd_level, comment, post_id))
    conn.commit()
    conn.close()

# delete_post()は、投稿IDを引数として受け取り、そのIDに対応する投稿をデータベースから削除する関数です。これにより、ユーザーが不要な投稿を削除したり、誤った投稿を取り消したりすることができます。
def delete_post(post_id):
    """投稿を削除"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

# get_user_last_post_time()は、ユーザー名を引数として受け取り、そのユーザーの最後の投稿時刻をデータベースから取得する関数です。これにより、ユーザーが最後に投稿した時間を確認したり、一定時間内の投稿制限を実装したりすることができます。
def get_user_last_post_time(user_name):
    """ユーザーの最後の投稿時刻を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 最新の投稿時刻を取得
    c.execute('SELECT timestamp FROM posts WHERE user_name = ? ORDER BY timestamp DESC LIMIT 1', (user_name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# get_posts_by_shop()は、店舗名を引数として受け取り、その店舗に関連する全ての投稿をデータベースから取得する関数です。これにより、ユーザーが特定の店舗の混雑状況やコメントを簡単に閲覧できるようになります。
def get_posts_by_shop(shop_name):
    """特定の店舗の投稿をすべて取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 店舗名で絞って投稿を取得
    c.execute('SELECT * FROM posts WHERE shop_name= ? ORDER BY timestamp DESC', (shop_name,))
    posts = c.fetchall()
    conn.close()
    return posts

# get_latest_post_by_shop()は、店舗名を引数として受け取り、その店舗に関連する最新の投稿をデータベースから取得する関数です。これにより、ユーザーが特定の店舗の最新の混雑状況やコメントを簡単に確認できるようになります。
def get_latest_post_by_shop(shop_name):
    """店舗ごとの最新投稿を1件取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM posts 
        WHERE shop_name= ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (shop_name,))
    result = c.fetchone()
    conn.close()
    return result

# 評価関連の関数
# get_post_ratings()は、投稿IDを引数として受け取り、その投稿に対する「役立った」と「役立たない」の評価数をデータベースから取得する関数です。これにより、ユーザーが投稿の評価状況を確認できるようになります。
def get_post_ratings(post_id):
    """投稿の評価数を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 「役立った」の数
    c.execute('SELECT COUNT(*) FROM ratings WHERE post_id = ? AND rating_type = ?', 
              (post_id, 'helpful'))
    helpful = c.fetchone()[0]
    
    # 「役立たない」の数
    c.execute('SELECT COUNT(*) FROM ratings WHERE post_id = ? AND rating_type = ?', 
              (post_id, 'not_helpful'))
    not_helpful = c.fetchone()[0]
    
    conn.close()
    return helpful, not_helpful

# get_user_rating()は、投稿IDとユーザー名を引数として受け取り、そのユーザーがその投稿に対してどのような評価を付けたかをデータベースから取得する関数です。これにより、ユーザーが自分の評価状況を確認したり、評価を変更したりすることができます。
def get_user_rating(post_id, user_name):
    """特定のユーザーがその投稿に評価を付けたかどうかをチェック
    Returns: 1 (helpful), 0 (not_helpful), None (未評価)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # ユーザーがどの種類の評価をしたかを取得
    c.execute('SELECT rating_type FROM ratings WHERE post_id = ? AND user_name = ?', (post_id, user_name))
    result = c.fetchone()
    conn.close()
    
    if result:
        # 'helpful' なら 1, 'not_helpful' なら 0
        return 1 if result[0] == 'helpful' else 0
    return None

# add_or_update_rating()は、投稿ID、ユーザー名、評価の種類（「役立った」または「役立たない」）を引数として受け取り、その評価をデータベースに追加または更新する関数です。これにより、ユーザーが投稿に対して評価を付けたり、既存の評価を変更したりすることができます。
def add_or_update_rating(post_id, user_name, rating_type):
    """投稿に評価を追加または更新（rating_type: 'helpful' or 'not_helpful'）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 既存の評価があれば更新、なければ挿入
        c.execute('''
            INSERT INTO ratings (post_id, user_name, rating_type)
            VALUES (?, ?, ?)
            ON CONFLICT(post_id, user_name) 
            DO UPDATE SET rating_type = excluded.rating_type
        ''', (post_id, user_name, rating_type))
        # 評価ポイントの付与（役立ったなら +10、役立たないなら -5）
        conn.commit()
    except Exception as e:
        print(f"評価追加エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

# get_user_average_rating()は、ユーザー名を引数として受け取り、そのユーザーの全投稿に対する評価の平均をデータベースから取得する関数です。これにより、ユーザーが自分の投稿の評価状況を全体的に把握できるようになります。
def get_user_average_rating(username):
    """ユーザーの平均評価を取得（0-100のパーセンテージ）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # ユーザーの全投稿IDを取得
    c.execute('SELECT id FROM posts WHERE user_name = ?', (username,))
    post_ids = [row[0] for row in c.fetchall()]
    # 投稿がない場合は None を返す
    if not post_ids:
        conn.close()
        return None
    
    # 全ての評価を取得
    placeholders = ','.join('?' * len(post_ids))
    c.execute(f'SELECT rating_type FROM ratings WHERE post_id IN ({placeholders})', post_ids)
    ratings = c.fetchall()
    conn.close()
    # 評価がない場合は None を返す
    if not ratings:
        return None
    
    # helpful = 1, not_helpful = 0として計算
    helpful_count = sum(1 for r in ratings if r[0] == 'helpful')
    total_count = len(ratings)
    
    # パーセンテージで返す（役立った評価の割合）
    return int((helpful_count / total_count) * 100)

# get_user_reservations()は、ユーザー名を引数として受け取り、そのユーザーの全ての予約をデータベースから取得する関数です。これにより、ユーザーが自分の予約状況を確認したり、予約を管理したりすることができます。
def get_user_reservations(user_name):
    """特定ユーザーの予約一覧を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, user_name, shop_name, date, time, people, comment
        FROM reservations
        WHERE user_name = ?
        ORDER BY date DESC, time DESC
    ''', (user_name,))
    reservations = c.fetchall()
    conn.close()
    return reservations

# delete_reservation()は、予約IDを引数として受け取り、そのIDに対応する予約をデータベースから削除する関数です。これにより、ユーザーが不要な予約を削除したり、誤った予約を取り消したりすることができます。
def delete_reservation(reservation_id):
    """予約を削除"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
    conn.commit()
    conn.close()


# ランクシステム関数（ポイント制）
# get_user_total_points()は、ユーザー名を引数として受け取り、そのユーザーの総ポイントをデータベースから取得する関数です。これにより、ユーザーが自分のポイント状況を確認できるようになります。
def get_user_helpful_count(username):
    """ユーザーが獲得したの総数を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # ユーザーの全投稿IDを取得
    c.execute('SELECT id FROM posts WHERE user_name = ?', (username,))
    post_ids = [row[0] for row in c.fetchall()]
    
    if not post_ids:
        conn.close()
        return 0
    
    # 全投稿の「役立った」評価の数をカウント
    placeholders = ','.join('?' * len(post_ids))
    c.execute(f'''
        SELECT COUNT(*) FROM ratings 
        WHERE post_id IN ({placeholders}) 
        AND rating_type = 'helpful'
    ''', post_ids)
    
    count = c.fetchone()[0]
    conn.close()
    return count

# get_user_rank_info()は、ユーザー名を引数として受け取り、そのユーザーのランク情報を計算して返す関数です。ポイント制に基づいて、ユーザーのランク、次のランクまでの進捗、総ポイントなどの情報を提供します。これにより、ユーザーが自分のランク状況を把握し、次のランクを目指すモチベーションを高めることができます。
def get_user_rank_info(username):
    """ユーザーのランク情報を取得（ポイント制・本番環境）"""
    # 合計ポイントを取得
    points_info = get_user_total_points(username)
    total_points = points_info['total_points']
    
    # ランク判定（ポイント制）
    # ポイント制のランク設定例
    if total_points >= 10000:
        rank = "信頼できる投稿者"
        rank_level = 3
        next_rank = None
        progress = 100
    elif total_points >= 5000:
        rank = "プロレポーター"

        rank_level = 2
        next_rank = "信頼できる投稿者"
        progress = int((total_points / 10000) * 100)
    elif total_points >= 10:
        rank = "ビギナー"

        rank_level = 1
        next_rank = "プロレポーター"
        progress = int((total_points / 5000) * 100)
    else:
        rank = "未ランク"

        rank_level = 0
        next_rank = "ビギナー"
        progress = int((total_points / 10) * 100)
    
    return {
        "rank": rank,
        #"icon": icon,
        "rank_level": rank_level,
        "total_points": total_points,
        "next_rank": next_rank,
        "progress": progress
    }
# can_set_banner()は、ユーザー名を引数として受け取り、そのユーザーがバナー設定の条件を満たしているかどうかをデータベースからチェックする関数です。これにより、ユーザーが特定のランクやポイント条件を満たしている場合にのみ、プロフィールバナーの設定が可能になるように制御できます。
def can_set_banner(username):
    """バナー設定が可能かチェック"""
    points_info = get_user_total_points(username)
    return points_info['total_points'] >= 5000

# has_trusted_badge()は、ユーザー名を引数として受け取り、そのユーザーが信頼バッジの条件を満たしているかどうかをデータベースからチェックする関数です。これにより、ユーザーが特定のランクやポイント条件を満たしている場合にのみ、プロフィールに信頼バッジが表示されるように制御できます。
def has_trusted_badge(username):
    """信頼バッジを持っているかチェック"""
    points_info = get_user_total_points(username)
    return points_info['total_points'] >= 10000

# 未投稿店舗チェック＆報酬システム（1時間以内判定）
# is_shop_unposted()は、店舗名を引数として受け取り、その店舗が1時間以内に投稿がないかどうかをデータベースからチェックする関数です。これにより、ユーザーが特定の店舗に対して新しい投稿を行う際に、その店舗が未投稿状態であるかどうかを判断し、報酬システムなどの条件分岐に利用することができます。
def is_shop_unposted(shop_name):
    """その店舗が1時間以内に投稿がないかチェック（マップから消えた = 未投稿扱い）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1時間前の時刻
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    # 1時間以内の投稿があるかチェック
    c.execute('''
        SELECT COUNT(*) FROM posts 
        WHERE shop_name= ? 
        AND datetime(timestamp) >= datetime(?)
    ''', (shop_name, one_hour_ago.isoformat()))
    
    count = c.fetchone()[0]
    conn.close()
    
    # 1時間以内に投稿がない = 未投稿扱い（True）
    return count == 0

# get_user_bonus_points()は、ユーザー名を引数として受け取り、そのユーザーのボーナスポイントをデータベースから取得する関数です。これにより、ユーザーが自分のボーナスポイント状況を確認できるようになります。
def get_user_bonus_points(username):
    """ユーザーのボーナスポイント取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # bonus_pointsからポイントを取得
        c.execute('SELECT bonus_points FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        conn.close()
        return 0

# add_bonus_points()は、ユーザー名とポイント数を引数として受け取り、そのユーザーのボーナスポイントをデータベースに加算する関数です。これにより、ユーザーが特定のアクションを行った際に、報酬としてボーナスポイントを付与することができます。また、ユーザーが存在しない場合は新規作成するロジックも含まれています。
def add_bonus_points(username, points):
    """ボーナスポイント付与"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # bonus_pointsにポイントを加算
        c.execute('''
            UPDATE users 
            SET bonus_points = COALESCE(bonus_points, 0) + ?
            WHERE username = ?
        ''', (points, username))
        
        if c.rowcount == 0:
            try:
                # ユーザーが存在しない場合は新規作成
                c.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
                # ユーザーテーブルのボーナスポイントを更新
                c.execute('''
                    UPDATE users 
                    SET bonus_points = COALESCE(bonus_points, 0) + ?
                    WHERE username = ?
                ''', (points, username))
            except:
                pass
        
        conn.commit()
        print(f"[ボーナスポイント] {username} に {points}pt 付与")
    except Exception as e:
        print(f"[ボーナスポイント付与エラー] {e}")
        conn.rollback()
    finally:
        conn.close()

# 評価ポイントシステム
# add_evaluation_points_column_if_not_exists()は、usersテーブルに評価ポイントカラムを追加する関数です。既にカラムが存在する場合は何もしません。これにより、ユーザーテーブルに評価ポイントを保存するためのカラムが確実に存在するようになります。
def add_evaluation_points_column_if_not_exists():
    """evaluation_pointsカラムを追加（存在しない場合のみ）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        #ユーザーテーブルに評価ポイントカラムを追加
        c.execute('ALTER TABLE users ADD COLUMN evaluation_points INTEGER DEFAULT 0')
        conn.commit()
        print("[DB更新] evaluation_pointsカラムを追加しました")
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

# get_user_evaluation_points()は、ユーザー名を引数として受け取り、そのユーザーの評価ポイントをデータベースから取得する関数です。これにより、ユーザーが自分の評価ポイント状況を確認できるようになります。
def get_user_evaluation_points(username):
    """ユーザーの評価ポイント取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 指定されたユーザーが評価ポイントを取得する
        c.execute('SELECT evaluation_points FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0
    except:
        conn.close()
        return 0

# add_evaluation_points()は、ユーザー名とポイント数を引数として受け取り、そのユーザーの評価ポイントをデータベースに加算する関数です。これにより、ユーザーが特定のアクションを行った際に、報酬として評価ポイントを付与することができます。また、ユーザーが存在しない場合は新規作成するロジックも含まれています。
def add_evaluation_points(username, points):
    """評価ポイント付与"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 指定されたユーザーの評価ポイントを加算する
        c.execute('''
            UPDATE users 
            SET evaluation_points = COALESCE(evaluation_points, 0) + ?
            WHERE username = ?
        ''', (points, username))
        
        conn.commit()
        print(f"[評価ポイント] {username} に {points}pt 付与")
    except Exception as e:
        print(f"[評価ポイント付与エラー] {e}")
        conn.rollback()
    finally:
        conn.close()

# get_user_total_points()は、ユーザー名を引数として受け取り、そのユーザーの総ポイント（ボーナスポイントと評価ポイントの合計）をデータベースから取得する関数です。これにより、ユーザーが自分の総ポイント状況を確認できるようになります。
def get_user_total_points(username):
    """ユーザーの合計ポイント取得（bonus + evaluation）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 評価とボーナスの合計ポイントを取得する
        c.execute('''
            SELECT 
                COALESCE(bonus_points, 0) as bonus,
                COALESCE(evaluation_points, 0) as evaluation
            FROM users 
            WHERE username = ?
        ''', (username,))
        result = c.fetchone()
        conn.close()
        
        if result:
            bonus = result[0]
            evaluation = result[1]
            
            return {
                'bonus_points': bonus,
                'evaluation_points': evaluation,
                'total_points': bonus + evaluation
            }
        # 結果が存在しない場合はすべて0で返す
        return {'bonus_points': 0, 'evaluation_points': 0, 'total_points': 0}
    except:
        conn.close()
        # エラー時はすべて0で返す
        return {'bonus_points': 0, 'evaluation_points': 0, 'total_points': 0}

# add_bonus_points_column()は、usersテーブルにbonus_pointsカラムを追加する関数です。既にカラムが存在する場合はエラーをキャッチして無視します。これにより、ユーザーテーブルにボーナスポイントを保存するためのカラムが確実に存在するようになります。
# usersテーブルにカラムを追加
def add_bonus_points_column():
    """usersテーブルにbonus_pointsカラムを追加"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # ユーザーテーブルにボーナスポイントカラムを追加
        c.execute('ALTER TABLE users ADD COLUMN bonus_points INTEGER DEFAULT 0')
        conn.commit()
        print("[DB更新] bonus_pointsカラムを追加しました")
    except sqlite3.OperationalError:
        print("[DB更新] bonus_pointsカラムは既に存在します")
    finally:
        conn.close()


# 初回実行時に自動でカラム追加を試みる
try:
    add_bonus_points_column()
    add_evaluation_points_column_if_not_exists()
except:
    pass
# get_ai_prediction()は、店舗名と現在の曜日を引数として受け取り、その店舗の直近1週間の投稿データを分析して、AI予測データを生成する関数です。これにより、ユーザーが特定の店舗の混雑状況を予測しやすくなります。予測は、各時間帯の「空いている」割合に基づいて行われ、60%以上の確率で空いている時間帯がある場合はその時間帯を返し、そうでない場合は「大変込み合っています」と返します。
def get_ai_prediction(shop_name, current_weekday):
    """
    AI予測データを取得
    「何曜日の何時～何時は空いている可能性が高いです」を1つだけ表示
    空いている時間がない場合は「大変込み合っています」
    """
    import sqlite3
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 直近1週間のデータを取得
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    
    cur.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            crowd_level,
            COUNT(*) as count
        FROM posts
        WHERE shop_name = ? 
        AND CAST(strftime('%w', timestamp) AS INTEGER) = ?
        AND timestamp >= ?
        GROUP BY hour, crowd_level
        ORDER BY hour
    """, (shop_name, current_weekday, one_week_ago))
    
    data = cur.fetchall()
    conn.close()
    
    total_posts = sum(row[2] for row in data)
    weekday_name = get_weekday_name(current_weekday)
    
    if not data or total_posts < 10:
        return {
            'has_enough_data': False,
            'total_posts': total_posts,
            'current_weekday_name': weekday_name
        }
    
    # 時間帯ごとのデータを整理
    hour_data = {}
    for hour, level, count in data:
        if hour not in hour_data:
            hour_data[hour] = {}
        hour_data[hour][level] = count
    
    # 空いている時間を探す（信頼度が高い順）
    best_time = None
    best_confidence = 0
    
    for hour in sorted(hour_data.keys()):
        levels = hour_data[hour]
        total = sum(levels.values())
        
        # 「空いている」の割合を計算
        empty_count = levels.get('空いている', 0)
        confidence = int((empty_count / total) * 100)
        
        # 60%以上の確率で空いている時間を採用
        if confidence >= 60 and confidence > best_confidence:
            best_time = {
                'time_range': f"{hour}:00-{int(hour)+1}:00",
                'data_count': total,
                'confidence': confidence
            }
            best_confidence = confidence
    # 最も信頼度の高い時間帯が見つからない場合は「大変込み合っています」とする
    return {
        'has_enough_data': True,
        'best_time': best_time,
        'is_crowded': best_time is None,
        'total_posts': total_posts,
        'current_weekday_name': weekday_name,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
# get_weekday_name()は、曜日番号を引数として受け取り、その番号に対応する日本語の曜日名を返す関数です。これにより、ユーザーが曜日番号を見たときに、直感的に理解できるようになります。
def get_weekday_name(weekday):
    """曜日番号を日本語名に変換"""
    weekdays = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    return weekdays[weekday] if 0 <= weekday < 7 else '不明'