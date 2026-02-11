from flask import Blueprint, render_template

# 店舗紹介ページ（固定情報）。混雑投稿とは違って、SHOP_DETAILS の説明文を見せるだけの枠です。
# 「おすすめ店舗」みたいな見せ方をする時のベースにもなります。

# Blueprintの作成
restaurant_bp = Blueprint("restaurant", __name__, template_folder="templates", static_folder="static")

# 店舗紹介の一覧ページ。SHOP_LIST と SHOP_DETAILS を合体してテンプレへ渡します。
@restaurant_bp.route("/restaurant")
def restaurant_page():
    """飲食店ページ（店舗紹介）"""
    from apps.config import SHOP_LIST, SHOP_DETAILS
    
    # 店舗紹介用データを準備
    shops_data = []
    for shop in SHOP_LIST:
        shop_name = shop["name"]
        detail = SHOP_DETAILS.get(shop_name, {})
        shops_data.append({
            "name": shop_name,
            "category": detail.get("category", "該当しない"),
            "description": detail.get("description", ""),
            "signature": detail.get("signature", ""),
            "url": shop.get("url", "")
        })
    
    return render_template("restaurant.html", shops=shops_data)
