#!/bin/bash
# 第1章・第2章・第3章のHTMLをPDFに変換する（印刷用レイアウトを維持）
# 使い方: ./make_pdf.sh  または  bash make_pdf.sh

cd "$(dirname "$0")"
OUT_DIR="pdf"
mkdir -p "$OUT_DIR"

# 絶対パス（Chrome headless用）
BASE="file://$(pwd)"

# macOS Chrome
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Chromium
CHROMIUM="/Applications/Chromium.app/Contents/MacOS/Chromium"

if [ -x "$CHROME" ]; then
  BROWSER="$CHROME"
elif [ -x "$CHROMIUM" ]; then
  BROWSER="$CHROMIUM"
else
  echo "Chrome または Chromium が見つかりません。"
  echo "ブラウザで各HTMLを開き、印刷 → PDFとして保存 で出力してください。"
  exit 1
fi

echo "PDFを生成しています..."

("$BROWSER" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT_DIR/第1章_基盤構築.pdf" \
  --print-to-pdf-no-header \
  "$BASE/第1章.html" 2>&1 | grep -v "Abort" > /dev/null) || true
sleep 1
if [ -f "$OUT_DIR/第1章_基盤構築.pdf" ]; then
  echo "  → $OUT_DIR/第1章_基盤構築.pdf"
else
  echo "  ✗ 第1章のPDF生成に失敗しました"
fi

("$BROWSER" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT_DIR/第2章_基本スキル.pdf" \
  --print-to-pdf-no-header \
  "$BASE/第2章.html" 2>&1 | grep -v "Abort" > /dev/null) || true
sleep 1
if [ -f "$OUT_DIR/第2章_基本スキル.pdf" ]; then
  echo "  → $OUT_DIR/第2章_基本スキル.pdf"
else
  echo "  ✗ 第2章のPDF生成に失敗しました"
fi

("$BROWSER" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$OUT_DIR/第3章_構造化.pdf" \
  --print-to-pdf-no-header \
  --virtual-time-budget=10000 \
  --run-all-compositor-stages-before-draw \
  "$BASE/第3章.html" 2>&1 | grep -v "Abort" > /dev/null) || true
sleep 3
if [ -f "$OUT_DIR/第3章_構造化.pdf" ]; then
  echo "  → $OUT_DIR/第3章_構造化.pdf"
else
  echo "  ✗ 第3章のPDF生成に失敗しました（HTMLファイルを確認してください）"
fi

echo "完了: $OUT_DIR/ を確認してください。"
