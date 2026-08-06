# v3.1 「参考サイト（pantograph.co.jp）にもっと寄せる」実装スペック

対象: `draft-v3/site/`（index.html / company.html / css/style.css / js/main.js）
前提: **文言は1文字も変えない**。配色は緑系のまま（参考元の紺・青は使わない）。ナビはハンバーガーのみ（オーナー指定）。
狙い: 参考元の「型（レイアウト・タイポ・罫線・帯・カードの作法）」を今より明確に踏襲する。

参考元の実測特徴（スクショから採取）
1. セクション見出し＝**極太の巨大英字**（黒・weight 800前後・行高0.85・字間ほぼ詰め）の**右横に小さな日本語**をベースライン揃えで置く（縦積みではない）
2. ページ左に**縦の細い罫線**が通り、コンテンツはその右から始まる。セクションの境目に横の細い罫線
3. 背景の淡い帯が**左右非対称にはみ出す**（全幅ベタ塗りではなく、片側だけ画面外まで伸びて反対側は手前で止まる）
4. 本文まわりに**巨大な極薄のウォーターマーク英字**（VISION 等）が敷いてある
5. サービスカード＝白カードの上辺に**ひし形（45度回転の正方形）のラベルバッジ**が半分めり込む。中は「01.（アクセント色）＋タイトル」の並び
6. ボタン＝**角丸なしのベタ塗り矩形**＋右端に**長い横線の矢印**
7. ヘッダーは常に不透明の白。右上端に**全高のダーク色 CONTACT ボタン**がぴったり付く
8. ヒーロー＝写真の上に**ベタ塗りの箱を敷いた文字**（見出しは白箱＋濃色文字、サブコピーは濃色箱＋白文字を1行ずつ）

## 実装する変更

### A. 共通タイポ
- Google Fonts の Barlow に **800** を追加（`family=Barlow:wght@600;700;800`）
- 本文 `body`: `letter-spacing: .04em; line-height: 2;`
- `.section-heading` を**横並び**に変更
  - `display:flex; align-items:baseline; gap:28px; flex-wrap:wrap; margin-bottom:64px;`
  - `h1,h2`: `font-family:var(--font-en); font-weight:800; font-size:clamp(3rem,8.2vw,7.4rem); line-height:.85; letter-spacing:-.01em; color:var(--green-900);`
  - `p`: 日本語ラベル。`font-size:.82rem; font-weight:700; letter-spacing:.2em; color:var(--ink);` **`::before` の緑の短い横線は削除**
  - 480px 以下は縦積み（`flex-direction:column; gap:10px;`）にしてよい

### B. 縦罫線・横罫線
- `.section` に `position:relative` を付け、`::before` で**左の縦罫線**（`width:1px; top:0; bottom:0; left:calc(50% - 620px); background:rgba(18,53,39,.10);`）を引く。1280px 未満では `left:40px` 相当に寄せ、**768px 以下は非表示**
- 各 `.section` の下端に横の細い罫線（`border-bottom:1px solid rgba(18,53,39,.08)`）。ダーク背景の `.contact` には引かない

### C. 非対称の淡い帯
- `.introduce` と `.works` に、装飾用の絶対配置ブロック（`.band` / `::after`）を1枚ずつ敷く（`z-index:0`、コンテンツは `z-index:1`）
  - INTRODUCE＝**右端から画面外まで伸び、左は 28% で止まる**淡い緑帯（`--green-050`）。上下はセクションの上辺・下辺をわざとまたぐ（例: `top:120px; bottom:-90px;`）
  - WORKS＝**左端から伸びて右は 22% 手前で止まる**同色の帯
  - `.service` は今の全面 `--green-050` をやめ、白背景＋**左からはみ出す帯**に変更（帯の上にカードが乗る）
- 帯は必ずコンテンツの背面。文字の可読性を落とさない

### D. ウォーターマーク英字
- INTRODUCE セクションに巨大な極薄英字を1枚敷く（例 `<span class="watermark" aria-hidden="true">VISION</span>`）
  - `font-family:var(--font-en); font-weight:800; font-size:clamp(7rem,17vw,15rem); line-height:1; color:#E8F1EC; letter-spacing:.02em;` 右下寄せ・`pointer-events:none`・親を `overflow:hidden`
  - 768px 以下は非表示

### E. ヒーロー（箱敷きの文字）
- 背景は今の深緑グラデ＋ドットのまま（写真素材は使わない）
- `h1` の各行を `<span>` で包み、**白のベタ塗り箱＋濃緑文字**にする
  - `.hero h1 span { display:inline; box-decoration-break:clone; -webkit-box-decoration-break:clone; padding:.12em .28em; background:var(--white); color:var(--green-900); }`
  - 行間が詰まって箱が重なるので `line-height:1.6` 程度に調整
