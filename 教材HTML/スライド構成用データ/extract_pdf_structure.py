#!/usr/bin/env python3
"""
PDFの構造を抽出してYAMLプロンプト作成用の情報を取得
"""

import sys
import os

def extract_pdf_info(pdf_path):
    """PDFファイルの基本情報を抽出"""
    try:
        # PyPDF2を試す
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                print(f"総ページ数: {num_pages}")
                print("\n=== メタデータ ===")
                metadata = pdf_reader.metadata
                if metadata:
                    for key, value in metadata.items():
                        print(f"{key}: {value}")
                
                print("\n=== 最初の数ページのテキスト（構造把握用） ===")
                for i, page in enumerate(pdf_reader.pages[:5], 1):
                    print(f"\n--- ページ {i} ---")
                    text = page.extract_text()
                    # 最初の500文字だけ表示
                    print(text[:500])
                
                return pdf_reader
        except ImportError:
            pass
        
        # pdfplumberを試す
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"総ページ数: {num_pages}")
                
                print("\n=== メタデータ ===")
                metadata = pdf.metadata
                if metadata:
                    for key, value in metadata.items():
                        print(f"{key}: {value}")
                
                print("\n=== 最初の数ページのテキスト（構造把握用） ===")
                for i, page in enumerate(pdf.pages[:5], 1):
                    print(f"\n--- ページ {i} ---")
                    text = page.extract_text()
                    # 最初の500文字だけ表示
                    if text:
                        print(text[:500])
                
                return pdf
        except ImportError:
            pass
        
        print("エラー: PDF処理ライブラリが見つかりません")
        print("以下のいずれかをインストールしてください:")
        print("  pip install PyPDF2")
        print("  pip install pdfplumber")
        return None
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    pdf_path = "ダイエットサポート資料のコピー　（営業資料作成元として）++.pdf"
    if not os.path.exists(pdf_path):
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        sys.exit(1)
    
    extract_pdf_info(pdf_path)

