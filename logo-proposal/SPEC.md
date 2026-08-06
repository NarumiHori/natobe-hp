# ナトビー ロゴ案 生成スペック（PMが設計・実装だけ委譲）

## 作るもの
`build.py` 1本（Python）。実行は `/tmp/nblogo/.venv/bin/python build.py`（fontTools 4.63 入り）。
このディレクトリ（`~/claude-projects/natobee-hp/logo-proposal/`）で動き、`out/` に成果物を書く。

出力：
1. ロゴ単体SVG（文字はアウトライン化＝フォント非依存で開ける）
   - `out/logo-a-lockup.svg` … Aパターン アイコン＋`natobee` 横並び
   - `out/logo-a-lockup-accent.svg` … 同上・`ee` だけブルー
   - `out/logo-a-stack.svg` … A 縦積み（アイコン上・文字下）
   - `out/logo-a-icon.svg` … A アイコンのみ（正方形 120×120）
   - `out/logo-b-lockup.svg` … Bパターン アイコン＋`Natobee` 横並び
   - `out/logo-b-lockup-caps.svg` … 同上・`NATOBEE`
   - `out/logo-b-stack.svg` … B 縦積み
   - `out/logo-b-icon.svg` … B アイコンのみ（120×120 のviewBox内に六角形）
   - 各ロックアップの白抜き版 `-white.svg`（濃紺背景に置く用＝文字を #FFFFFF、アイコンのグラデはそのまま、必要なら明るめ版）
2. 一覧HTML `out/sheet.html`（下の「比較シート」）

## 共通の考え方（変更しないこと）
- YouTubeアイコンから受け継ぐのは「器＋中の再生マーク」というシルエットだけ。
- 外し方は3つ＝①色を赤→青のグラデーション ②器の比率を横長→正方形／六角形 ③Bは六角形＝ハニカム（社名の bee）で完全に別物にする。
- 色はHP（natobe.pages.dev）の海の青に合わせる：`#0B5E73` `#16A9C7` `#67D9DF` が既存ブランド色。

## Aパターン（かわいい系）
### アイコン `icon_a`（viewBox `0 0 120 120`）
- 器：`<rect x="4" y="4" width="112" height="112" rx="32" ry="32">`（角丸の大きいアプリアイコン型）
- グラデ：`linearGradient` id一意, `x1=0 y1=0 x2=1 y2=1`（objectBoundingBox）
  - stop 0% `#63E0E6` / 52% `#24A6DA` / 100% `#1667C4`
- 再生マーク：白 `#FFFFFF`。頂点 `(47,34) (47,86) (89,60)` の三角を**角丸半径9**で丸めたパス（3つの角すべて丸める）。
  角丸三角は「各頂点で隣接する2辺方向へ r 分だけ内側に入った点を求め、その2点を頂点を制御点にした2次ベジェで結ぶ」方式で生成する（`Q` を使う）。ハードコードした数値の羅列ではなく、頂点リストと半径から計算する関数 `rounded_polygon(points, r)` を書き、Bでも使い回すこと。
### ロゴタイプ
- 文字：`natobee`（全部小文字）
- フォント：`fonts/Quicksand-Bold.ttf`
- 字間：+2.0%（em比 0.02 を各文字の advance に加算）
- 色：`#123A55`
- accent版：`natob` を `#123A55`、`ee` をグラデ（アイコンと同じ3色・横方向）
### ロックアップ
- 横並び：アイコン高さ = 文字の cap height の約 1.55 倍。アイコンと文字の間は アイコン幅の 0.30 倍。ベースラインではなく**光学的に上下センター**（アイコンの中心と、文字の x-height 帯の中心を合わせる）。
- 縦積み：アイコン中央上、下に文字。間隔はアイコン幅の 0.22 倍。

## Bパターン（かっこいい系）
### アイコン `icon_b`（viewBox `0 0 120 120`）
- 器：**フラットトップ六角形**。頂点 `(32,9) (88,9) (116,60) (88,111) (32,111) (4,60)`、**角丸半径12**（同じ `rounded_polygon` を使う）
- グラデ：stop 0% `#5FD8EC` / 50% `#1595C4` / 100% `#0B5E73`（`x1=0 y1=0 x2=1 y2=1`）
- 内側のセル線：同じ六角形を中心基準で 0.80 倍に縮小したものを `fill=none stroke=#FFFFFF stroke-width=2.4 opacity=0.28`
- 再生マーク：白、頂点 `(48,37) (48,83) (86,60)`、**角丸半径3**（シャープ）
### ロゴタイプ
- `Natobee`（Nだけ大文字）＝ `fonts/Outfit-SemiBold.ttf`、字間 +1.5%、色 `#0B2E3D`
- `NATOBEE`（全部大文字）＝ `fonts/Outfit-Medium.ttf`、字間 +20%、色 `#0B2E3D`
### ロックアップ
- Aと同じ規則。ただし六角形は高さいっぱいなので、アイコン高さ = cap height の 1.7 倍。

## 文字のアウトライン化
- fontTools（`TTFont` + `SVGPathPen` / `glyphSet`）でグリフを取り出し、`unitsPerEm` で正規化してから拡大・移動して1本の `<path>` にまとめる。
- 字間はカーニングなしでよい（`hmtx` の advance ＋ letter-spacing）。
- 出力SVGに `<text>` を残さないこと（フォントが無い環境でも同じ見た目になるのが受け入れ条件）。

## 比較シート `out/sheet.html`
- 幅 1400px 固定、白背景、`fonts/NotoSansJP-Medium.ttf` を `@font-face` で読み日本語ラベルを表示。
- 構成（上から）
  1. 見出し「株式会社ナトビー ロゴ案」＋小さく「YouTubeらしさは残しつつ、色と形で別物に」
  2. 「Aパターン｜かわいい系」…アイコン大（150px）、横並びロックアップ、`ee`アクセント版、縦積み版
  3. 濃紺帯（`#0B2E3D`）にAの白抜きロックアップ
  4. 「Bパターン｜かっこいい系」…アイコン大（150px）、`Natobee` 横並び、`NATOBEE` 横並び、縦積み版
  5. 濃紺帯にBの白抜きロックアップ
  6. 「小さくした時の見え方」…A・Bのアイコンを 64px / 32px / 16px で並べる
  7. 「使用カラー」…A・Bそれぞれのグラデ帯と HEX 表記
- SVGは `<img src="...">` ではなくインラインで埋め込むか、同ディレクトリ相対の `<img>` でよい（`file://` で開いて崩れないこと）。
- ラベルは日本語、専門用語を使わない（「角丸」「字間」等の内部用語をシートに出さない）。

## 受け入れ条件
1. `/tmp/nblogo/.venv/bin/python build.py` がエラーなしで完走し、上記SVGと `out/sheet.html` が生成される。
2. 各SVGに `<text>` 要素が1つも無い（`grep -c '<text' out/*.svg` が全部0）。
3. `google-chrome --headless` で `out/sheet.html` を撮っても文字化け・重なりが無い。
4. アイコンAとBが同じ `rounded_polygon` 関数を使っている（コード重複なし）。
5. 色は上記のHEXから変えない。
