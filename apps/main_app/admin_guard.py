# このファイルは管理者ルートの共通ガードを定義するためのもの
# このファイルはシステム全体におけるセキュリティーのかなめとなるため、ルートごとに個別にガードを実装するのではなく、共通のデコレータとしてまとめています。
"""
管理者ルート共通ガード

目的：
- 管理者ページへのアクセス制御を一箇所に集約
- ルートごとの「書き忘れ」「条件ミス」を防ぐ
"""
# ライブラリのインポート
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

# 管理者権限が必要なルートにこのデコレータを付けることで、アクセス制御を行います。
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
    # @wrapsを使うことで、元の関数(view_func)の名前やドキュメントを維持します。
    # これがないと、FlaskがURLを関数に紐付ける際に混乱する可能性があります。
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # is_admin が無い/False のとき弾く（安全側）
        # 管理者権限の有無は管理者権限判定クラスをインスタンス化してuserクラスで管理者権限判定プロパティを定義している
        if not getattr(current_user, "is_admin", False):
            flash("管理者権限が必要です", "error")

            # 判定の結果管理者権限を持っていないためトップへリダイレクトします
            return redirect(url_for("main.index", next=request.full_path))
        # 管理者権限がある場合は、元のビュー関数を呼び出して処理を続行します
        return view_func(*args, **kwargs)
    # wrapper関数を返すことで、デコレータとして機能します。
    return wrapper
