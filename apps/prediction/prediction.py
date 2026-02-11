"""
AI予測モジュール
店舗ごとの混雑状況を曜日別・時間帯別に予測（過去3ヶ月のデータ使用）
"""

from datetime import datetime, timedelta
from collections import Counter
import sqlite3
import os

# データベースファイルのパス
basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(basedir, "post_data.db")

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
    
    return filtered_posts

def get_shop_total_post_count(shop_name, months=3):
    """店舗の過去N ヶ月の総投稿数を取得"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    n_months_ago = datetime.now() - timedelta(days=30 * months)
    n_months_ago_str = n_months_ago.isoformat()
    
    # 過去N ヶ月分の投稿数をカウント
    c.execute('''
        SELECT COUNT(*) 
        FROM posts 
        WHERE shop_name = ? AND timestamp >= ?
    ''', (shop_name, n_months_ago_str))
    
    count = c.fetchone()[0]
    conn.close()
    return count

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
    
    return {
        'has_enough_data': True,
        'total_posts': total_posts,
        'predictions': predictions,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': '過去3ヶ月',
        'current_weekday_name': weekday_names[current_weekday]
    }

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

def get_best_time_to_visit(shop_name):
    """最も空いている時間帯を推奨"""
    prediction_data = predict_hourly_crowd(shop_name)
    
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
    
    if moderate_times:
        moderate_times.sort(key=lambda x: x['confidence'], reverse=True)
        return moderate_times[0]
    
    return None