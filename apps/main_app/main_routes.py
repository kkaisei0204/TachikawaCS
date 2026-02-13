# 必要なライブラリのインポート
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from apps.main_app.models import db
from apps.main_app.admin_guard import admin_required
import os

# Blueprintの作成
main_bp = Blueprint("main", __name__)

# トップページ（地図）
@main_bp.route('/')
def index():
    # 最新1時間の各店舗の最新投稿を取得
    from apps.post_page.post_db import get_all_posts
    from apps.prediction.prediction import get_shop_total_post_count
    from apps.config import SHOP_LOCATIONS, SHOP_DETAILS, SHOP_LIST
    from datetime import datetime, timedelta
    all_posts = get_all_posts()
    latest_by_shop = {}
    one_hour_ago = datetime.now() - timedelta(hours=1)
    now = datetime.now()
    for post in all_posts:
        post_id = post[0]
        user_name = post[1]
        shop_name = post[2]
        crowd_level = post[3]
        comment = post[4]
        timestamp = post[5]
        try:
            dt = datetime.fromisoformat(timestamp)
        except Exception:
            continue
        if dt < one_hour_ago:
            break
        shop_location = SHOP_LOCATIONS.get(shop_name)
        if not shop_location:
            continue
        if shop_name in latest_by_shop:
            continue
        total_posts = get_shop_total_post_count(shop_name, months=3)
        shop_detail = SHOP_DETAILS.get(shop_name, {})
        category = shop_detail.get('category', '該当しない')
        shop_url = ''
        for shop in SHOP_LIST:
            if shop['name'] == shop_name:
                shop_url = shop.get('url', '')
                break
        delta = now - dt
        if delta.total_seconds() < 60:
            time_ago = "たった今"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            time_ago = f"{minutes}分前"
        else:
            hours = int(delta.total_seconds() / 3600)
            time_ago = f"{hours}時間前"
        latest_by_shop[shop_name] = {
            "shop_name": shop_name,
            "user_name": user_name,
            "crowd_level": crowd_level,
            "comment": comment,
            "lat": shop_location["lat"],
            "lng": shop_location["lng"],
            "total_posts": total_posts,
            "has_ai_prediction": total_posts >= 10,
            "category": category,
            "time_ago": time_ago,
            "url": shop_url
        }
    map_markers = list(latest_by_shop.values())
    return render_template('index.html', map_markers=map_markers)


# ログイン/ログアウト/新規登録
@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """ログイン処理"""
    from apps.main_app.models import User

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash("ログインしました", "success")
            return redirect(url_for("main.index"))
        else:
            flash("ユーザー名またはパスワードが違います", "error")

    return render_template("login.html")

# ログアウト
@main_bp.route("/logout")
@login_required
def logout():
    """ログアウト処理"""
    logout_user()
    flash("ログアウトしました", "error")
    return redirect(url_for("main.index"))

