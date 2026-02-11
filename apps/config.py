import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///local.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 位置情報チェック機能のON/OFF (True: 有効, False: 無効)
LOCATION_CHECK_ENABLED = True

# 投稿可能な店舗からの最大距離（メートル）
MAX_DISTANCE_METERS = 300


# 店舗名と緯度(lat)と経度(lng)を設定する
SHOP_LIST = [
    {"name": "スターバックス立川南口店スターバックス コーヒー グランデュオ立川店", "lat": 35.697307015553605, "lng": 139.41478041838099,"url": "https://store.starbucks.co.jp/detail-1400/?utm_source=Bing&utm_medium=organic&utm_campaign=store&utm_content=1400%22%7D"},                    
    {"name": "タリーズコーヒー ルミネ立川店", "lat": 35.69844690359814, "lng": 139.4137547311192,"url": "https://shop.tullys.co.jp/detail/5483141"},
    {"name": "ドトールコーヒーショップ 立川南口駅前店", "lat": 35.69702943349045, "lng": 139.41444263450072 ,"url": "https://shop.doutor.co.jp/doutor/spot/detail?code=1011307"},
    {"name": "カフェ・ベローチェ 立川フロム中武店", "lat": 35.69985782584284, "lng": 139.41555637791217 ,"url": "https://c-united.co.jp/veloce/"},
    {"name": "マクドナルド立川南口店", "lat": 35.69712388111498, "lng": 139.41276783689034 ,"url": "https://map.mcdonalds.co.jp/map/13679"},
    {"name": "モスバーガー立川南口店", "lat": 35.69646941051727, "lng": 139.41609526083343 ,"url": "https://www.mos.jp/"},
    {"name": "サイゼリヤ 立川北口店", "lat": 35.69980088894923, "lng": 139.41217281488352 ,"url": "https://shop.saizeriya.co.jp/sz_restaurant/spot/detail?code=0842"},
    {"name": "ガスト 立川駅南口店（から好し取扱店）", "lat": 35.697918039351535, "lng": 139.41191531656597 ,"url": "https://www.skylark.co.jp/"},
    {"name": "ラーメン二郎立川店", "lat": 35.696871120979765, "lng": 139.40968829778637 },
    {"name": "一風堂立川店", "lat": 35.698514717352424, "lng": 139.41433907497876 ,"url": "https://stores.ippudo.com/1099"},
    {"name": "ガブ飲み処 鬼ぞりゴリラ 立川店", "lat": 35.70069146222663, "lng": 139.41634239402308,"url": "https://onigori.five-group.co.jp/shoplist/tachikawa/?utm_source=google&utm_medium=GBP"},
    {"name": "土鍋ご飯 然々(SHIKA-JIKA)", "lat": 35.698186105108014 , "lng": 139.4138661768292 ,"url": "https://www.ecute.jp/tachikawa/shop/4624"},
    {"name": "しんぱち食堂 立川曙町店", "lat": 35.70180538525037, "lng": 139.41580426333684 ,"url": "https://www.shinpachi-shokudo.com/"},
    {"name": "おいしいご飯屋さん笹", "lat": 35.696213422130654, "lng": 139.41814410119164 ,"url": "https://oishiigohan-sasa.com/"},
    {"name": "GALERA TACHIKAWA", "lat": 35.69957729181409, "lng": 139.4162324368905 ,"url": "https://galera.tokyo/"},
    {"name": "あなたに会えてよかった。", "lat": 35.6987896496665, "lng": 139.4118163368904 },
    {"name": "自然定食【いい日々】", "lat": 35.705019125698136, "lng": 139.41817286387607, "url": "https://www.instagram.com/iihibi_tachikawa/#"},
    {"name": "から好し 立川駅南口店", "lat": 35.69689404213645, "lng": 139.41418450485628 ,"url": "https://store-info.skylark.co.jp/karayoshi/map/018206/"},
    {"name": "Italianbar ATTACHMENT 立川店", "lat": 35.700891913498744, "lng": 139.41484252894944, "url": "https://ggp2514.gorp.jp/"},
    {"name": "洋膳食堂 新豚亭", "lat": 35.69905600339688, "lng": 139.41862550011345 },
    {"name": "島想食堂", "lat": 35.696208369575785, "lng": 139.4192052847702, "url": "https://shimaomou.com/"},
    {"name": "chawan エキュート立川店", "lat": 35.69753149740313, "lng": 139.41331356757664 ,"url": "https://store-info.skylark.co.jp/chawan/map/019005/"},
    {"name": "菊松食堂", "lat": 35.70334655677978, "lng": 139.4134784903222 ,"url": "https://kikumatsusyokudou.owst.jp/"},
    {"name": "Solito Piatto（ソリトピアット）", "lat": 35.697581758273465, "lng": 139.41693229402284 ,"url": "https://www.instagram.com/solito.piatto/?igsh=cGh0Y3E5bWltNWcz#"},
    {"name": "ふみちゃんキッチン", "lat": 35.697387441623675, "lng": 139.41845012100814 ,"url": "https://www.fumichankitchen.com/"},
    {"name": "愛ル豚～肉の創作酒場～", "lat": 35.699005400833556, "lng": 139.41229960566497 ,"url": "https://airutontachikawa.com/"},
    {"name": "ひなたかなた", "lat": 35.69920220310922, "lng": 139.41540789402288 ,"url": "http://hinata-kanata.com/"},
    {"name": "大衆海鮮居酒屋 おっ魚", "lat": 35.696402621737846, "lng": 139.41582461306692 ,"url": "https://hitosara.com/0006141968/?cid=ovt_yg_ss_00564233&yclid=YSS.1000324960.EAIaIQobChMI8uCipsCMkgMVQX0PAh0kYTHeEAAYAiAAEgIzFPD_BwE&sa_p=YSA&sa_cc=1000324960&sa_t=1768444278582&sa_ra=C5%22%7D"},
    {"name": "焼SOBA osakaきっちん。エキュート立川", "lat": 35.69842353369124, "lng": 139.4150623419028 ,"url": "https://www.ecute.jp/tachikawa/shop/3866"},
    {"name": "厨 くりや 立川", "lat": 35.695165097794664, "lng": 139.41461556572605 ,"url": "https://ghj9500.gorp.jp/"},
    {"name": "磯丸水産 立川北口大通り店", "lat": 35.69987167631022, "lng": 139.41462693635134 ,"url": "https://isomaru.jp/1478/"},
    {"name": "ジョナサン 立川北口店", "lat": 35.70070510014384, "lng": 139.41230489564782 ,"url": "https://www.skylark.co.jp/jonathan/index.html"},
    {"name": "デニーズ立川南店", "lat": 35.691562477182096, "lng": 139.41766631099156 ,"url": "https://www.dennys.jp/"},
    {"name": "サイゼリヤ 立川ビックカメラ店", "lat": 35.6995158024834, "lng":139.4145193514676  ,"url": "https://shop.saizeriya.co.jp/sz_restaurant/spot/detail?code=0747"},
    {"name": "バーミヤン 立川駅北口店", "lat": 35.701853585193916, "lng": 139.41144202448388 ,"url": "https://www.skylark.co.jp/bamiyan/index.html"},
    {"name": "ガスト 立川駅南口店", "lat": 35.697202298617135, "lng": 139.4117459956476 ,"url": "https://www.skylark.co.jp/"},
    {"name": "夢庵食堂 立川駅南口店", "lat": 35.69705456383438, "lng": 139.41244290913954 ,"url": "https://www.skylark.co.jp/ym_shokudo/index.html"},
    {"name": "ガスト 立川曙橋点", "lat": 35.700629499049164, "lng": 139.41523920913974 ,"url": "https://store-info.skylark.co.jp/gusto/map/018952/"},
    {"name": "ウェンディーズ ファーストキッチン 立川フロム中武店", "lat": 35.69989233805591, "lng": 1139.414650139828 ,"url": "https://wendys-firstkitchen.co.jp/shop/map.php?shopid=30"},
    {"name": "松屋 立川北口店", "lat": 35.698932655016584, "lng": 139.41158905517204 ,"url": "https://pkg.navitime.co.jp/matsuyafoods/spot/detail?code=0000000655"},
    {"name": "松屋 立川錦町店", "lat": 35.69626653007649, "lng": 139.4151118091395 ,"url": "https://pkg.navitime.co.jp/matsuyafoods/spot/detail?code=0000000144"},
    {"name": "バケット ルミネ立川店", "lat": 35.6984769787399, "lng": 139.4138026956477 ,"url": "https://www.saint-marc-hd.com/baqet/shop/231/"},
    {"name": "とり鉄 立川店", "lat": 35.70028710096613, "lng": 139.4151142533199 ,"url": "https://gj0m300.gorp.jp/"},
    {"name": "マイアミガーデン立川店", "lat": 35.69962561290832, "lng": 139.41348179564778 ,"url": "https://miami-garden.jp/"},
    {"name": "日本酒バル ファンキー原田2 波平Essence", "lat": 35.69702420738449, "lng": 139.4153854398279 },
    {"name": "大むら", "lat": 35.69455488637699, "lng": 139.3965283692611 ,"url": "https://soba-oomura.com/menu/"},
    {"name": "燗アガリ立川", "lat": 35.69652835114054, "lng":139.41371733982768  ,"url": "https://www.bing.com/search?q=%E7%87%97%E3%82%A2%E3%82%AC%E3%83%AA%E7%AB%8B%E5%B7%9D&cvid=2946fde7531743c88d8842f682f74da9&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOTIGCAEQABhAMgYIAhAAGEAyBggDEAAYQDIGCAQQRRg9MgYIBRBFGDwyBggGEEUYPDIICAcQ6QcY_FXSAQgxMDM4ajBqNKgCCLACAQ&FORM=ANAB01&ucpdpc=UCPD&PC=TBTS%22%7D"} ,
    {"name": "肉汁餃子のダンダダン 立川北口店", "lat": 35.699146026300035, "lng": 139.4151729244838 },
    {"name": "ビビ 立川本店", "lat": 35.695414857641886, "lng": 139.41711156681149 ,"url": "https://vvt.shopinfo.jp/"},
    {"name": "お魚総本家 立川店", "lat": 35.69693542919938, "lng": 139.41257696866373 ,"url": "https://osakanasohonke-tachikawa.com/"},
    {"name": "肉バル酒場GB 立川南口店", "lat": 35.69592674132154, "lng":139.4128961263357 },
    {"name": "スカイレストラン ハレアス", "lat": 36.01445530796187, "lng": 140.97777230717355 ,"url": "https://www.hotel-emisia.com/tokyotachikawa/lp/hareus/"},
    {"name": "魚トの神 立川", "lat": 35.6974592675163, "lng": 139.4113774956476 ,"url": "https://totonokami-tachikawa.owst.jp/"},
    {"name": "九州料理 二代目もつ鍋わたり 立川店", "lat": 35.69651412975187, "lng": 139.41311550913952 ,"url": "https://watari2nd-tachikawa.com/"},
    {"name": "Xyon Tokyo 立川北口店", "lat": 35.69980319995239, "lng": 139.4151823226316 },
    {"name": "SHIBASAKI CAMP", "lat": 35.69497377159062, "lng": 139.41427694167984 ,"url": "https://shibasakicamp.com/"},
    {"name": "焼売のジョー 立川店", "lat": 35.69701890299564, "lng": 139.4153913244837 ,"url": "https://www.shumainojo.com/%E5%BA%97%E8%88%97%E6%83%85%E5%A0%B1"},
    {"name": "伊達かつ・グランデュオ立川店", "lat": 35.697419702557625, "lng": 139.41446753982783 ,"url": "https://date-katsu-tachikawa.com/"},
    {"name": "博多もつ鍋だいやめ立川北口店", "lat": 35.69943153645821, "lng": 139.4135567244838 ,"url": "https://daiyame-tachikawa.stores.jp/"},
    {"name": "曙町場内酒場", "lat": 35.70042856125257, "lng": 139.4110679937956 ,"url": "https://www.bing.com/search?q=曙町場内酒場&cvid=50a3e63f9c2548b4ae85332869bfbcf0&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOTIGCAEQABhAMgYIAhAAGEAyBggDEAAYQDIGCAQQABhAMgYIBRBFGD0yBggGEEUYPDIGCAcQRRg8MggICBDpBxj8VdIBBzgzM2owajSoAgiwAgE&FORM=ANAB01&ucpdpc=UCPD&PC=TBTS%22%7D"},
    {"name": "野菜と創作curry 舞", "lat": 35.70355100818875, "lng": 139.4147778361237 ,"url": "https://www.instagram.com/spicecurry_mai/?igshid=MjEwN2IyYWYwYw%3D%3D"},
    {"name": "ボンガスカレーダイニング", "lat": 35.69769758395462, "lng":139.41088533797551 ,"url": "https://bongas-curry-dining.owst.jp/"},
    {"name": "underthecascade", "lat": 35.70447190708136, "lng": 139.41218926681205 ,"url": "https://g293468.gorp.jp/"},
    {"name": "蔵CAFE ヤマスカフェ", "lat": 35.696691777191404, "lng": 139.40274261099174 ,"url": "https://yamaskuracafe.wixsite.com/website"},
    {"name": "ゑびす屋 場外馬券場前店", "lat": 35.7101392450532, "lng": 139.42622812647244 ,"url": "https://www.annex-tachikawa.com/store/suzuran166/"},
    {"name": "幸喜寿し", "lat": 35.701296523479456, "lng": 139.41658842263166 },
    {"name": "大原亭", "lat": 35.696184471180345, "lng": 139.4135754022215, "reservation_url": "/shop/oharatei#reserve"}
]

