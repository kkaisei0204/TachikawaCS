from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from apps.main_app.models import db
from apps.main_app.models import Reservation
from apps.config import SHOP_LIST  # 店舗リストを読み込む
from flask import Blueprint

# 予約機能（デモ枠）。混雑投稿とは別に、予約→完了→履歴の流れだけ用意しています。
# 発表で触れるなら「予約もできる（デモ）」くらいの扱いで十分です。

reservation_bp = Blueprint(
    "reservation",
    __name__,
    template_folder="templates",
    static_folder="static"
 )


# 予約フォーム（GET）と登録（POST）。入力を受け取って Reservation に保存します。
# 店舗未選択の時は「大原亭」を入れて、デモとして流れが止まらないようにしています。
@reservation_bp.route("/reserve", methods=["GET", "POST"])
def reserve():
    """架空の居酒屋を含む店舗の予約処理"""
    if request.method == "POST":
        user_name = request.form.get("user_name")
        shop_name = request.form.get("shop_name")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        people = request.form.get("people")
        comment = request.form.get("comment")

        # 入力チェック
        if not user_name or not date_str or not time_str or not people:
            flash("必須項目をすべて入力してください。", "error")
            return redirect(url_for("reservation.reserve"))

        # 日付・時間変換
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            flash("日付または時間の形式が正しくありません。", "error")
            return redirect(url_for("reservation.reserve"))

        # 店舗未選択時 → 架空の居酒屋を設定
        if not shop_name:
            shop_name = "居酒屋 大原亭 立川キャンパス店"

        # データベース保存
        new_reservation = Reservation(
            user_name=user_name,
            shop_name=shop_name,
            date=date,
            time=time,
            people=int(people),
            comment=comment
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f"{shop_name} の予約が完了しました！", "success")
        return redirect(url_for("reservation.thanks"))

    # GETリクエスト時 → フォーム表示
    reservations = Reservation.query.order_by(Reservation.created_at.desc()).all()

    # 店舗一覧に架空店舗を追加
    extended_shops = SHOP_LIST + [
        {"name": "居酒屋 大原亭 立川キャンパス店", "lat": 35.6962, "lng": 139.4136}
    ]

    return render_template("reserve.html", reservations=reservations, shop_list=extended_shops)


# 完了画面。ここは表示だけ。
@reservation_bp.route("/thanks")
def thanks():
    """予約完了ページ"""
    return render_template("thanks.html")


# 予約履歴。最新順で出してます（デモ用なので全ユーザー共通）。
@reservation_bp.route("/reservation_history")
def reservation_history():
    """予約履歴一覧"""
    reservations = Reservation.query.order_by(Reservation.date.desc(), Reservation.time.desc()).all()
    return render_template("reservations.html", reservations=reservations)
