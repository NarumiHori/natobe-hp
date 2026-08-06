# ナトビー ロゴ v2（Bパターン確定後の修正）生成スペック

オーナーのフィードバック（録画より）
1. **綴りは e が1個**＝`Natobe`（今の案は `Natobee` で誤り）。
2. **Bパターン（六角形）＋「読みやすい表記」（Nだけ大文字）で確定**。
3. **アイコンの中の再生マークのバランスが悪い**＝「左下にずれて見える／右上がスカスカ」。ここを整える。
4. **SNSアイコンにした時の見え方も調整**してほしい。
5. 最終的に**使用カラーのA案・B案**を見て決めたい。

このファイルは 3（バランス）の**候補出し**の指示。実装は `build_v2.py`（新規・`build.py` は触らない）。

## 作るもの
`~/claude-projects/natobee-hp/logo-proposal/build_v2.py`（Python・実行は `/tmp/nblogo/.venv/bin/python build_v2.py`）。
`build.py` から `rounded_polygon` / `gradient` / `fmt` / `Wordmark` 系のフォント→アウトライン化ユーティリティを **import して再利用**する（コピペ禁止・`build.py` は import しても副作用が出ないよう、必要なら `build.py` 側は `if __name__ == "__main__":` の中だけを実行する形に留める）。
出力先は `out/v2/`。

## 1. アイコン候補（今回の主目的）
六角形（`B_HEXAGON`＝`(32,9) (88,9) (116,60) (88,111) (32,111) (4,60)`・角丸12）と白い再生マーク（`(45,34) (45,86) (90,60)`・角丸3）の組み合わせを、**パラメータ化した関数** `icon_v2(gradient_id, *, tri_scale=1.0, tri_dx=0.0, tri_dy=0.0, hex_points=B_HEXAGON, hex_r=12, tri_r=3)` で作る。
`tri_scale` は三角形の**重心を基準にした拡大縮小**、`tri_dx/tri_dy` は平行移動。

次の6候補を SVG で出す（`out/v2/icon-v0.svg` 〜 `icon-v5.svg`、viewBox `0 0 120 120`）。

1. `v0` 現行のまま（基準）
2. `v1` `tri_scale=1.12`
3. `v2` `tri_dx=-7.5`（三角の外接箱の中心を六角形の中心に合わせる）
4. `v3` `tri_dx=-3.75, tri_scale=1.06`
5. `v4` 六角形を**ポインティトップ**（上下が尖り・左右がフラットな向き）に変えたもの＝頂点 `(60,4) (111,32) (111,88) (60,116) (9,88) (9,32)`、角丸12、三角は現行のまま
6. `v5` 六角形の角丸を `hex_r=20` に大きくし、`tri_scale=1.08`

## 2. 候補比較シート
`out/v2/variants.html`（幅1080px・白背景）。
各候補を1行にして、左から **220px / 96px / 48px** の3サイズを並べ、行の左端に `v0`〜`v5` のラベル。96px の隣に**円形にくり抜いた版**（`border-radius:50%` の枠に収めた見え方＝SNSアイコン想定）も並べる。
各行の下に薄い区切り線。日本語ラベル不要（v番号だけでよい）。

## 受け入れ条件
1. `/tmp/nblogo/.venv/bin/python build_v2.py` がエラーなく完走し、`out/v2/icon-v0.svg`〜`icon-v5.svg` と `out/v2/variants.html` ができる。
2. 各SVGに `<text>` が無い。
3. `rounded_polygon` を再実装していない（`build.py` から import している）。
4. `variants.html` を `google-chrome --headless --screenshot` で撮って、6行×各サイズが重なりなく並ぶ。