# 新規登録
@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """新規登録（アイコン画像必須・bio任意）"""
    from apps.main_app.models import User
    from PIL import Image
    import uuid
    # POSTリクエスト時の処理
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        icon_file = request.files.get('icon')
        bio = request.form.get("bio", "")
        # 入力チェック
        if not username or not password:
            flash("ユーザー名とパスワードを入力してください", "error")
            return render_template('register.html')
        # アイコン画像のチェック
        if not icon_file or icon_file.filename == '':
            flash("アイコン画像を選択してください", "error")
            return render_template('register.html')
        # 既存ユーザーの確認
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("このユーザー名は既に使用されています", "error")
            return render_template('register.html')
        # 画像処理とユーザー登録
        try:
            filename = secure_filename(icon_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            # 対応形式チェック
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            if file_ext not in allowed_extensions:
                flash("JPG, PNG, GIF形式の画像を選択してください", "error")
                return render_template('register.html')
            # ユニークなファイル名生成
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            # 保存フォルダの準備
            basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            upload_folder = os.path.join(basedir, 'apps', 'top_page', 'static', 'uploads', 'icons')
            os.makedirs(upload_folder, exist_ok=True)
            # 画像処理
            filepath = os.path.join(upload_folder, unique_filename)
            # 画像オープン
            img = Image.open(icon_file)
            # 透過PNG/GIFの背景を白に変換
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 正方形クロップ
            width, height = img.size
            min_dimension = min(width, height)
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            img = img.crop((left, top, right, bottom))

            # リサイズ
            img = img.resize((200, 200), Image.LANCZOS)

            # 保存
            img.save(filepath, quality=85, optimize=True)
            # データベース登録
            icon_path = f"uploads/icons/{unique_filename}"
            # 新規ユーザー作成
            new_user = User(
                username=username,
                password=password,
                is_admin=False,
                icon_path=icon_path,
                bio=bio
            )
            db.session.add(new_user)
            db.session.commit()
            # 自動ログイン
            login_user(new_user)
            flash("登録が完了しました", "success")
            return redirect(url_for('main.index'))
        # 例外処理
        except Exception as e:
            print(f"画像処理エラー: {e}")
            flash("画像の処理中にエラーが発生しました", "error")
            return render_template('register.html')
    # GETリクエスト時は登録フォームを表示
    return render_template('register.html')

# 管理者
@main_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    """
    管理者専用：ユーザー一覧
    - q: ユーザー名の部分一致検索
    - sort: 並び替え（id_desc / id_asc / name_asc / name_desc / admin_first）
    """
    from apps.main_app.models import User
    from apps.post_page.post_db import get_all_posts
    from collections import Counter
    # 検索・並び替えパラメータ取得
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "id_desc").strip()
    # クエリ構築
    query = User.query
    if q:
        # 部分一致
        query = query.filter(User.username.contains(q))

    # 並び替え
    if sort == "id_asc":
        query = query.order_by(User.id.asc())
    elif sort == "name_asc":
        query = query.order_by(User.username.asc())
    elif sort == "name_desc":
        query = query.order_by(User.username.desc())
    elif sort == "admin_first":
        query = query.order_by(User.is_admin.desc(), User.id.asc())
    else:
        # デフォルト
        query = query.order_by(User.id.desc())
    # ユーザー取得
    users = query.all()

    # 投稿数をまとめて計算
    post_counts = Counter()
    try:
        all_posts = get_all_posts()
        for p in all_posts:
            post_counts[p[1]] += 1
    except Exception:
        pass

    # テンプレで使いやすいよう整形
    users_view = []
    for u in users:
        users_view.append({
            "id": u.id,
            "username": u.username,
            "is_admin": bool(u.is_admin),
            "posts_count": post_counts.get(u.username, 0),
        })
    # レンダリング
    return render_template(
        'admin.html',
        users=users_view,
        q=q,
        sort=sort
    )

# ユーザー詳細
@main_bp.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    """管理者専用：ユーザー詳細（投稿数/平均評価/最新投稿など）"""
    from apps.main_app.models import User
    from apps.post_page.post_db import get_all_posts, get_post_ratings, get_user_average_rating
    from datetime import datetime
    # ユーザー取得
    user = User.query.get_or_404(user_id)

    # 投稿一覧から該当ユーザー分だけ抽出（最新10件）
    latest_posts = []
    posts_count = 0
    # 全投稿走査
    try:
        all_posts = get_all_posts()
        for p in all_posts:
            if p[1] != user.username:
                continue
            posts_count += 1

            # 最新10件だけ表示用に詰める
            if len(latest_posts) < 10:
                try:
                    dt = datetime.fromisoformat(p[5])
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    time_str = p[5]
                # 評価数取得
                helpful, not_helpful = get_post_ratings(p[0])
                latest_posts.append({
                    "post_id": p[0],
                    "shop_name": p[2],
                    "crowd_level": p[3],
                    "comment": p[4],
                    "time": time_str,
                    "helpful": helpful,
                    "not_helpful": not_helpful,
                })
    except Exception:
        pass

    # 平均評価（既存関数がある前提）
    try:
        avg_rating = get_user_average_rating(user.username)
    except Exception:
        avg_rating = None
    # レンダリング
    return render_template(
        'admin_user_detail.html',
        user=user,
        posts_count=posts_count,
        avg_rating=avg_rating,
        latest_posts=latest_posts
    )

# ユーザー削除
@main_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """管理者専用：ユーザー削除（自分自身は削除不可）"""
    from apps.main_app.models import User
    # ユーザー取得
    user = User.query.get_or_404(user_id)
    # 自分自身の削除は不可
    if user.id == current_user.id:
        flash("自分自身は削除できません", "error")
        return redirect(url_for('main.admin_panel'))
    # 削除実行
    username = user.username
    db.session.delete(user)
    db.session.commit()
    # 完了メッセージ
    flash(f"ユーザー '{username}' を削除しました", "success")
    return redirect(url_for('main.admin_panel'))

