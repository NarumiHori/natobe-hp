# ナトビー ロゴ v3（最終案・カラー2案）生成スペック

前提＝オーナーがBパターン（六角形）と「読みやすい表記」（Nだけ大文字）を選び、
①綴りは e が1個 `Natobe` ②再生マークのバランスを整える ③SNSアイコンの見え方も調整
④最後に**使用カラーのA案・B案**を見て決める、という段階。

実装は `build_v3.py`（新規）。`build.py` と `build_v2.py` から `rounded_polygon` / `gradient` / `fmt` /
フォントのアウトライン化まわり（`Wordmark` 生成関数）を **import して再利用**する（コピペ・再実装は禁止）。
実行＝`/tmp/nblogo/.venv/bin/python build_v3.py`。出力先＝`out/v3/`。

## 0. ファイル先頭に置く調整用の定数（PMが手で触る）
```python
FINAL_TRI_DX = -3.75      # 再生マークの左右位置（マイナスで左へ）
FINAL_TRI_SCALE = 1.06    # 再生マークの大きさ
ICON_TO_CAP = 1.62        # アイコンの高さ ÷ 文字のcap height
ICON_GAP = 0.24           # アイコンと文字の間隔（アイコン幅に対する比）
```

## 1. カラー2案
- **A案「海の青」**（HPと同じ色）：グラデ `0% #5FD8EC` / `50% #1595C4` / `100% #0B5E73`、文字色 `#0B2E3D`
- **B案「藍の青」**（引き締めた濃い青）：グラデ `0% #4FC8F5` / `50% #1F63D6` / `100% #122E6B`、文字色 `#12224F`

## 2. 図形
- 六角形＝`build_v2` の `B_HEXAGON`（`(32,9) (88,9) (116,60) (88,111) (32,111) (4,60)`）、角丸12。
- 再生マーク＝`(45,34) (45,86) (90,60)`、角丸3 を、**重心基準で `FINAL_TRI_SCALE` 倍したうえで x に `FINAL_TRI_DX` 平行移動**（`build_v2.icon_v2` と同じ扱い）。
- ロゴタイプ＝`Natobe`（Nだけ大文字・**e は1個**）、`fonts/Outfit-SemiBold.ttf`、字間 +1.5%、アウトライン化（`<text>` を残さない）。

## 3. ロックアップの組み方（ここが今回の修正点）
- 横並び：アイコン高さ = 文字の **cap height × `ICON_TO_CAP`**。
- **上下の合わせは cap height 帯の中心**（＝`N` の上端と baseline の中間）にアイコンの中心を合わせる。
  ※旧版は x-height 帯の中心に合わせていたためアイコンが下に沈んで見えた。ここを直す。
- アイコンと文字の間隔 = アイコン幅 × `ICON_GAP`。
- 縦積み：アイコン中央上・文字下、間隔はアイコン幅の 0.22 倍、左右中央そろえ。

## 4. 出力するSVG（A案・B案それぞれ）
`out/v3/` に、`{a|b}` を色案として：
1. `natobe-{a|b}-lockup.svg` … アイコン＋`Natobe` 横並び
2. `natobe-{a|b}-lockup-white.svg` … 濃い背景用（文字を `#FFFFFF`・アイコンのグラデはそのまま）
3. `natobe-{a|b}-stack.svg` … 縦積み
4. `natobe-{a|b}-icon.svg` … アイコンのみ（viewBox `0 0 120 120`）
5. `natobe-{a|b}-avatar-light.svg` … SNS用（**512×512**・白 `#FFFFFF` の正方形背景に六角形を中央配置。六角形の高さ＝キャンバスの78%）
6. `natobe-{a|b}-avatar-dark.svg` … SNS用（同じ寸法・背景を `#0B2E3D`、六角形の高さ＝78%）
※ avatar は円形に切り抜かれても欠けないこと（六角形が中央の直径78%の円に収まる）。

## 5. 比較シート `out/v3/sheet.html`（幅1080px・白背景・日本語ラベルは `fonts/NotoSansJP-Medium.ttf` を @font-face）
上から順に：
1. 見出し「株式会社ナトビー ロゴ｜最終案」＋小さく「六角形＋Natobe で確定。色をA案・B案から選んでください」
2. 「直したところ」…横2列のカード。左＝「前」、右＝「後」。
   - 1段目＝綴り：前 `Natobee` / 後 `Natobe`（どちらも A案の色のロックアップで、`build.py` の旧 `Natobee` ロックアップは使わず、この `build_v3.py` 内で綴り違いを生成して比べる）
   - 2段目＝アイコン：前＝`build_v2.icon_v2()` の既定（無調整）/ 後＝`FINAL_TRI_DX`・`FINAL_TRI_SCALE` 適用版。どちらも 200px で並べる
3. 「カラーA案｜海の青」…アイコン200px・横並びロックアップ・縦積み、その下に濃紺帯（`#0B2E3D`）で白抜きロックアップ
4. 「カラーB案｜藍の青」…同じ構成（濃紺帯は `#0B1B3D`）
5. 「SNSのアイコンにした時」…A案・B案それぞれ、白背景版と濃紺版を **円形にくり抜いて** 128px / 64px で表示（`border-radius:50%`・`overflow:hidden`）
6. 「小さくした時の見え方」…A案・B案のアイコンを 48px / 32px / 16px
7. 「使用カラー」…A案・B案それぞれグラデ帯とHEX3つを表示
- 専門用語（角丸・字間・cap height 等）はシートに出さない。ラベルは日常語。

## 6. 受け入れ条件
1. `/tmp/nblogo/.venv/bin/python build_v3.py` がエラーなく完走し、上記12本のSVGと `sheet.html` ができる。
2. `grep -c '<text' out/v3/*.svg` が全部 0。
3. `rounded_polygon` とフォントのアウトライン化を再実装していない（import で再利用）。
4. 綴りが `Natobe`（e が1個）であること。
5. `google-chrome --headless --window-size=1080,<高さ> --screenshot` で撮って、文字化け・重なり・はみ出しが無い。
