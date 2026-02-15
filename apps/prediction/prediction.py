# このファイルの役割はは、過去の投稿データを分析して、未来の混雑状況を予測するAI（ロジック）モジュールです
"""
AI予測モジュール
店舗ごとの混雑状況を曜日別・時間帯別に予測（過去3ヶ月のデータ使用）
"""
# ライブラリのインポート
from datetime import datetime, timedelta
from collections import Counter
import sqlite3
import os

# データベースファイルのパス
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(basedir, "post_data.db")
# get_shop_posts_by_weekday_hour()は、特定の店舗の過去Nヶ月間の同曜日・同時間帯の投稿を取得する関数です。これにより、特定の店舗が特定の曜日と時間帯にどれだけ混雑しているかを分析するためのデータを提供します。関数は、店舗名、曜日、時間、および遡る月数を引数として受け取り、該当する投稿のリストを返します。
def get_shop_posts_by_weekday_hour(shop_name, weekday, hour, months=3):
    """
    特定店舗の過去N ヶ月間の同曜日・同時間帯の投稿を取得
    
    Args:
        shop_name: 店舗名
        weekday: 曜日（0=月曜, 6=日曜）
        hour: 時間（0-23）
        months: 何ヶ月前まで遡るか（デフォルト3ヶ月）
    
    Returns:
        該当する投稿のリスト
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # N ヶ月前の日時を計算
    n_months_ago = datetime.now() - timedelta(days=30 * months)
    n_months_ago_str = n_months_ago.isoformat()
    
    # 該当店舗の過去N ヶ月の投稿を取得
    c.execute('''
        SELECT id, user_name, shop_name, crowd_level, comment, timestamp 
        FROM posts 
        WHERE shop_name = ? AND timestamp >= ?
        ORDER BY timestamp DESC
    ''', (shop_name, n_months_ago_str))
    # 全投稿を取得
    all_posts = c.fetchall()
    conn.close()
    
    # 曜日と時間でフィルタリング
    filtered_posts = []
    for post in all_posts:
        timestamp = post[5]
        try:
            dt = datetime.fromisoformat(timestamp)
            
            # 曜日と時間が一致するかチェック
            if dt.weekday() == weekday and dt.hour == hour:
                filtered_posts.append(post)
        except:
            continue
    # フィルタリングされた投稿のリストを返す
    return filtered_posts

# get_shop_total_post_count()は、特定の店舗の過去Nヶ月間の総投稿数を取得する関数です。これにより、店舗ごとのデータ量を把握し、予測の信頼度を判断するための基準を提供します。関数は、店舗名と遡る月数を引数として受け取り、その期間内の該当店舗の投稿数をカウントして返します。
def get_shop_total_post_count(shop_name, months=3):
    """店舗の過去N ヶ月の総投稿数を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # N ヶ月前の日時を計算
    n_months_ago = datetime.now() - timedelta(days=30 * months)
    n_months_ago_str = n_months_ago.isoformat()
    
    # 過去N ヶ月分の投稿数をカウント
    c.execute('''
        SELECT COUNT(*) 
        FROM posts 
        WHERE shop_name = ? AND timestamp >= ?
    ''', (shop_name, n_months_ago_str))
    # 投稿数を取得
    count = c.fetchone()[0]
    conn.close()
    return count
