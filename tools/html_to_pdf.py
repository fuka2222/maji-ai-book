#!/usr/bin/env python3
"""
HTMLファイルをPDFに変換するスクリプト
Chrome/Edgeのヘッドレスモードを使用
"""

import subprocess
import sys
from pathlib import Path


def html_to_pdf(html_path: Path, output_path: Path = None):
    """
    HTMLファイルをPDFに変換
    
    Args:
        html_path: HTMLファイルのパス
        output_path: 出力PDFファイルのパス（省略時は自動生成）
    """
    if not html_path.exists():
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {html_path}")
    
    if output_path is None:
        output_path = html_path.with_suffix('.pdf')
    
    # Chrome/Edgeのパスを確認
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_path = path
            break
    
    if chrome_path is None:
        # システムのデフォルトブラウザを使用
        chrome_path = "google-chrome"  # Linuxの場合
        try:
            result = subprocess.run(
                ["which", "google-chrome"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                chrome_path = result.stdout.strip()
            else:
                raise FileNotFoundError(
                    "Chrome/Edgeが見つかりません。"
                    "ChromeまたはEdgeをインストールしてください。"
                )
        except:
            raise FileNotFoundError(
                "Chrome/Edgeが見つかりません。"
                "ChromeまたはEdgeをインストールしてください。"
            )
    
    # HTMLファイルの絶対パスを取得
    html_absolute = html_path.resolve()
    
    # file:// プロトコルでURLを作成
    html_url = f"file://{html_absolute}"
    
    # PDF生成コマンド
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=" + str(output_path.resolve()),
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        html_url
    ]
    
    print(f"PDFを生成中: {html_path.name} -> {output_path.name}")
    print(f"Chrome/Edge: {chrome_path}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"エラー: {result.stderr}", file=sys.stderr)
            raise RuntimeError(f"PDF生成に失敗しました: {result.stderr}")
        
        if output_path.exists():
            print(f"✓ PDFを生成しました: {output_path}")
            print(f"  サイズ: {output_path.stat().st_size / 1024:.1f} KB")
        else:
            raise RuntimeError("PDFファイルが生成されませんでした")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("PDF生成がタイムアウトしました")
    except Exception as e:
        raise RuntimeError(f"PDF生成中にエラーが発生しました: {e}")


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python html_to_pdf.py <HTMLファイルパス> [出力PDFパス]")
        sys.exit(1)
    
    html_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        html_to_pdf(html_path, output_path)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()



