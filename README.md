# ひらがな たんけんたい

5さいくらいの こどもが、音声なしで遊べるひらがな学習アプリです。

## はじめかた

1. Python 3.10 以上を用意します。
2. このフォルダで `pip install -r requirements.txt` を実行します。
3. `streamlit run app.py` を実行します。
4. 表示されたURLを、パソコンまたはiPhoneのブラウザで開きます。

## 問題を増やす

- 「なまえを つくろう」: `data/name_questions.csv`
- 「なかまの ことば」: `data/related_questions.csv`
- 「わけてみよう」: `data/sorting_questions.json`

CSVはExcelでも編集できます。文字の選択肢は `|`（縦線）で区切ります。
JSONは同じ形の問題をコピーし、`id` が重ならないように変更してください。

## 絵文字を画像に変える

`images` フォルダへ、問題データの `image` と同じ名前のPNG画像を置きます。
たとえば `images/dog.png` を置くと、犬の絵文字がその画像に変わります。
画像がない場合は、問題データの `emoji` が自動で表示されます。

## 記録について

問題番号、正解数、間違えた問題、選んだ文字、仕分けた画像は、
ブラウザを開いている間 `st.session_state` に保存されます。