# predict_hourly_crowd()は、特定の店舗の過去3ヶ月の投稿データを分析して、曜日別・時間帯別の混雑予測を生成する関数です。これにより、ユーザーが特定の店舗の混雑状況を時間帯ごとに予測できるようになります。関数は、店舗名を引数として受け取り、過去3ヶ月の投稿データから各時間帯の混雑レベルを集計し、最も多い混雑レベルを予測値とします。また、予測の信頼度も計算して返します。
def predict_hourly_crowd(shop_name):
    """
    過去3ヶ月のデータから曜日別・時間帯別の混雑予測を生成
    
    Returns:
        dict: {
            'has_enough_data': bool,
            'total_posts': int,
            'predictions': [...],
            'last_updated': '2025-01-11 15:30:00'
        }
    """
    
    # 過去3ヶ月の総投稿数を確認
    total_posts = get_shop_total_post_count(shop_name, months=3)
    
    # 10件未満なら予測不可
    if total_posts < 10:
        return {
            'has_enough_data': False,
            'total_posts': total_posts,
            'predictions': [],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': '過去3ヶ月'
        }
    
    # 現在の曜日を取得
    current_weekday = datetime.now().weekday()
    
    # 曜日名（表示用）
    weekday_names = ['月曜', '火曜', '水曜', '木曜', '金曜', '土曜', '日曜']
    
    # 時間帯ごとの予測を生成
    predictions = []
    
    for hour in range(9, 22):
        # 過去の同曜日・同時間帯のデータを取得
        posts = get_shop_posts_by_weekday_hour(shop_name, current_weekday, hour, months=3)
        data_count = len(posts)
        
        # データがない時間帯はスキップ
        if data_count == 0:
            continue
        
        # 混雑レベルを集計
        crowd_levels = [post[3] for post in posts]
        counter = Counter(crowd_levels)
        total = sum(counter.values())
        
        # 最も多い混雑レベルを予測値とする（多数決）
        predicted_level = counter.most_common(1)[0][0]
        
        # 信頼度を計算
        confidence_base = (counter[predicted_level] / total) * 100
        
        # データ量による補正（10件で60%、50件以上で100%）
        data_factor = min(data_count / 50, 1.0)
        confidence = int(confidence_base * (0.6 + 0.4 * data_factor))
        
        # 予測結果を追加
        predictions.append({
            'hour': hour,
            'time_range': f'{hour}:00-{hour+1}:00',
            'predicted_level': predicted_level,
            'confidence': confidence,
            'data_count': data_count,
            'distribution': dict(counter)
        })
    # 予測結果を返す
    return {
        'has_enough_data': True,
        'total_posts': total_posts,
        'predictions': predictions,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': '過去3ヶ月',
        'current_weekday_name': weekday_names[current_weekday]
    }
# get_current_hour_prediction()は、特定の店舗の現在時刻の混雑予測を取得する関数です。これにより、ユーザーが今まさに訪れようとしている店舗の混雑状況をリアルタイムで把握できるようになります。関数は、店舗名を引数として受け取り、predict_hourly_crowd()関数を呼び出して全時間帯の予測を取得し、その中から現在の時間帯に対応する予測を抽出して返します。もし現在の時間帯の予測が存在しない場合はNoneを返します。
def get_current_hour_prediction(shop_name):
    """現在時刻の予測を取得"""
    prediction_data = predict_hourly_crowd(shop_name)
    
    if not prediction_data['has_enough_data']:
        return None
    
    current_hour = datetime.now().hour
    
    for pred in prediction_data['predictions']:
        if pred['hour'] == current_hour:
            return pred
    
    return None
# get_best_time_to_visit()は、特定の店舗の最も空いている時間帯を推奨する関数です。これにより、ユーザーが特定の店舗を訪れる際に、混雑を避けるための最適な時間帯を知ることができます。関数は、店舗名を引数として受け取り、predict_hourly_crowd()関数を呼び出して全時間帯の予測を取得し、その中から「空いている」と予測された時間帯を抽出して信頼度の高い順にソートし、最も信頼度の高い時間帯を返します。もし「空いている」時間帯がない場合は、「やや混雑」の中から同様に最も信頼度の高い時間帯を返し、それもない場合はNoneを返します。
def get_best_time_to_visit(shop_name):
    """最も空いている時間帯を推奨"""
    prediction_data = predict_hourly_crowd(shop_name)
    # 予測に十分なデータがない場合はNoneを返す
    if not prediction_data['has_enough_data']:
        return None
    
    # 「空いている」時間帯を抽出
    empty_times = [
        pred for pred in prediction_data['predictions']
        if pred['predicted_level'] == '空いている'
    ]
    
    if empty_times:
        # 信頼度が高い順にソート
        empty_times.sort(key=lambda x: x['confidence'], reverse=True)
        return empty_times[0]
    
    # 「空いている」がない場合は「やや混雑」を探す
    moderate_times = [
        pred for pred in prediction_data['predictions']
        if pred['predicted_level'] == 'やや混雑'
    ]
    # 信頼度が高い順にソートして返す
    if moderate_times:
        moderate_times.sort(key=lambda x: x['confidence'], reverse=True)
        return moderate_times[0]
    # 「空いている」も「やや混雑」もない場合はNoneを返す
    return None