# 権限切替
@main_bp.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def admin_toggle_admin(user_id):
    """
    管理者専用：権限切替（一般 ↔ 管理者）
    - 自分自身は切替不可（事故防止）
    """
    from apps.main_app.models import User
    # ユーザー取得
    user = User.query.get_or_404(user_id)
    # 自分自身の権限変更は不可
    if user.id == current_user.id:
        flash("自分自身の権限は変更できません", "error")
        return redirect(url_for('main.admin_user_detail', user_id=user.id))
    # 権限切替実行
    user.is_admin = not bool(user.is_admin)
    db.session.commit()
    # 完了メッセージ
    flash(f"'{user.username}' の権限を変更しました", "success")
    return redirect(url_for('main.admin_user_detail', user_id=user.id))

# ユーザーページ
@main_bp.route('/user/<username>')
@login_required
def user_page(username):
    """ユーザーページ（そのユーザーの投稿・評価集計・平均評価）"""
    from apps.main_app.models import User
    from apps.post_page.post_db import get_all_posts, get_post_ratings, get_user_average_rating
    # ユーザー取得
    user = User.query.filter_by(username=username).first_or_404()
    # 投稿一覧から該当ユーザー分だけ抽出
    all_posts = get_all_posts()
    user_posts = []
    # 全投稿走査
    for post_id, post_user_name, shop_name, crowd_level, comment, timestamp in all_posts:
        if post_user_name == username:
            helpful, not_helpful = get_post_ratings(post_id)
            user_posts.append({
                "id": post_id,
                "shop_name": shop_name,
                "crowd_level": crowd_level,
                "comment": comment,
                "timestamp": timestamp,
                "helpful_count": helpful,
                "not_helpful_count": not_helpful,
                "total_ratings": helpful + not_helpful
            })
    # 投稿を新しい順にソート
    user_posts.sort(key=lambda x: x['timestamp'], reverse=True)
    # 平均評価取得
    avg_rating = get_user_average_rating(username)
    # レンダリング
    return render_template(
        'user_page.html',
        user=user,
        user_posts=user_posts,
        avg_rating=avg_rating
    )

# プロフィール編集
@main_bp.route("/profile/edit", methods=["GET"])
@login_required
def profile_edit():
    """プロフィール編集ページ（表示）"""
    from apps.post_page.post_db import get_user_total_points, can_set_banner
    
    # ユーザーのポイント情報を取得
    points_info = get_user_total_points(current_user.username)
    rank_info = {
        'total_points': points_info['total_points'],
        'bonus_points': points_info['bonus_points'],
        'evaluation_points': points_info['evaluation_points'],
        'can_set_banner': can_set_banner(current_user.username)
    }
    # レンダリング
    return render_template("profile_edit.html", user=current_user, rank_info=rank_info)

