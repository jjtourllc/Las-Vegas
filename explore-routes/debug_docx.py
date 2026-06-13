#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to examine DOCX internal structure - output to file"""

import zipfile
import xml.etree.ElementTree as ET
import os
import sys

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\旅游工作\出团单\拉斯维加斯+大峡谷国家公园+马蹄湾+羚羊彩穴+布莱斯峡谷国家公园+大提顿国家公园+黄石国家公园+盐湖城+大盐湖 6日游.docx"

with zipfile.ZipFile(file_path, 'r') as z:
    with z.open('word/document.xml') as doc_xml:
        tree = ET.parse(doc_xml)
        root = tree.getroot()
        
        NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        
        # Print all paragraphs
        print("=" * 80)
        print("PARAGRAPHS:")
        print("=" * 80)
        for i, para in enumerate(root.findall('.//' + NS + 'p')):
            texts = []
            for run in para.findall('.//' + NS + 't'):
                if run.text:
                    texts.append(run.text)
            if texts:
                txt = ''.join(texts)
                if len(txt) > 100:
                    txt = txt[:100] + '...'
                print(f"[{i}] {txt}")
        
        # Print all tables
        print("\n" + "=" * 80)
        tables_count = len(root.findall('.//' + NS + 'tbl'))
        print(f"TABLES COUNT: {tables_count}")
        print("=" * 80)
        
        for t_idx, table in enumerate(root.findall('.//' + NS + 'tbl')):
            print(f"\n--- TABLE {t_idx} ---")
            rows = table.findall('.//' + NS + 'tr')
            print(f"  Rows: {len(rows)}")
            for r_idx, row in enumerate(rows[:10]):  # Only first 10 rows
                cells = row.findall('.//' + NS + 'tc')
                row_texts = []
                for cell in cells:
                    cell_texts = []
                    for para in cell.findall('.//' + NS + 'p'):
                        for run in para.findall('.//' + NS + 't'):
                            if run.text:
                                cell_texts.append(run.text)
                    row_texts.append(''.join(cell_texts))
                print(f"  Row {r_idx}: {row_texts}")
            if len(rows) > 10:
                print(f"  ... ({len(rows) - 10} more rows)")
