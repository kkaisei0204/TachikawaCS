"""
top_page Blueprint
トップページ関連の機能をまとめるBlueprint
"""

from flask import Blueprint

# top Blueprint を定義
top = Blueprint(
    'top',
    __name__,
    template_folder='templates',
    static_folder='static'
)