CROWD_LEVELS = [
    "空いている",
    "やや混雑",
    "満席",
]

# 店舗名,緯度,経度から位置情報を取得する辞書を作成
SHOP_LOCATIONS = {}
for shop in SHOP_LIST:
    location = {
        "lat": shop["lat"],
        "lng": shop["lng"]
    }
    # reservation_urlが存在する場合のみ追加
    if "reservation_url" in shop:
        location["reservation_url"] = shop["reservation_url"]
    
    SHOP_LOCATIONS[shop["name"]] = location

# 店舗詳細情報（カテゴリ、説明、看板メニュー）

SHOP_DETAILS = {
    # カフェ
    "スターバックス立川南口店スターバックス コーヒー グランデュオ立川店": {
        "category": "カフェ",
        "description": "世界的に有名なコーヒーチェーン。落ち着いた雰囲気で勉強や仕事にも最適。",
        "signature": "キャラメルマキアート、季節限定フラペチーノ"
    },
    "タリーズコーヒー ルミネ立川店": {
        "category": "カフェ",
        "description": "アメリカシアトル発のカフェ。豊富なドリンクメニューと居心地の良い空間。",
        "signature": "ロイヤルミルクティー、タリーズハニーミルクラテ"
    },
    "ドトールコーヒーショップ 立川南口駅前店": {
        "category": "カフェ",
        "description": "リーズナブルで気軽に利用できる日本発のコーヒーチェーン。朝の通勤時にも人気。",
        "signature": "ブレンドコーヒー、ミラノサンド"
    },
    "カフェ・ベローチェ 立川フロム中武店": {
        "category": "カフェ",
        "description": "手頃な価格で本格的なコーヒーが楽しめるイタリアンカフェ。",
        "signature": "カフェラテ、ベルギーワッフル"
    },
    
    # ファストフード
    "マクドナルド立川南口店": {
        "category": "ファストフード",
        "description": "世界最大のハンバーガーチェーン。24時間営業で深夜も利用可能。",
        "signature": "ビッグマック、ポテトフライ、マックシェイク"
    },
    "モスバーガー立川南口店": {
        "category": "ファストフード",
        "description": "日本発の人気ハンバーガーチェーン。新鮮な野菜とこだわりのパティが特徴。",
        "signature": "モスバーガー、テリヤキバーガー"
    },
    "ウェンディーズ ファーストキッチン 立川フロム中武店": {
        "category": "ファストフード",
        "description": "アメリカンスタイルのハンバーガーと和風メニューの融合。",
        "signature": "ベーコンマッシュルームメルト、ベーコンエッグバーガー"
    },
    "松屋 立川北口店": {
        "category": "牛丼",
        "description": "24時間営業の牛丼チェーン。リーズナブルで早い提供が魅力。",
        "signature": "牛めし、牛焼肉定食"
    },
    "松屋 立川錦町店": {
        "category": "牛丼",
        "description": "24時間営業の牛丼チェーン。深夜も営業しており便利。",
        "signature": "牛めし、カレー"
    },
    
    # ファミレス
    "サイゼリヤ 立川北口店": {
        "category": "イタリアンファミレス",
        "description": "低価格で本格的なイタリアンが楽しめるファミリーレストラン。学生に人気。",
        "signature": "ミラノ風ドリア、マルゲリータピザ"
    },
    "サイゼリヤ 立川ビックカメラ店": {
        "category": "イタリアンファミレス",
        "description": "ビックカメラ内にあるイタリアンファミレス。買い物ついでに立ち寄れる。",
        "signature": "ミラノ風ドリア、プロシュート"
    },
    "ガスト 立川駅南口店（から好し取扱店）": {
        "category": "ファミリーレストラン",
        "description": "豊富なメニューが揃うファミレス。から好しメニューも楽しめる。",
        "signature": "ハンバーグ、から好し唐揚げ定食"
    },
    "ガスト 立川駅南口店": {
        "category": "ファミリーレストラン",
        "description": "家族連れに人気のファミレス。和洋中のメニューが充実。",
        "signature": "ハンバーグ、若鶏の唐揚げ"
    },
    "ガスト 立川曙橋点": {
        "category": "ファミリーレストラン",
        "description": "多彩なメニューと手頃な価格が魅力のファミレス。",
        "signature": "デミグラスハンバーグ、和風おろしハンバーグ"
    },
    "ジョナサン 立川北口店": {
        "category": "ファミリーレストラン",
        "description": "落ち着いた雰囲気のファミレス。ランチやディナーに最適。",
        "signature": "ハンバーグ＆海老フライ、パスタメニュー"
    },
    "デニーズ立川南店": {
        "category": "ファミリーレストラン",
        "description": "アメリカンスタイルのファミレス。パンケーキが人気。",
        "signature": "パンケーキ、ハンバーグステーキ"
    },
    "バーミヤン 立川駅北口店": {
        "category": "中華ファミレス",
        "description": "手頃な価格で中華料理が楽しめるファミレス。",
        "signature": "餃子、チャーハン、麻婆豆腐"
    },
    "夢庵食堂 立川駅南口店": {
        "category": "和食ファミレス",
        "description": "和食中心のファミレス。定食メニューが豊富。",
        "signature": "天丼、とんかつ定食"
    },
    "バケット ルミネ立川店": {
        "category": "ベーカリーレストラン",
        "description": "焼きたてパン食べ放題が人気のレストラン。",
        "signature": "焼きたてパン食べ放題、パスタランチ"
    },
    
    # ラーメン
    "ラーメン二郎立川店": {
        "category": "ラーメン",
        "description": "全国に熱狂的なファンを持つラーメンの名店。大盛り無料のボリューム満点ラーメン。",
        "signature": "小ラーメン（野菜マシマシ、ニンニク入り）"
    },
    "一風堂立川店": {
        "category": "ラーメン",
        "description": "博多とんこつラーメンの人気チェーン。濃厚なスープと細麺が特徴。",
        "signature": "白丸元味、赤丸新味"
    },
    
    # 居酒屋
    "ガブ飲み処 鬼ぞりゴリラ 立川店": {
        "category": "居酒屋",
        "description": "リーズナブルな価格で飲み放題が楽しめる人気居酒屋。若者に人気。",
        "signature": "飲み放題コース、唐揚げ"
    },
    "大衆海鮮居酒屋 おっ魚": {
        "category": "海鮮居酒屋",
        "description": "新鮮な魚介類が自慢の大衆居酒屋。刺身盛り合わせが絶品。",
        "signature": "刺身盛り合わせ、焼き魚"
    },
    "磯丸水産 立川北口大通り店": {
        "category": "海鮮居酒屋",
        "description": "24時間営業の海鮮居酒屋。深夜も新鮮な海鮮が楽しめる。",
        "signature": "浜焼き、海鮮丼"
    },
    "とり鉄 立川店": {
        "category": "焼き鳥居酒屋",
        "description": "串焼きと鶏料理が自慢の居酒屋。コスパ抜群。",
        "signature": "焼き鳥盛り合わせ、鶏の唐揚げ"
    },
    "日本酒バル ファンキー原田2 波平Essence": {
        "category": "日本酒バル",
        "description": "豊富な日本酒が揃うバル。日本酒好きにおすすめ。",
        "signature": "日本酒飲み比べ、季節の一品料理"
    },
    "肉汁餃子のダンダダン 立川北口店": {
        "category": "餃子居酒屋",
        "description": "肉汁たっぷりの焼き餃子が名物。ビールとの相性抜群。",
        "signature": "肉汁餃子、チャーハン"
    },
    "お魚総本家 立川店": {
        "category": "海鮮居酒屋",
        "description": "新鮮な魚介料理が楽しめる居酒屋。",
        "signature": "刺身定食、海鮮丼"
    },
    "肉バル酒場GB 立川南口店": {
        "category": "肉バル",
        "description": "肉料理が充実したバル。ワインとの相性も抜群。",
        "signature": "熟成肉ステーキ、ローストビーフ"
    },
    "魚トの神 立川": {
        "category": "海鮮居酒屋",
        "description": "新鮮な魚料理が自慢の居酒屋。",
        "signature": "刺身、焼き魚"
    },
    "Xyon Tokyo 立川北口店": {
        "category": "ダイニングバー",
        "description": "おしゃれな雰囲気のダイニングバー。デートにも最適。",
        "signature": "クラフトビール、創作料理"
    },
    "曙町場内酒場": {
        "category": "居酒屋",
        "description": "地元で人気の居酒屋。アットホームな雰囲気。",
        "signature": "焼き鳥、もつ煮込み"
    },
    "燗アガリ立川": {
        "category": "日本酒居酒屋",
        "description": "厳選された日本酒が楽しめる大人の隠れ家。",
        "signature": "日本酒各種、季節の酒肴"
    },
    
    # 和食・定食
    "土鍋ご飯 然々(SHIKA-JIKA)": {
        "category": "和食",
        "description": "土鍋で炊いたご飯が絶品の和食店。素材にこだわった料理が魅力。",
        "signature": "土鍋ご飯定食、季節の一品料理"
    },
    "しんぱち食堂 立川曙町店": {
        "category": "定食",
        "description": "ボリューム満点の定食が人気。コスパ抜群で学生に人気。",
        "signature": "から揚げ定食、生姜焼き定食"
    },
    "おいしいご飯屋さん笹": {
        "category": "定食",
        "description": "家庭的な味わいの定食が楽しめる食堂。",
        "signature": "日替わり定食、焼き魚定食"
    },
    "自然定食【いい日々】": {
        "category": "自然食",
        "description": "健康志向の自然食が楽しめる定食屋。",
        "signature": "玄米定食、野菜たっぷりランチ"
    },
    "から好し 立川駅南口店": {
        "category": "唐揚げ専門",
        "description": "サクサクの唐揚げが自慢の専門店。",
        "signature": "から揚げ定食、チキン南蛮"
    },
    "洋膳食堂 新豚亭": {
        "category": "洋食",
        "description": "洋食メニューが充実した食堂。",
        "signature": "とんかつ、ハンバーグ"
    },
    "島想食堂": {
        "category": "定食",
        "description": "沖縄料理が楽しめる食堂。",
        "signature": "ゴーヤチャンプルー、ソーキそば"
    },
    "chawan エキュート立川店": {
        "category": "丼もの",
        "description": "駅ナカで気軽に丼ものが楽しめる。",
        "signature": "親子丼、天丼"
    },
    "菊松食堂": {
        "category": "定食",
        "description": "昔ながらの定食が楽しめる食堂。",
        "signature": "生姜焼き定食、さば味噌定食"
    },
    "厨 くりや 立川": {
        "category": "和食",
        "description": "旬の食材を使った和食が楽しめる。",
        "signature": "季節の会席、刺身定食"
    },
    "大むら": {
        "category": "そば",
        "description": "本格的な手打ちそばが味わえる名店。",
        "signature": "もりそば、天ざるそば"
    },
    "幸喜寿し": {
        "category": "寿司",
        "description": "新鮮なネタが自慢の寿司屋。",
        "signature": "にぎり寿司、ちらし寿司"
    },
    
    # 洋食・イタリアン
    "GALERA TACHIKAWA": {
        "category": "イタリアン",
        "description": "本格的なイタリア料理が楽しめるレストラン。",
        "signature": "生パスタ、石窯ピザ"
    },
    "Italianbar ATTACHMENT 立川店": {
        "category": "イタリアンバル",
        "description": "カジュアルにイタリアンが楽しめるバル。ワインも豊富。",
        "signature": "アヒージョ、パスタ"
    },
    "Solito Piatto（ソリトピアット）": {
        "category": "イタリアン",
        "description": "こだわりのイタリアン料理とワイン。",
        "signature": "自家製パスタ、リゾット"
    },
    "伊達かつ・グランデュオ立川店": {
        "category": "とんかつ",
        "description": "サクサクのとんかつが自慢の専門店。",
        "signature": "ロースかつ定食、ヒレかつ定食"
    },
    
    # もつ鍋・鍋料理
    "九州料理 二代目もつ鍋わたり 立川店": {
        "category": "もつ鍋",
        "description": "本場博多のもつ鍋が楽しめる専門店。コラーゲンたっぷり。",
        "signature": "もつ鍋、明太子"
    },
    "博多もつ鍋だいやめ立川北口店": {
        "category": "もつ鍋",
        "description": "博多風のもつ鍋が自慢。スープが絶品。",
        "signature": "もつ鍋（醤油・味噌）"
    },
    
    # その他専門店
    "焼SOBA osakaきっちん。エキュート立川": {
        "category": "焼きそば",
        "description": "駅ナカで本格的な焼きそばが楽しめる。",
        "signature": "焼きそば、お好み焼き"
    },
    "焼売のジョー 立川店": {
        "category": "焼売専門",
        "description": "できたての熱々焼売が自慢。",
        "signature": "焼売、餃子"
    },
    "ビビ 立川本店": {
        "category": "韓国料理",
        "description": "本格的な韓国料理が楽しめる。",
        "signature": "サムギョプサル、チーズタッカルビ"
    },
    "野菜と創作curry 舞": {
        "category": "カレー",
        "description": "野菜たっぷりの創作カレー。スパイスにこだわり。",
        "signature": "季節野菜のカレー、スパイスカレー"
    },
    "ボンガスカレーダイニング": {
        "category": "カレー",
        "description": "スパイスが香る本格カレー専門店。",
        "signature": "チキンカレー、キーマカレー"
    },
    
    # カフェ・レストラン
    "あなたに会えてよかった。": {
        "category": "カフェレストラン",
        "description": "おしゃれな雰囲気のカフェレストラン。女性に人気。",
        "signature": "パスタランチ、デザートプレート"
    },
    "ふみちゃんキッチン": {
        "category": "家庭料理",
        "description": "家庭的な温かみのある料理が楽しめる。",
        "signature": "日替わりランチ、手作りデザート"
    },
    "愛ル豚～肉の創作酒場～": {
        "category": "創作居酒屋",
        "description": "豚肉料理の創作メニューが楽しめる酒場。",
        "signature": "豚の角煮、しゃぶしゃぶ"
    },
    "ひなたかなた": {
        "category": "カフェダイニング",
        "description": "落ち着いた空間でゆったり食事ができる。",
        "signature": "ランチプレート、自家製スイーツ"
    },
    "マイアミガーデン立川店": {
        "category": "アメリカン",
        "description": "アメリカンスタイルの料理とカクテル。",
        "signature": "ステーキ、ハンバーガー"
    },
    "SHIBASAKI CAMP": {
        "category": "アウトドアダイニング",
        "description": "アウトドア気分が楽しめるダイニング。",
        "signature": "BBQ料理、クラフトビール"
    },
    "underthecascade": {
        "category": "カフェ",
        "description": "隠れ家的なカフェ。落ち着いた雰囲気。",
        "signature": "スペシャリティコーヒー、手作りケーキ"
    },
    "蔵CAFE ヤマスカフェ": {
        "category": "古民家カフェ",
        "description": "蔵を改装した趣のあるカフェ。",
        "signature": "コーヒー、自家製スイーツ"
    },
    "スカイレストラン ハレアス": {
        "category": "レストラン",
        "description": "高層階からの眺望が素晴らしいレストラン。",
        "signature": "コース料理、ビュッフェ"
    },
    "ゑびす屋 場外馬券場前店": {
        "category": "居酒屋",
        "description": "競馬場近くの活気ある居酒屋。",
        "signature": "焼き鳥、もつ煮"
    },
    
    # 架空店舗
    "大原亭": {
        "category": "居酒屋",
        "description": "立川キャンパス前の人気居酒屋。学生の憩いの場。",
        "signature": "唐揚げ、レモンサワー"
    }
}