#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MarkdownファイルをHTMLに変換するスクリプト
"""

import re
import html as html_escape
from pathlib import Path

def parse_table(md_table):
    """MarkdownテーブルをHTMLテーブルに変換"""
    lines = md_table.strip().split('\n')
    if len(lines) < 2:
        return md_table
    
    # ヘッダー行
    header = lines[0].split('|')
    header = [h.strip() for h in header if h.strip()]
    
    # 区切り行をスキップ
    data_lines = lines[2:]
    
    html = '<table>\n<thead>\n<tr>\n'
    for h in header:
        html += f'<th>{h}</th>\n'
    html += '</tr>\n</thead>\n<tbody>\n'
    
    for line in data_lines:
        if not line.strip():
            continue
        cells = line.split('|')
        cells = [c.strip() for c in cells if c.strip()]
        if cells:
            html += '<tr>\n'
            for cell in cells:
                # Markdownの強調を処理
                cell = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cell)
                html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
    
    html += '</tbody>\n</table>'
    return html

def markdown_to_html(md_text, chapter_num):
    """MarkdownテキストをHTMLに変換"""
    
    # 章タイトルとイントロを抽出
    title_match = re.match(r'^# (.+?)\n\n(.+?)\n\n---', md_text, re.DOTALL)
    if title_match:
        chapter_title = title_match.group(1)
        intro = title_match.group(2).strip()
    else:
        # フォールバック
        title_match = re.match(r'^# (.+?)\n\n(.+?)(?=\n##|\n---|$)', md_text, re.DOTALL)
        if title_match:
            chapter_title = title_match.group(1)
            intro = title_match.group(2).strip()
        else:
            chapter_title = f"第{chapter_num}章"
            intro = ""
    
    # HTMLの開始部分
    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chapter_title} - 目標達成を支援するコーチング</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header class="chapter-header">
            <h1>{chapter_title}</h1>
            <p class="chapter-intro">{intro}</p>
        </header>
'''
    
    # セクションごとに分割
    sections = re.split(r'\n---\n', md_text)
    
    for section in sections:
        if not section.strip():
            continue
            
        # 見出しレベル2（##）でセクションを分割
        section_parts = re.split(r'\n(## .+?)\n', section)
        
        current_section = None
        for i, part in enumerate(section_parts):
            if part.startswith('## '):
                # セクション見出し
                section_title = part.replace('## ', '').strip()
                if current_section:
                    html += '</section>\n'
                html += f'        <section class="section">\n'
                html += f'            <h2>{section_title}</h2>\n'
                current_section = True
            elif part.strip():
                # セクションの内容
                content = process_content(part)
                if content.strip():
                    html += content
    
    if current_section:
        html += '        </section>\n'
    
    html += '''    </div>
</body>
</html>'''
    
    return html

def process_content(text):
    """コンテンツ部分を処理"""
    result = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 見出し
        if line.startswith('#### '):
            result.append(f'            <h4>{line[5:].strip()}</h4>\n')
        elif line.startswith('### '):
            result.append(f'            <h3>{line[4:].strip()}</h3>\n')
        elif line.startswith('## '):
            result.append(f'            <h2>{line[3:].strip()}</h2>\n')
        elif line.startswith('# '):
            result.append(f'            <h1>{line[2:].strip()}</h1>\n')
        
        # テーブル
        elif line.strip().startswith('|') and '|' in line:
            table_lines = [line]
            i += 1
            # 区切り行をスキップ
            if i < len(lines) and '|' in lines[i] and '---' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            # データ行を収集
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            i -= 1  # 次のループでi++されるので
            table_md = '\n'.join(table_lines)
            result.append(f'            {parse_table(table_md)}\n')
        
        # コードブロック
        elif line.strip().startswith('```'):
            code_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                code_lines.append(lines[i])
            code_text = '\n'.join(code_lines[1:-1])
            lang = line[3:].strip() if len(line) > 3 else ''
            result.append(f'            <pre><code class="{lang}">{html_escape.escape(code_text)}</code></pre>\n')
        
        # リスト（番号付き）
        elif re.match(r'^\d+\.\s+', line):
            result.append('            <ol>\n')
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                item = re.sub(r'^\d+\.\s+', '', lines[i])
                item = process_inline_markdown(item)
                result.append(f'                <li>{item}</li>\n')
                i += 1
            i -= 1
            result.append('            </ol>\n')
        
        # リスト（箇条書き）
        elif line.strip().startswith('- '):
            result.append('            <ul>\n')
            while i < len(lines) and (lines[i].strip().startswith('- ') or 
                                      (lines[i].strip().startswith('  - ') or lines[i].strip().startswith('    - '))):
                item = lines[i].strip()
                # インデントを考慮
                if item.startswith('    - '):
                    item = item[6:]
                    indent = '                '
                elif item.startswith('  - '):
                    item = item[4:]
                    indent = '                '
                else:
                    item = item[2:]
                    indent = '                '
                item = process_inline_markdown(item)
                result.append(f'{indent}<li>{item}</li>\n')
                i += 1
            i -= 1
            result.append('            </ul>\n')
        
        # 水平線
        elif line.strip() == '---':
            result.append('            <hr>\n')
        
        # 空行
        elif not line.strip():
            pass
        
        # 通常の段落
        else:
            if line.strip():
                processed = process_inline_markdown(line.strip())
                result.append(f'            <p>{processed}</p>\n')
        
        i += 1
    
    return ''.join(result)

def process_inline_markdown(text):
    """インラインMarkdownを処理"""
    # 強調（**text**）
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 強調（*text*）
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # インラインコード
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # ハイライト（**text**を<span class="highlight">に変換）
    text = re.sub(r'<strong>(.+?)</strong>', r'<strong class="highlight">\1</strong>', text)
    return text

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    md_dir = base_dir / '教材草稿'
    html_dir = base_dir / '教材HTML'
    
    for i in range(1, 5):
        md_file = md_dir / f'第{i}章.md'
        if md_file.exists():
            print(f'変換中: {md_file.name}')
            md_content = md_file.read_text(encoding='utf-8')
            html_content = markdown_to_html(md_content, i)
            
            html_file = html_dir / f'第{i}章.html'
            html_file.write_text(html_content, encoding='utf-8')
            print(f'出力: {html_file.name}')
        else:
            print(f'ファイルが見つかりません: {md_file}')

