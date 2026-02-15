# 立川の市の混雑状況を、リアルタイムでチェックしたり評価したりするためのプログラム
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta

# トピックス（最近の投稿一覧）。
# 一覧を作るだけじゃなく、評価（👍/👎）の数や、投稿者の平均評価も一緒に出します。
# sort パラメータで並び替え（新しい順/古い順/評価順）に対応しています。

# Blueprintの作成
topics_bp = Blueprint("topics", __name__, template_folder="templates", static_folder="static")

# 一覧ページ本体。DBから投稿を取り、テンプレに渡しやすい dict へ整形します。
# ここで time_ago（何秒前/何分前…）も作って、表示側を軽くしています。
@topics_bp.route("/topics")
def topics_page():
    """トピックスページ（最近の投稿一覧）"""
    from apps.post_page.post_db import get_all_posts, get_post_ratings, get_user_average_rating
    from apps.config import SHOP_LIST, SHOP_DETAILS
    
    # 並び替えパラメータの取得
    sort_by = request.args.get('sort', 'new')
    
    # 投稿一覧取得
    all_posts = get_all_posts()
    
    # 1時間前の時刻を計算
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    recent_posts_list = []

    for post in all_posts:
        post_id = post[0]
        user_name = post[1]
        shop_name = post[2]
        crowd_level = post[3]
        comment = post[4]
        timestamp = post[5]

        try:
            # ISO形式の日時文字列をdatetimeに変換
            dt = datetime.fromisoformat(timestamp)

            # 1時間以内の投稿のみを処理
            if dt < one_hour_ago:
                continue

            helpful, not_helpful = get_post_ratings(post_id)

            diff = datetime.now() - dt
            seconds = diff.total_seconds()

            # 投稿者ごとの平均評価を取得
            user_avg = get_user_average_rating(user_name)
            
            # ログインユーザーの評価状況を取得
            user_rating = None
            if current_user.is_authenticated:
                from apps.post_page.post_db import get_user_rating
                # 修正：引数の順序を修正（post_id, user_name）
                user_rating = get_user_rating(post_id, current_user.username)
            
            # 経過時間の表示用文字列作成
            if seconds < 60:
                time_ago = f"{int(seconds)}秒前"
            elif seconds < 3600:
                time_ago = f"{int(seconds // 60)}分前"
            elif seconds < 86400:
                time_ago = f"{int(seconds // 3600)}時間前"
            else:
                time_ago = f"{int(seconds // 86400)}日前"

            recent_posts_list.append({
                "id": post_id,
                "user_name": user_name,
                "shop_name": shop_name,
                "crowd_level": crowd_level,
                "comment": comment,
                "timestamp": dt,
                "time_ago": time_ago,
                "helpful_count": helpful,
                "not_helpful_count": not_helpful,
                "user_avg_rating": user_avg,
                "user_rated": user_rating
            })
            
        except Exception as e:
            # 日付変換エラーなどはスキップ
            print(f"投稿処理エラー: {e}")
            continue

    # Python側で並び替えを実行
    if sort_by == 'new':
        # 新しい順（timestampの降順）
        recent_posts_list.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == 'old':
        # 古い順（timestampの昇順）
        recent_posts_list.sort(key=lambda x: x['timestamp'])
    elif sort_by == 'rating':
        # 評価が高い順（helpful_countの降順）
        recent_posts_list.sort(key=lambda x: x['helpful_count'], reverse=True)
    else:
        # デフォルトは新しい順
        recent_posts_list.sort(key=lambda x: x['timestamp'], reverse=True)

    print(f"[デバッグ] 取得した投稿数: {len(recent_posts_list)}")

    # 店舗リストを作成（詳細情報付き）
    shops_with_details = []
    for shop in SHOP_LIST:
        shop_name = shop['name']
        shop_info = {
            'name': shop_name,
            'category': SHOP_DETAILS.get(shop_name, {}).get('category', '未分類'),
            'description': SHOP_DETAILS.get(shop_name, {}).get('description', ''),
            'signature': SHOP_DETAILS.get(shop_name, {}).get('signature', ''),
            'url': shop.get('url', '')
        }
        shops_with_details.append(shop_info)
    
    # テンプレートに渡す
    return render_template("topics.html", 
                         recent_posts=recent_posts_list, 
                         sort_by=sort_by,
                         shops=shops_with_details)


# 修正：評価追加エンドポイント
# 評価のPOST。1=役に立った / 0=役に立たなかった の2択。
# 👍が付いた時だけ投稿者へポイントを加算します（運用のゲーム性枠）。
@topics_bp.route('/topics/rate/<int:post_id>/<int:rating>', methods=['POST'])
@login_required
def rate_post(post_id, rating):
    """投稿に評価をつける（rating: 1=役に立った, 0=役に立たなかった）"""
    from apps.post_page.post_db import add_or_update_rating, get_post_ratings, add_evaluation_points, get_post_by_id
    
    print(f"[評価リクエスト] post_id={post_id}, rating={rating}, user={current_user.username}")
    
    if rating not in [0, 1]:
        print(f"[評価エラー] 無効なrating値: {rating}")
        return jsonify({"success": False, "error": "Invalid rating"}), 400
    
    try:
        # ratingを rating_type に変換
        if rating == 1:
            rating_type = 'helpful'
        else:
            rating_type = 'not_helpful'
        
        print(f"[評価処理] rating_type={rating_type}")
        
        # 修正：add_rating → add_or_update_rating
        add_or_update_rating(post_id, current_user.username, rating_type)
        print(f"[評価処理] 評価を保存しました")
        
        # 👍なら投稿者に評価ポイント付与
        if rating_type == 'helpful':
            post = get_post_by_id(post_id)
            if post:
                post_author = post[1]  # user_name
                # 自分の投稿には評価ポイントを付与しない
                if post_author != current_user.username:
                    add_evaluation_points(post_author, 10)
                    print(f"[評価ポイント] {post_author} に10pt付与（👍獲得）")
                else:
                    print(f"[評価ポイント] 自分の投稿のため付与なし")
        
        # 最新の評価数を取得
        helpful, not_helpful = get_post_ratings(post_id)
        print(f"[評価結果] 👍={helpful}, 👎={not_helpful}")
        
        # 最新の評価数を返す
        return jsonify({
            "success": True,
            "helpful_count": helpful,
            "not_helpful_count": not_helpful
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[評価エラー] {e}")
        print(f"[詳細エラー]\n{error_details}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500