# プロフィール更新
@main_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    """プロフィール編集（保存）"""
    from PIL import Image
    from apps.main_app.models import User
    import uuid
    import sqlite3
    
    # フォームデータ取得
    new_username = request.form.get("username", "").strip()
    bio = request.form.get("bio", "")
    
    # ユーザーネーム変更処理
    if new_username and new_username != current_user.username:
        # 新しいユーザーネームが既に使用されているかチェック
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            flash("このユーザー名は既に使用されています", "error")
            return redirect(url_for('main.profile_edit'))
        
        # ユーザーネーム変更（古いユーザーネームは自動的に解放される）
        old_username = current_user.username
        current_user.username = new_username
        
        # post_data.dbのusersテーブルも更新（ポイント情報）
        try:
            basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            DB_PATH = os.path.join(basedir, "post_data.db")
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, old_username))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"post_data.db更新エラー: {e}")
        
        flash(f"ユーザー名を「{new_username}」に変更しました", "success")
    
    # プロフィール情報更新
    current_user.bio = bio
    # アイコン画像処理
    if "icon" in request.files:
        file = request.files["icon"]
        if file and file.filename != "":
            try:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                # 対応形式チェック
                allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
                if file_ext not in allowed_extensions:
                    flash("JPG, PNG, GIF形式の画像を選択してください", "error")
                    return redirect(url_for('main.profile_edit'))
                # ユニークなファイル名生成
                unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                # 保存フォルダの準備
                basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                upload_folder = os.path.join(basedir, 'apps', 'top_page', 'static', 'uploads', 'icons')
                os.makedirs(upload_folder, exist_ok=True)
                # 画像処理
                filepath = os.path.join(upload_folder, unique_filename)
                # 画像オープン
                img = Image.open(file)
                # 透過PNG/GIFの背景を白に変換
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                # 正方形クロップ
                width, height = img.size
                min_dimension = min(width, height)
                left = (width - min_dimension) // 2
                top = (height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension
                img = img.crop((left, top, right, bottom))
                # リサイズ
                img = img.resize((200, 200), Image.LANCZOS)
                img.save(filepath, quality=85, optimize=True)
                # データベース更新
                current_user.icon_path = f"uploads/icons/{unique_filename}"
            # 例外処理
            except Exception as e:
                print(f"画像処理エラー: {e}")
                flash("画像の処理中にエラーが発生しました", "error")
                return redirect(url_for('main.profile_edit'))
    # 変更保存
    db.session.commit()
    flash("プロフィールを更新しました！", "success")
    return redirect(url_for("main.user_page", username=current_user.username))

# 大原亭店舗ページと予約処理
@main_bp.route("/shop/oharatei")
def oharatei():
    """大原亭の店舗ページを表示"""
    return render_template("oharatei.html")

# 大原亭予約処理
@main_bp.route("/shop/oharatei/reservation", methods=["POST"])
def oharatei_reservation():
    """大原亭の予約を処理"""
    from apps.main_app.models import Reservation
    from datetime import datetime
    # フォームデータ取得と予約登録
    try:
        customer_name = request.form.get("customer_name")
        phone = request.form.get("phone")
        reservation_date = request.form.get("reservation_date")
        reservation_time = request.form.get("reservation_time")
        people = request.form.get("people")
        comment = request.form.get("comment", "")
        # 日時オブジェクト変換
        date_obj = datetime.strptime(reservation_date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(reservation_time, "%H:%M").time()
        # 予約登録
        new_reservation = Reservation(
            user_name=customer_name,
            shop_name="大原亭",
            date=date_obj,
            time=time_obj,
            people=int(people),
            comment=comment
        )
        db.session.add(new_reservation)
        db.session.commit()
        # 完了メッセージ
        flash(
            f"ご予約を承りました！{customer_name}様、{reservation_date} {reservation_time}に{people}名様でお待ちしております。",
            "success"
        )
        return redirect(url_for("main.oharatei") + "#reserve")
    # 例外処理
    except Exception as e:
        print(f"予約エラー: {e}")
        flash("予約の処理中にエラーが発生しました。もう一度お試しください。", "error")
        return redirect(url_for("main.oharatei") + "#reserve")

# 管理者
@main_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """
    管理者向けダッシュボード
    - KPI（投稿数/予約数/評価数/AI一致率）
    - グラフ（店舗別投稿数、投稿推移、混雑割合、予約推移、予約時間帯）
    - AI精度ワースト（多数決ベースの簡易評価）
    - 異常検知（直近1時間の急増）
    - 集計期間切替（?days=7/30/90/all）
    """
    from datetime import datetime, timedelta
    from collections import Counter, defaultdict
    from apps.post_page.post_db import get_all_posts
    from apps.main_app.models import Reservation
    import sqlite3
    # 全投稿取得
    all_posts = get_all_posts()
    now = datetime.now()

    
    # 集計期間切替
    days_arg = (request.args.get("days") or "30").lower().strip()
    allowed = {"7", "30", "90", "all"}
    if days_arg not in allowed:
        days_arg = "30"
    # 期間設定
    if days_arg == "all":
        window_start = None
        window_days = "all"
    else:
        window_days = int(days_arg)
        window_start = now - timedelta(days=window_days)
    # 推移ラベルの最大は 90日（allでも長すぎないように）
    label_span = 90 if window_days == "all" else window_days

    # 固定期間
    days_90 = now - timedelta(days=90)
    hours_1 = now - timedelta(hours=1)
    days_7 = now - timedelta(days=7)
    
    # 店舗別投稿数（全期間）
    shop_counts = Counter()
    for p in all_posts:
        shop_counts[p[2]] += 1
    
    # 店舗別投稿数データ整形 
    shop_labels = list(shop_counts.keys())
    shop_data = list(shop_counts.values())

    # 投稿推移（日別：選択期間）
    posts_by_day = Counter()
    posts_window = []
    eval_posts = []
    # 全投稿走査
    for p in all_posts:
        try:
            dt = datetime.fromisoformat(p[5])
        except Exception:
            continue
        # 選択期間内かどうか
        if (window_start is None) or (dt >= window_start):
            day_key = dt.strftime("%m/%d")
            posts_by_day[day_key] += 1
            posts_window.append((p, dt))
            eval_posts.append((p[2], dt.weekday(), dt.hour, p[3]))
    # 日別投稿数データ整形
    day_labels = []
    day_values = []
    for i in range(label_span, -1, -1):
        d = (now - timedelta(days=i)).strftime("%m/%d")
        day_labels.append(d)
        day_values.append(posts_by_day.get(d, 0))


    # 混雑割合（選択期間）
    crowd_counter = Counter()
    for p, _dt in posts_window:
        crowd_counter[p[3]] += 1
    # データ整形
    crowd_labels = list(crowd_counter.keys())
    crowd_data = list(crowd_counter.values())

    
    # 予約推移（選択期間）
    if window_start is None:
        reservations_window = Reservation.query.all()
    else:
        reservations_window = Reservation.query.filter(Reservation.created_at >= window_start).all()
    # 予約日別・時間帯別集計
    res_by_day = Counter()
    res_by_hour = Counter()
    # 集計
    for r in reservations_window:
        try:
            res_by_day[r.created_at.strftime("%m/%d")] += 1
        except Exception:
            pass
        try:
            res_by_hour[r.time.hour] += 1
        except Exception:
            pass
    # データ整形
    res_day_labels = []
    res_day_values = []
    for i in range(label_span, -1, -1):
        d = (now - timedelta(days=i)).strftime("%m/%d")
        res_day_labels.append(d)
        res_day_values.append(res_by_day.get(d, 0))
    # 時間帯別（9-21時）
    hour_labels = [f"{h}時" for h in range(9, 22)]
    hour_values = [res_by_hour.get(h, 0) for h in range(9, 22)]

    # 総評価数（ratings）
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    DB_PATH = os.path.join(basedir, "post_data.db")
    total_ratings = 0
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM ratings")
        total_ratings = c.fetchone()[0]
        conn.close()
    except Exception:
        total_ratings = 0

    # AI精度
    slot_counter = defaultdict(Counter)
    for p in all_posts:
        try:
            dt = datetime.fromisoformat(p[5])
        except Exception:
            continue
        if dt >= days_90:
            key = (p[2], dt.weekday(), dt.hour)
            slot_counter[key][p[3]] += 1
    # 店舗別評価
    shop_eval_total = Counter()
    shop_eval_hit = Counter()
    # 評価ループ
    for shop, wd, hr, actual in eval_posts:
        key = (shop, wd, hr)
        if key not in slot_counter:
            continue
        predicted = slot_counter[key].most_common(1)[0][0]
        shop_eval_total[shop] += 1
        if predicted == actual:
            shop_eval_hit[shop] += 1
    # 店舗別精度計算
    shop_accuracy = []
    for shop in shop_eval_total:
        total = shop_eval_total[shop]
        hit = shop_eval_hit[shop]
        acc = round((hit / total) * 100, 1) if total else 0
        shop_accuracy.append({"shop": shop, "acc": acc, "n": total})
    # 精度ワースト10
    shop_accuracy.sort(key=lambda x: x["acc"])
    worst_accuracy = shop_accuracy[:10]
    # 全体精度
    total_eval = sum(shop_eval_total.values())
    total_hit = sum(shop_eval_hit.values())
    overall_accuracy = round((total_hit / total_eval) * 100, 1) if total_eval else None


    # 異常検知（直近1時間）
    recent_1h = Counter()
    last7h_counts = Counter()
    # 集計ループ
    for p in all_posts:
        try:
            dt = datetime.fromisoformat(p[5])
        except Exception:
            continue
        shop = p[2]
        if dt >= hours_1:
            recent_1h[shop] += 1
        if dt >= days_7:
            last7h_counts[shop] += 1
    # 異常検知判定
    anomalies = []
    for shop, cnt in recent_1h.items():
        avg_per_hour = last7h_counts.get(shop, 0) / (7 * 24)
        if cnt >= 3 and avg_per_hour > 0 and cnt >= avg_per_hour * 2:
            anomalies.append({
                "shop": shop,
                "count_1h": cnt,
                "avg_1h": round(avg_per_hour, 2)
            })

    
    # KPI
    total_posts = len(all_posts)
    posts_window_count = sum(day_values)
    reservations_window_count = len(reservations_window)

    dashboard = {
        "window": {"days": window_days, "label_span": label_span},
        "kpi": {
            "total_posts": total_posts,
            "posts_last30": posts_window_count,               
            "total_ratings": total_ratings,
            "reservations_last30": reservations_window_count, 
            "overall_ai_accuracy": overall_accuracy,
        },
        "shop_bar": {"labels": shop_labels, "data": shop_data},
        "posts_line_30": {"labels": day_labels, "data": day_values},
        "crowd_donut_30": {"labels": crowd_labels, "data": crowd_data},
        "reservations_line_30": {"labels": res_day_labels, "data": res_day_values},
        "reservations_by_hour": {"labels": hour_labels, "data": hour_values},
        "ai_worst": worst_accuracy,
        "anomalies": anomalies,
    }
    # レンダリング
    return render_template('admin_dashboard.html', dashboard=dashboard)


# 管理者
@main_bp.route('/admin/dashboard/shop/<path:shop_name>')
@login_required
@admin_required
def admin_shop_dashboard(shop_name):
    """
    店舗別ダッシュボード（本格版）
    - 期間切替（?days=7/30/90/all）
    - 投稿推移（日別）
    - 混雑レベル割合
    - 曜日別投稿数 / 時間帯別投稿数（9-21時）
    - 直近1時間の急増アラート（店舗単体）
    - 投稿者ランキング
    - 最新投稿（最大10件）
    """
    from datetime import datetime, timedelta
    from collections import Counter, defaultdict
    from apps.post_page.post_db import get_all_posts
    from apps.main_app.models import Reservation
    # 現在日時取得
    now = datetime.now()
    # 集計期間切替
    days_arg = (request.args.get("days") or "30").lower().strip()
    allowed = {"7", "30", "90", "all"}
    if days_arg not in allowed:
        days_arg = "30"
    # 期間設定
    if days_arg == "all":
        window_start = None
        window_days = "all"
    else:
        window_days = int(days_arg)
        window_start = now - timedelta(days=window_days)

    # 推移ラベルの最大は 90日（allでも長すぎないように）
    label_span = 90 if window_days == "all" else window_days

    
    # 固定期間（AI学習/異常検知）
    days_90 = now - timedelta(days=90)
    hours_1 = now - timedelta(hours=1)
    days_7 = now - timedelta(days=7)

    
    # 投稿データ取得
    all_posts = get_all_posts()
    # 店舗別投稿抽出
    shop_posts = []  # (p, dt)
    for p in all_posts:
        if p[2] != shop_name:
            continue
        try:
            dt = datetime.fromisoformat(p[5])
        except Exception:
            continue
        shop_posts.append((p, dt))

    
    # 期間内投稿（window）を作る
    posts_window = []
    for p, dt in shop_posts:
        if (window_start is None) or (dt >= window_start):
            posts_window.append((p, dt))

    
    # 投稿推移（日別）
    posts_by_day = Counter()
    for p, dt in posts_window:
        posts_by_day[dt.strftime("%m/%d")] += 1
    # 日別投稿数データ整形
    day_labels = []
    day_values = []
    for i in range(label_span, -1, -1):
        d = (now - timedelta(days=i)).strftime("%m/%d")
        day_labels.append(d)
        day_values.append(posts_by_day.get(d, 0))

    
    # 混雑割合（期間内）
    crowd_counter = Counter()
    for p, dt in posts_window:
        crowd_counter[p[3]] += 1
    crowd_labels = list(crowd_counter.keys())
    crowd_data = list(crowd_counter.values())

    # 曜日別/時間帯別 投稿数（期間内）
    weekday_counter = Counter()  
    hour_counter = Counter()     
    # 集計ループ
    for p, dt in posts_window:
        weekday_counter[dt.weekday()] += 1
        hour_counter[dt.hour] += 1
    # データ整形
    weekday_labels = ["月", "火", "水", "木", "金", "土", "日"]
    weekday_values = [weekday_counter.get(i, 0) for i in range(7)]

    hour_labels = [f"{h}時" for h in range(9, 22)]
    hour_values = [hour_counter.get(h, 0) for h in range(9, 22)]

    
    # AI精度（簡易）
    slot_counter = defaultdict(Counter)
    for p, dt in shop_posts:
        if dt >= days_90:
            slot_counter[(dt.weekday(), dt.hour)][p[3]] += 1
    # 評価ループ
    total_eval = 0
    total_hit = 0
    for p, dt in posts_window:
        key = (dt.weekday(), dt.hour)
        if key not in slot_counter:
            continue
        predicted = slot_counter[key].most_common(1)[0][0]
        actual = p[3]
        total_eval += 1
        if predicted == actual:
            total_hit += 1
    # 精度計算
    ai_acc = round((total_hit / total_eval) * 100, 1) if total_eval else None


    # 異常検知（店舗単体）
    # 直近1時間 >=3件 かつ 過去7日平均との差の2倍以上
    recent_1h = 0
    last7d_total = 0
    for p, dt in shop_posts:
        if dt >= hours_1:
            recent_1h += 1
        if dt >= days_7:
            last7d_total += 1

    avg_per_hour = last7d_total / (7 * 24) if last7d_total else 0
    anomaly = None
    if recent_1h >= 3 and avg_per_hour > 0 and recent_1h >= avg_per_hour * 2:
        anomaly = {
            "count_1h": recent_1h,
            "avg_1h": round(avg_per_hour, 2)
        }
    # 投稿者ランキング（期間内：上位5）

    user_counter = Counter()
    for p, dt in posts_window:
        user_counter[p[1]] += 1
    # データ整形
    top_users = [
        {"user": name, "count": cnt}
        for name, cnt in user_counter.most_common(5)
    ]


    # 最新投稿（最大10件）

    latest_posts = sorted(shop_posts, key=lambda x: x[1], reverse=True)[:10]
    latest_posts_view = [
        {
            "user": p[1],
            "crowd": p[3],
            "comment": p[4],
            "time": dt.strftime("%Y-%m-%d %H:%M")
        }
        for p, dt in latest_posts
    ]

    # 予約（店名で紐付けできる場合のみ）
    #   期間内の予約推移（日別）
    shop_res = []
    try:
        if hasattr(Reservation, "shop_name"):
            q = Reservation.query.filter(Reservation.shop_name == shop_name)
            if window_start is not None:
                q = q.filter(Reservation.created_at >= window_start)
            shop_res = q.all()
    except Exception:
        shop_res = []
    # 予約推移（日別・時間帯別）
    res_by_day = Counter()
    res_by_hour = Counter()
    for r in shop_res:
        try:
            res_by_day[r.created_at.strftime("%m/%d")] += 1
        except Exception:
            pass
        try:
            res_by_hour[r.time.hour] += 1
        except Exception:
            pass
    # データ整形
    res_day_labels = []
    res_day_values = []
    for i in range(label_span, -1, -1):
        d = (now - timedelta(days=i)).strftime("%m/%d")
        res_day_labels.append(d)
        res_day_values.append(res_by_day.get(d, 0))
    # 時間帯別（9-21時）
    res_hour_labels = [f"{h}時" for h in range(9, 22)]
    res_hour_values = [res_by_hour.get(h, 0) for h in range(9, 22)]

    # データまとめ
    data = {
        "shop_name": shop_name,
        "window": {
            "days": window_days,
            "label_span": label_span
        },
        "kpi": {
            "posts_total": len(shop_posts),               
            "posts_window": sum(day_values),              
            "ai_accuracy": ai_acc,
            "reservations_window": len(shop_res),         
        },
        "anomaly": anomaly,
        "top_users": top_users,
        "posts_line": {"labels": day_labels, "data": day_values},
        "crowd_donut": {"labels": crowd_labels, "data": crowd_data},
        "posts_by_weekday": {"labels": weekday_labels, "data": weekday_values},
        "posts_by_hour": {"labels": hour_labels, "data": hour_values},
        "reservations_line": {"labels": res_day_labels, "data": res_day_values},
        "reservations_by_hour": {"labels": res_hour_labels, "data": res_hour_values},
        "latest_posts": latest_posts_view
    }

    return render_template("admin_shop_dashboard.html", data=data)


# 店舗一覧・詳細ページ
@main_bp.route('/shops')
def shops_list():
    """店舗一覧ページ"""
    from apps.config import SHOP_LIST
    from apps.shop_details import SHOP_DETAILS
    
    # カテゴリーマッピング（詳細カテゴリー → 8つの主要カテゴリー）
    category_mapping = {
        # カフェ
        'カフェ': 'カフェ',
        'カフェレストラン': 'カフェ',
        'カフェダイニング': 'カフェ',
        '古民家カフェ': 'カフェ',
        
        # レストラン
        'レストラン': 'レストラン',
        'イタリアン': 'レストラン',
        'イタリアンバル': 'レストラン',
        'フレンチ': 'レストラン',
        '洋食': 'レストラン',
        '和食': 'レストラン',
        '定食': 'レストラン',
        '中華': 'レストラン',
        '韓国料理': 'レストラン',
        'アメリカン': 'レストラン',
        'アウトドアダイニング': 'レストラン',
        'ベーカリーレストラン': 'レストラン',
        '創作料理': 'レストラン',
        '海鮮': 'レストラン',
        'カレー': 'レストラン',
        'とんかつ': 'レストラン',
        
        # ラーメン屋
        'ラーメン': 'ラーメン屋',
        
        # ファーストフード
        'ファストフード': 'ファーストフード',
        'ファスフード': 'ファーストフード',
        '牛丼': 'ファーストフード',
        
        # ファミリーレストラン
        'ファミレス': 'ファミリーレストラン',
        'ファミリーレストラン': 'ファミリーレストラン',
        'イタリアンファミレス': 'ファミリーレストラン',
        '中華ファミレス': 'ファミリーレストラン',
        '和食ファミレス': 'ファミリーレストラン',
        
        # 弁当屋（該当なし）
        
        # 居酒屋
        '居酒屋': '居酒屋',
        '創作居酒屋': '居酒屋',
        'もつ鍋': '居酒屋',
        '海鮮居酒屋': '居酒屋',
        '焼き鳥': '居酒屋',
        '鉄板焼き居酒屋': '居酒屋',
    }
    
    # 店舗情報を整形
    shops = []
    for shop in SHOP_LIST:
        shop_name = shop['name']
        shop_detail = SHOP_DETAILS.get(shop_name, {})
        detail_category = shop_detail.get('category', '該当しない')
        
        # カテゴリーマッピングを適用
        main_category = category_mapping.get(detail_category, '該当しない')
        # 店舗情報を追加
        shops.append({
            'name': shop_name,
            'category': main_category,
            'description': shop_detail.get('description', ''),
            'signature': shop_detail.get('signature', ''),
            'url': shop.get('url', '')
        })
    # レンダリング
    return render_template('shops_list.html', shops=shops)
# 店舗詳細ページ
@main_bp.route('/shop/<shop_name>')
def shop_detail(shop_name):
    """店舗詳細ページ - 最新10件の投稿とAI予測を表示"""
    from apps.post_page.post_db import get_all_posts, get_post_ratings
    from apps.prediction.prediction import predict_hourly_crowd, get_best_time_to_visit
    from apps.config import SHOP_LIST
    from datetime import datetime
    # 店舗情報取得
    shop_info = None
    for shop in SHOP_LIST:
        if shop['name'] == shop_name:
            shop_info = shop
            break
    # 店舗が見つからない場合はリダイレクト
    if not shop_info:
        flash('店舗が見つかりません', 'error')
        return redirect(url_for('main.index'))
    # 最新10件の投稿取得
    all_posts = get_all_posts()
    recent_posts = []
    # 全投稿走査
    for post in all_posts:
        if post[2] == shop_name:
            post_id = post[0]
            user_name = post[1]
            crowd_level = post[3]
            comment = post[4]
            timestamp = post[5]
            # 日時変換と経過時間計算
            try:
                dt = datetime.fromisoformat(timestamp)
                # 評価数取得
                helpful, not_helpful = get_post_ratings(post_id)
                # 経過時間計算
                diff = datetime.now() - dt
                seconds = diff.total_seconds()
                # 経過時間を日本語表記に変換
                if seconds < 60:
                    time_ago = f"{int(seconds)}秒前"
                elif seconds < 3600:
                    time_ago = f"{int(seconds // 60)}分前"
                elif seconds < 86400:
                    time_ago = f"{int(seconds // 3600)}時間前"
                else:
                    time_ago = f"{int(seconds // 86400)}日前"
                # 投稿データを追加
                recent_posts.append({
                    'post_id': post_id,
                    'user_name': user_name,
                    'crowd_level': crowd_level,
                    'comment': comment,
                    'timestamp': timestamp,
                    'time_ago': time_ago,
                    'helpful_count': helpful,
                    'not_helpful_count': not_helpful
                })
                # 最新10件で終了
                if len(recent_posts) >= 10:
                    break
            except Exception:
                continue
    # AI予測データ取得
    prediction_data = predict_hourly_crowd(shop_name)
    best_time = get_best_time_to_visit(shop_name)
    # レンダリング
    return render_template(
        'ai_prediction.html',
        shop=shop_info,
        recent_posts=recent_posts,
        prediction_data=prediction_data,
        best_time=best_time
    )