- サブコピーは**1行＝1つの濃緑の箱**（`background:rgba(12,41,29,.82); color:var(--white); padding:.5em .9em;`）。`<br>` 区切りのままだと箱にできないので、3行それぞれを `<span class="hero__line">` で包み `display:table` 等で行ごとの箱にする（**文言は変更しない**）
- ヒーローの文字は**左寄せ**（今の中央寄せをやめる）。`place-items:center` → `align-items:center; justify-items:start;` 相当に

### F. ヘッダー
- **常に不透明の白**に固定。`is-over-hero` の透明状態は廃止（CSS・JS 両方から取り除く。JS のスクロール監視が不要になるなら削除してよい）。白ロゴは company/footer でのみ使用
- 右上端に**全高のダーク CONTACT ボタン**を追加
  - `<a class="header-cta" href="#contact">`（company.html では `index.html#contact`）。中身＝小さなメールアイコン（インライン SVG・外部読み込み禁止）＋ `CONTACT`
  - `height:100%; padding:0 34px; background:var(--green-900); color:#fff; font-family:var(--font-en); font-weight:700; letter-spacing:.12em; text-decoration:none;` ヘッダーの `padding-right` を 0 にしてピッタリ右端に付ける
  - ハンバーガーはその左隣。768px 以下は CONTACT の文字を隠しアイコンのみ（または非表示）にして崩れないようにする

### G. SERVICE カード
- カードの上辺に**ひし形バッジ**（`.service-card__label` を流用）
  - `width:86px; height:86px; transform:rotate(45deg); background:var(--green-500);` カード上辺に半分めり込む（`position:absolute; top:0; left:50%; translate:-50% -50%;`）
  - 中の文字（制作／戦略／共創）は `rotate(-45deg)` で戻して白・0.85rem・中央
  - カードは `position:relative; padding-top:78px;` 角丸なし・`border:1px solid rgba(18,53,39,.08)`・影は今より浅く。**上辺の緑4pxのバーは削除**
- カードの見出しは**中央寄せ**で「`01.`（アクセント緑・Barlow 800・2.6rem）＋ タイトル（green-900・1.3rem）」を**同じ行に並べる**（今は番号が上、タイトルが下）
- 本文は左寄せのまま `.94rem`

### H. ボタン
- `.button` の角丸をなくし、右端に**長い矢印**を付ける
  - `position:relative; padding-right:64px;` ＋ `::after` で `width:38px; height:1px; background:currentColor;` を右に、さらに矢じり（小さい斜線 or `::before`）
  - ホバーで矢印が数 px 右へ伸びる
- 参考元の「もっと見る」型のリンクボタンとして `.button--line`（塗りなし・枠線のみ・同じ矢印）も定義しておく（今は未使用でよい）

### I. WORKS / お問い合わせ / 会社概要
- WORKS の事例タイトル `.work-item h3` は**左に短い縦のアクセントバー**（`border-left:4px solid var(--green-500); padding-left:18px;`）を付ける
- `.contact` は深緑のまま。中身を**左寄せ**にし、リード文の左側に `CONTACT / お問い合わせ` の見出しは付けない（オーナー指定でラベルなし）ので、ボタンはリード文の下・左寄せに置く
- `company.html` の `.page-hero` 内の見出しも A の横並び型に合わせる。会社概要の定義リストは罫線を細く（`rgba(18,53,39,.10)`）

## やってはいけないこと
- 文言の変更・追加・削除（英語のキャッチコピー等を**新規に足さない**）
- 参考元の紺・青の使用、参考元の画像・イラスト素材の流用
- 外部の画像/フォント以外のリソース読み込み、ビルドツールの導入

## 受け入れ条件
1. `index.html` を 1440px で開くと、セクション見出しが「巨大英字＋右横に小さい日本語」になっている
2. 左の縦罫線がページを通して見え、淡い帯が左右非対称にはみ出している
3. ヒーローの見出しが白箱、サブコピーが3行それぞれ濃緑の箱になっている
4. ヘッダーが常に白で、右上端に全高のダーク CONTACT ボタンが付いている
5. SERVICE の3カードにひし形バッジが上辺へ半分めり込み、「01. 制作代行」が1行に並んでいる
6. ボタンの右端に矢印が出ている
7. 1440 / 1280 / 768 / 390px でレイアウトが破綻せず、横スクロールが出ない
8. ハンバーガー開閉・スムーススクロール・WORKS の3リンク（画像2つ＋チャンネル名）が従来どおり動く
9. コンソールエラー 0・文言が v3 から1文字も変わっていない
