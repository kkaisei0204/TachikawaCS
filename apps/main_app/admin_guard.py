"""
管理者ルート共通ガード

目的：
- 管理者ページへのアクセス制御を一箇所に集約
- ルートごとの「書き忘れ」「条件ミス」を防ぐ
"""

from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user


def admin_required(view_func):
    """
    管理者のみ許可するデコレータ。

    前提：
    - @login_required が先に付いている（未ログインはログインへ飛ぶ）
    - current_user に is_admin が存在する

    挙動：
    - 管理者でない場合：メッセージ表示→トップへ戻す
    - （任意）next を付けておくと、管理者化された後に戻りやすい
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # is_admin が無い/False のとき弾く（安全側）
        if not getattr(current_user, "is_admin", False):
            flash("管理者権限が必要です", "error")

            # 管理画面に来ようとしていた場合の戻り先（任意）
            # 必要なければ next 関連は消してOK
            return redirect(url_for("main.index", next=request.full_path))
        return view_func(*args, **kwargs)

    return wrapper
