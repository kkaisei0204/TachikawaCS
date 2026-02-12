from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime, timedelta
import math
from flask_login import login_required, current_user
from apps.post_page.post_db import init_db, add_post, get_post_by_id, update_post, delete_post, get_posts_by_shop, is_shop_unposted, add_bonus_points
from apps.config import SHOP_LIST, CROWD_LEVELS, LOCATION_CHECK_ENABLED, MAX_DISTANCE_METERS, SHOP_LOCATIONS

# Blueprint定義
post_bp = Blueprint('post', __name__, template_folder='templates', static_folder='static')

# アプリ起動時にDB初期化
init_db()

# 計算する関数
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    2点間の距離を計算（Haversine公式）
    Returns: 距離（メートル）
    """
    R = 6371000

    # ラジアンに変換
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine公式
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def check_location_within_range(user_lat, user_lon, shop_name):
    """
    ユーザーの位置が店舗から指定範囲内かチェック
    Returns: (範囲内かどうか, 距離)
    """
    # 位置情報チェックが無効の場合は常にTrue
    if not LOCATION_CHECK_ENABLED:
        return True, 0
    
    # 店舗の位置情報を取得
    shop_location = SHOP_LOCATIONS.get(shop_name)
    if not shop_location:
        return False, None
    
    shop_lat = shop_location['lat']
    shop_lon = shop_location['lng']
    
    # 距離を計算
    distance = calculate_distance(user_lat, user_lon, shop_lat, shop_lon)
    
    # 指定距離以内かチェック
    within_range = distance <= MAX_DISTANCE_METERS
    
    return within_range, distance

# 未投稿店舗を判定する関数
def get_unposted_shops():
    """1時間以内に投稿がない店舗のリストを取得"""
    unposted_shops = []
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    for shop in SHOP_LIST:
        shop_name = shop["name"]
        # この店舗の投稿を取得
        posts = get_posts_by_shop(shop_name)
        
        # 1時間以内の投稿があるかチェック
        has_recent_post = False
        for post in posts:
            try:
                # post[5]はtimestamp
                post_time = datetime.fromisoformat(post[5])
                if post_time >= one_hour_ago:
                    has_recent_post = True
                    break
            except:
                continue
        
        # 1時間以内に投稿がなければ未投稿リストに追加
        if not has_recent_post:
            unposted_shops.append(shop_name)
    
    return unposted_shops

# 投稿ページ
@post_bp.route('/post', methods=['GET'])
@login_required
def post_page():
    # 店舗名のリストを作成
    shop_names = [shop["name"] for shop in SHOP_LIST]
    
    # 未投稿店舗のリストを取得
    unposted_shops = get_unposted_shops()
    
    # 投稿ページを表示
    return render_template('post.html', 
                            shop_list=shop_names,
                            unposted_shops=unposted_shops,
                            crowd_levels=CROWD_LEVELS,
                            location_check_enabled=LOCATION_CHECK_ENABLED,
                            max_distance=MAX_DISTANCE_METERS)

# 投稿処理
@post_bp.route('/post', methods=['POST'])
@login_required
def submit_post():
    shop_name = request.form.get('shop_name')
    crowd_level = request.form.get('crowd_level')
    comment = request.form.get('comment', '').strip()

    # ログインユーザー名を使用
    user_name = current_user.username

    # 位置情報チェック処理（管理者は除外）
    if LOCATION_CHECK_ENABLED and not current_user.is_admin:
        # 位置情報を取得
        user_lat = request.form.get('latitude')
        user_lon = request.form.get('longitude')

        # 位置情報が取得できていない場合
        if not user_lat or not user_lon:
            return jsonify({
                "success": False,
                "error": "位置情報が取得できませんでした。位置情報の利用を許可してください。"
            }), 400
        
        # 文字列を数値に変換
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "位置情報の形式が正しくありません。"
            }), 400
        
        # 店舗への距離チェック
        within_range, distance = check_location_within_range(user_lat, user_lon, shop_name)
        
        if not within_range:
            # 店舗が見つからない場合など
            if distance is None:
                return jsonify({
                    "success": False,
                    "error": "店舗の位置情報が見つかりません。"
                }), 400
                
            # 範囲外の場合はエラー
            return jsonify({
                "success": False,
                "error": f"店舗から約{int(distance)}m離れています。{MAX_DISTANCE_METERS}m以内から投稿してください。"
            }), 403

    # 投稿保存処理
    add_post(user_name, shop_name, crowd_level, comment or "（コメントなし）")
    
    # 未投稿店舗（1時間以内に投稿がない）ならボーナスポイント付与
    if is_shop_unposted(shop_name):
        add_bonus_points(user_name, 50)
        print(f"[ボーナス] {user_name} に50pt付与（未投稿店舗）")

    print(f"[投稿完了] {user_name} さんが投稿 → {shop_name}（{crowd_level}）")

    # JSONで成功レスポンスを返す（JavaScript側でリダイレクトする）
    flash("投稿しました", "success")
    return jsonify({"success": True, "redirect": url_for('topics.topics_page')})

# 投稿編集ページ（表示）
@post_bp.route('/post/edit/<int:post_id>', methods=['GET'])
@login_required
def edit_post(post_id):
    """投稿編集ページを表示"""
    post = get_post_by_id(post_id)
    
    if not post:
        flash("投稿が見つかりません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # 投稿者本人かチェック
    post_user_name = post[1]
    # 本人でないならエラー
    if post_user_name != current_user.username:
        flash("この投稿を編集する権限がありません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # 投稿データを辞書形式に変換
    post_data = {
        "id": post[0],
        "user_name": post[1],
        "shop_name": post[2],
        "crowd_level": post[3],
        "comment": post[4],
        "timestamp": post[5]
    }
    
    shop_names = [shop["name"] for shop in SHOP_LIST]
    
    # 編集ページを表示
    return render_template('post_edit.html', 
                         post=post_data, 
                         shop_list=shop_names, 
                         crowd_levels=CROWD_LEVELS)

# 投稿編集処理（保存）
@post_bp.route('/post/edit/<int:post_id>', methods=['POST'])
@login_required
def update_post_route(post_id):
    """投稿を更新"""
    post = get_post_by_id(post_id)
    
    # 投稿が存在しない場合
    if not post:
        flash("投稿が見つかりません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # 投稿者本人かチェック
    post_user_name = post[1]
    if post_user_name != current_user.username:
        flash("この投稿を編集する権限がありません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # フォームデータを取得
    shop_name = request.form.get('shop_name')
    crowd_level = request.form.get('crowd_level')
    comment = request.form.get('comment', '').strip()
    
    # 投稿を更新
    update_post(post_id, shop_name, crowd_level, comment or "（コメントなし）")
    
    flash("投稿を更新しました", "success")
    return redirect(url_for('main.user_page', username=current_user.username))

# 投稿削除処理
@post_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post_route(post_id):
    """投稿を削除"""
    post = get_post_by_id(post_id)
    
    # 投稿が存在しない場合
    if not post:
        flash("投稿が見つかりません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # 投稿者本人かチェック
    post_user_name = post[1]
    if post_user_name != current_user.username and not current_user.is_admin:
        flash("この投稿を削除する権限がありません", "error")
        return redirect(url_for('main.user_page', username=current_user.username))
    
    # 投稿を削除
    delete_post(post_id)
    
    flash("投稿を削除しました", "success")
    return redirect(url_for('main.user_page', username=current_user.username))