"""
EMERGENCY_FIX.py
表示崩れを緊急修正するスクリプト

使用方法:
  python EMERGENCY_FIX.py
"""

import os
import re

BASE_DIR = r"C:\systems\apps"

# 修正用のCSSコード
MOBILE_FIX_CSS = """
  <style>
    /* 緊急修正：表示崩れ対策 */
    * {
      box-sizing: border-box !important;
    }
    
    html, body {
      margin: 0 !important;
      padding: 0 !important;
      overflow-x: hidden !important;
      width: 100% !important;
      max-width: 100% !important;
    }
    
    .container {
      width: 100% !important;
      max-width: 1200px !important;
      margin: 0 auto !important;
      padding: 30px 20px !important;
      box-sizing: border-box !important;
    }
    
    /* ハンバーガーメニュー */
    .menu-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 998;
    }
    
    .menu-overlay.active {
      display: block;
    }
    
    /* モバイルメニュー */
    @media (max-width: 768px) {
      .container {
        padding: 20px 16px !important;
      }
      
      .menu-outer01 {
        position: fixed;
        top: 0;
        right: -100%;
        width: auto;
        min-width: 220px;
        max-width: 80%;
        height: 100vh;
        background: #fff;
        transition: right 0.3s ease;
        z-index: 999;
        overflow-y: auto;
        padding: 60px 0 20px;
        box-shadow: -2px 0 10px rgba(0,0,0,0.1);
      }
      
      .menu-outer01.active {
        right: 0;
      }
      
      .sample_menu_list01 {
        display: flex !important;
        flex-direction: column !important;
        padding: 0 !important;
        margin: 0 !important;
        gap: 0 !important;
      }
      
      .sample_menu_list01 li {
        width: 100%;
        border-bottom: none !important;
      }
      
      .sample_menu_list01 a {
        display: block;
        padding: 15px 25px !important;
        color: #333 !important;
        font-size: 14px !important;
        white-space: nowrap;
        text-decoration: none;
      }
      
      .sample_menu_list01 a:hover {
        background: #f5f5f5;
      }
      
      .sample_menu_list01 .user-info {
        margin-top: auto;
        border-top: none !important;
        background: #fff !important;
        padding: 20px 25px !important;
      }
      
      .sample_menu_list01 .user-info .user-link {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0 !important;
        font-size: 14px !important;
        color: #2d3748 !important;
        white-space: nowrap;
      }
      
      .sample_menu_list01 .user-icon-img {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50%;
        border: 2px solid #667eea;
      }
    }
    
    body.menu-open {
      overflow: hidden;
    }
    
    @media (max-width: 375px) {
      .container {
        padding: 15px 12px !important;
      }
    }
  </style>"""


FILES_TO_FIX = [
    os.path.join(BASE_DIR, "top_page", "templates", "index.html"),
    os.path.join(BASE_DIR, "topics_page", "templates", "topics.html"),
    os.path.join(BASE_DIR, "top_page", "templates", "user_page.html"),
    os.path.join(BASE_DIR, "post_page", "templates", "post.html"),
    os.path.join(BASE_DIR, "top_page", "templates", "admin.html"),
    os.path.join(BASE_DIR, "top_page", "templates", "admin_dashboard.html"),
    os.path.join(BASE_DIR, "top_page", "templates", "admin_reservations.html"),
]


def fix_file(filepath):
    """ファイルを修正"""
    print(f"修正中: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"ファイルが見つかりません")
        return False
    
    # バックアップ
    backup_path = filepath + ".bak"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 既存の<style>タグを削除（競合回避）
    content = re.sub(
        r'<style>.*?</style>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # </head>の直前に修正CSSを挿入
    if '</head>' in content:
        content = content.replace('</head>', MOBILE_FIX_CSS + '\n</head>')
    
    # viewportタグがなければ追加
    if 'name="viewport"' not in content:
        content = re.sub(
            r'(<meta\s+charset[^>]*>)',
            r'\1\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            content
        )
    
    # 保存
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"修正完了 (バックアップ: {backup_path})")
    return True


def main():
    print("=" * 60)
    print("緊急修正スクリプト - 表示崩れを修正します")
    print("=" * 60)
    print()
    
    success = 0
    fail = 0
    
    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            success += 1
        else:
            fail += 1
        print()
    
    print("=" * 60)
    print(f"修正完了: {success}ファイル")
    if fail > 0:
        print(f"失敗: {fail}ファイル")
    print("=" * 60)
    print()
    print("サーバーを再起動してください:")
    print("  Ctrl + C → python run.py")


if __name__ == '__main__':
    main()
