// スマホ特有のイライラする挙動を抑える
// mobileutils.js
// モバイル実機で「変な挙動を減らす」ための小物まとめ。
// 画面側（HTML/CSS）を触らずに済むように、JSで吸収できるところだけ対応しています。
// ※意図：ズーム/プルトゥリフ/バウンス/キーボード表示/オフライン通知など、スマホ固有の事故を減らす。

// DOMの準備ができてからイベントを貼ります（要素取得が失敗しないように）。
document.addEventListener('DOMContentLoaded', function() {
  
  // ボタン要素のダブルタップズーム防止
  // ボタン周りのダブルタップで、iOS Safari が勝手に拡大することがあるので抑制します。
  // touchend を拾って click に流す（passive:false じゃないと preventDefault が効かない）。
  const buttons = document.querySelectorAll('button, .btn, .rating-btn, .filter-btn');
  buttons.forEach(button => {
    button.addEventListener('touchend', function(e) {
      e.preventDefault();
      this.click();
    }, { passive: false });
  });
  
  // 2. プルトゥリフレッシュのような挙動を防ぐ
  // 画面最上部で下に引っ張るとページが“びよん”ってなる（プルトゥリフレッシュ風）挙動を抑えます。
  let startY = 0;
  document.addEventListener('touchstart', function(e) {
    startY = e.touches[0].pageY;
  }, { passive: true });
  
  document.addEventListener('touchmove', function(e) {
    const y = e.touches[0].pageY;
    // 上方向にスクロールしていて、既にページトップにいる場合
    if (y > startY && window.scrollY === 0) {
      e.preventDefault();
    }
  }, { passive: false });
  
  // 3. iOS Safariのバウンス効果を制限
  // iOS のバウンス（オーバースクロール）対策。
  // .scrollable を付けた要素だけはスクロールを許可、他は（必要になったら）ここで抑制する想定。
  document.body.addEventListener('touchmove', function(e) {
    if (e.target.classList.contains('scrollable')) {
      return;
    }
    // 特定の要素以外でのバウンスを防ぐ
  }, { passive: false });
  
  // 4. モバイルキーボード表示時のレイアウト調整
  // キーボードが出たときに入力欄が隠れやすいので、フォーカス時に中央付近へ寄せます。
  const inputs = document.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      // 入力フィールドにフォーカス時、少しスクロール
      setTimeout(() => {
        this.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 300);
    });
  });
  
  // 5. オンライン/オフライン状態の検知
  // オフライン時は上部に赤帯を出す。ネット復帰したら消す。
  window.addEventListener('online', function() {
    console.log('オンラインに復帰しました');
    const offlineNotice = document.getElementById('offline-notice');
    if (offlineNotice) {
      offlineNotice.style.display = 'none';
    }
  });
  
  window.addEventListener('offline', function() {
    console.log('オフラインになりました');
    let offlineNotice = document.getElementById('offline-notice');
    if (!offlineNotice) {
      offlineNotice = document.createElement('div');
      offlineNotice.id = 'offline-notice';
      // ここはCSSを増やさずに済ませるため、最低限のスタイルだけ直書きしています。
      offlineNotice.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ff6b6b;
        color: white;
        padding: 10px;
        text-align: center;
        z-index: 10000;
        font-size: 14px;
      `;
      offlineNotice.textContent = '⚠️ オフライン状態です';
      document.body.appendChild(offlineNotice);
    }
    offlineNotice.style.display = 'block';
  });
  
  // 6. スワイプジェスチャー検知（将来の拡張用）
  // 右/左スワイプ検知（今はログ出すだけ）。将来「戻る」「次へ」などの導線に使える枠。
  let touchStartX = 0;
  let touchEndX = 0;
  
  document.addEventListener('touchstart', function(e) {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  
  document.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });
  
  function handleSwipe() {
    const swipeThreshold = 100;
    const diff = touchEndX - touchStartX;
    
    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        // 右スワイプ
        console.log('右スワイプ検知');
      } else {
        // 左スワイプ
        console.log('左スワイプ検知');
      }
    }
  }
  
  // 7. ビューポート高さの動的調整（モバイルブラウザのアドレスバー対応）
  // モバイルのアドレスバーで 100vh がズレる問題対策。
  // CSS側で height: calc(var(--vh) * 100); みたいに使う想定です。
  function setVH() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  
  setVH();
  window.addEventListener('resize', setVH);
  window.addEventListener('orientationchange', setVH);
  
  // 8. 慣性スクロールの有効化（iOS Safari）
  // iOS の慣性スクロールを有効化（スクロールがカクつくのを軽減）。
  document.body.style.webkitOverflowScrolling = 'touch';
  
});


// PWAまわり（将来対応のためのフックだけ置いてます）
// ※今はService Workerを登録していないので、ここはログだけ。
// Service Worker登録（PWA対応）
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    // Service Workerは必要に応じて後で実装
    console.log('Service Worker対応ブラウザ');
  });
}


// 端末が「インストールできますよ」と言ってきた時のイベント。
// deferredPrompt を握っておくと、任意のタイミングで prompt() できます（必要になったら）。
// インストールプロンプト（PWA）
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  console.log('PWAインストール可能');
  e.preventDefault();
  deferredPrompt = e;
  
  // インストールバナーを表示（オプション）
  const installBanner = document.getElementById('install-banner');
  if (installBanner) {
    installBanner.style.display = 'block';
  }
});


// 向き変更はUI崩れの原因になりやすいので、ログだけでも残しておくと切り分けが楽です。
// 画面の向き変更検知
window.addEventListener('orientationchange', function() {
  console.log('画面向き変更:', screen.orientation?.type || window.orientation);
});
