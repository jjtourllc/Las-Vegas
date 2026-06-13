#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游产品卡片自动化更新脚本 v3
扫描出团单文件夹中的 DOCX 文件，解析产品信息，与 tours.json 对比，发现新产品并添加
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
import shutil
import re
import sys

# 配置路径
OUTUAN_DOCX_DIR = r"D:\旅游工作\出团单"
TOURS_JSON_PATH = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tours.json"
TOUR_FILES_DIR = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tour-files"

NS_DOCUMENT = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_existing_product_codes():
    """读取 tours.json 获取已有的 product_code 列表"""
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        tours = json.load(f)
    return {tour['product_code'] for tour in tours}

def parse_docx_all(file_path):
    """解析 DOCX 文件，返回 (paragraphs, all_tables)"""
    with zipfile.ZipFile(file_path, 'r') as z:
        with z.open('word/document.xml') as doc_xml:
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            
            paragraphs = []
            tables = []
            
            # 提取所有段落（扁平化列表）
            for para in root.findall('.//' + NS_DOCUMENT + 'p'):
                texts = []
                for run in para.findall('.//' + NS_DOCUMENT + 't'):
                    if run.text:
                        texts.append(run.text)
                if texts:
                    paragraphs.append(''.join(texts))
            
            # 提取所有表格
            for table in root.findall('.//' + NS_DOCUMENT + 'tbl'):
                rows = []
                for row in table.findall('.//' + NS_DOCUMENT + 'tr'):
                    cells_texts = []
                    for cell in row.findall('.//' + NS_DOCUMENT + 'tc'):
                        cell_texts = []
                        for para in cell.findall('.//' + NS_DOCUMENT + 'p'):
                            for run in para.findall('.//' + NS_DOCUMENT + 't'):
                                if run.text:
                                    cell_texts.append(run.text)
                        cells_texts.append(''.join(cell_texts))
                    rows.append(cells_texts)
                tables.append(rows)
            
            return paragraphs, tables

def extract_product_info_from_paragraphs(file_name, paragraphs, tables):
    """从扁平化的段落列表中提取产品信息
    
    关键发现：DOCX 文件的表格内容存储在独立的 <w:p> 段落标签内，
    标签和值是分开的行。例如：
      [5] 产品编号
      [6] R0004737
      [9] 出发城市
      [10] 拉斯维加斯 Las Vegas
    """
    info = {
        'product_code': '',
        'tour_code': '',
        'departure_city': '',
        'arrival_city': '',
        'duration': '',
        'price': '',
        'dates': '',
        'highlights': '',
        'route': '',
        'name': ''
    }
    
    # 从文件名提取产品名称
    name = file_name.replace('.docx', '')
    name = re.sub(r'（套餐）\s*\.?$', '', name)
    info['name'] = name
    
    # === 方法1：从扁平化段落中提取 ===
    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()
        
        # 产品编号
        if '产品编号' in para_stripped or 'product_code' in para_stripped.lower():
            if i + 1 < len(paragraphs):
                info['product_code'] = paragraphs[i + 1].strip()
        
        # 团号/线路编号
        elif '团号' in para_stripped or '线路编号' in para_stripped or '出团编号' in para_stripped:
            if i + 1 < len(paragraphs):
                info['tour_code'] = paragraphs[i + 1].strip()
        
        # 出发城市
        elif '出发城市' in para_stripped or '出发地' in para_stripped or 'Departure' in para_stripped:
            if i + 1 < len(paragraphs):
                city = paragraphs[i + 1].strip()
                if city and len(city) < 100 and '产品' not in city:
                    info['departure_city'] = city
        
        # 目的地城市
        elif '目的地城市' in para_stripped or '目的地' in para_stripped:
            if i + 1 < len(paragraphs):
                city = paragraphs[i + 1].strip()
                if city and len(city) < 100 and '产品' not in city:
                    info['arrival_city'] = city
        
        # 返回城市（如果 arrival_city 未设置）
        elif '返回城市' in para_stripped and not info['arrival_city']:
            if i + 1 < len(paragraphs):
                city = paragraphs[i + 1].strip()
                if city and len(city) < 100 and '产品' not in city:
                    info['arrival_city'] = city
        
        # 行程天数
        elif '行程天数' in para_stripped or '行程时间' in para_stripped or '天数' in para_stripped:
            if i + 1 < len(paragraphs):
                dur = paragraphs[i + 1].strip()
                if dur:
                    info['duration'] = dur
        
        # 产品价格
        elif '产品价格' in para_stripped or '价格' in para_stripped:
            if i + 1 < len(paragraphs):
                price_line = paragraphs[i + 1].strip()
                if price_line:
                    info['price'] = price_line
        
        # 出发班期
        elif '出发班期' in para_stripped or '班期' in para_stripped:
            if i + 1 < len(paragraphs):
                info['dates'] = paragraphs[i + 1].strip()
        
        # 途经地点
        elif '途经地点' in para_stripped or '途经' in para_stripped or '途径' in para_stripped:
            if i + 1 < len(paragraphs):
                info['route'] = paragraphs[i + 1].strip()
        
        # 行程特色标题
        elif '行程特色' in para_stripped or '行程亮点' in para_stripped:
            pass  # 下面单独处理
    
    # === 方法2：从表格中提取补充信息 ===
    # 第一个表格通常是产品信息表（即使内容在段落中）
    if len(tables) > 0:
        # 遍历表格所有单元格，尝试提取价格
        for row in tables[0]:
            for cell in row:
                # 提取价格模式
                prices = re.findall(r'[\d,]+\s*/\s*人', cell)
                if prices:
                    for p in prices:
                        if not info['price']:
                            info['price'] = p.strip()
    
    # === 方法3：从正文段落中提取 highlights ===
    highlights_lines = []
    in_highlights = False
    
    for para in paragraphs:
        para_stripped = para.strip()
        
        # 检测行程特色标题
        if any(marker in para_stripped for marker in ['行程特色', '行程亮点', '特色说明']):
            in_highlights = True
            continue
        
        # 在 highlights 区域内收集内容
        if in_highlights and para_stripped:
            # 遇到下一个大标题停止
            if any(para_stripped.startswith(m) for m in ['产品', '出发', '行程天数', '价格', '班期']):
                in_highlights = False
                continue
            # 排除标签行
            if any(skip in para_stripped for skip in ['产品编号', '团号', '出发城市', '目的地', '返回城市', '天数', '价格']):
                continue
            # 收集特色内容
            if len(para_stripped) > 5 and len(para_stripped) < 500:
                highlights_lines.append(para_stripped)
    
    if highlights_lines:
        info['highlights'] = ' | '.join(highlights_lines[:5])
    
    return info

def create_product_card(info):
    """创建标准化的产品卡片格式"""
    card = {
        'product_code': info['product_code'],
        'name': info['name'],
        'tour_code': info['tour_code'],
        'route': info.get('route', ''),
        'departure_city': info.get('departure_city', ''),
        'duration': info.get('duration', ''),
        'price': info.get('price', ''),
        'highlights': info.get('highlights', ''),
        'dates': info.get('dates', '')
    }
    return card

def add_to_tours_json(card):
    """将新产品添加到 tours.json"""
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        tours = json.load(f)
    
    tours.append(card)
    
    # 按 product_code 排序
    tours.sort(key=lambda x: x['product_code'])
    
    with open(TOURS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(tours, f, ensure_ascii=False, indent=2)
    
    return tours

def copy_docx_to_tour_files(file_path, docx_file):
    """复制 DOCX 文件到 tour-files 目录"""
    os.makedirs(TOUR_FILES_DIR, exist_ok=True)
    dest_path = os.path.join(TOUR_FILES_DIR, docx_file)
    if not os.path.exists(dest_path):
        shutil.copy2(file_path, dest_path)
        return True
    return False

def main():
    print("=" * 60)
    print("Travel Product Card Auto Update Script v3")
    print("=" * 60)
    
    # 1. 获取已有 product_codes
    existing_codes = get_existing_product_codes()
    print(f"\nExisting products count: {len(existing_codes)}")
    print(f"Existing product_codes: {sorted(existing_codes)}")
    
    # 2. 扫描 DOCX 文件
    docx_files = [f for f in os.listdir(OUTUAN_DOCX_DIR) if f.endswith('.docx')]
    docx_files.sort()
    print(f"\nDOCX files in outuan dir: {len(docx_files)}")
    
    # 3. 逐个解析
    new_products = []
    skipped_products = []
    
    for docx_file in docx_files:
        file_path = os.path.join(OUTUAN_DOCX_DIR, docx_file)
        print(f"\n{'=' * 60}")
        print(f"Parsing: {docx_file}")
        
        paragraphs, tables = parse_docx_all(file_path)
        info = extract_product_info_from_paragraphs(docx_file, paragraphs, tables)
        
        pc_display = info['product_code'] or '(NOT FOUND)'
        tc_display = info['tour_code'] or '(NOT FOUND)'
        print(f"  product_code: {pc_display}")
        print(f"  tour_code: {tc_display}")
        print(f"  departure_city: {info['departure_city']}")
        print(f"  arrival_city: {info['arrival_city']}")
        print(f"  duration: {info['duration']}")
        print(f"  price: {info['price'][:80] if info['price'] else ''}")
        print(f"  route: {info['route'][:80] if info['route'] else ''}")
        highlights_short = info['highlights'][:80] + '...' if len(info['highlights']) > 80 else info['highlights']
        print(f"  highlights: {highlights_short}")
        
        # 检查是否重复
        is_duplicate = False
        reason = ""
        
        # 检查 product_code 是否已有
        if info['product_code'] in existing_codes:
            is_duplicate = True
            reason = f"Product {info['product_code']} already in tours.json"
        
        # 检查文件是否已经在 tour-files 目录中
        dest_file = os.path.join(TOUR_FILES_DIR, docx_file)
        if os.path.exists(dest_file):
            is_duplicate = True
            reason = f"File already in tour-files directory"
        
        # 如果 product_code 为空
        if not info['product_code'] and not is_duplicate:
            print(f"  WARNING: No product_code found, skipping")
            skipped_products.append({'file': docx_file, 'reason': 'No product_code found'})
            continue
        
        if is_duplicate:
            skipped_products.append({'file': docx_file, 'reason': reason})
            print(f"  SKIP: {reason}")
        else:
            # 创建产品卡片
            card = create_product_card(info)
            new_products.append(card)
            
            # 添加到 tours.json
            tours = add_to_tours_json(card)
            print(f"  ADDED to tours.json!")
            
            # 复制文件到 tour-files
            copied = copy_docx_to_tour_files(file_path, docx_file)
            if copied:
                print(f"  Copied to tour-files/")
            else:
                print(f"  File already in tour-files/")
            
            print(f"  NEW: {info['name'][:50]}")
    
    # 4. 输出最终结果
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")
    print(f"DOCX files parsed: {len(docx_files)}")
    print(f"New products added: {len(new_products)}")
    print(f"Skipped products: {len(skipped_products)}")
    
    if new_products:
        print("\n[NEW PRODUCTS ADDED]")
        for p in new_products:
            print(f"  [{p['product_code']}] {p['name'][:50]}")
            print(f"    Route: {p['departure_city']} -> Duration: {p['duration']}")
            if p.get('route'):
                print(f"    Path: {p['route'][:100]}")
    
    if skipped_products:
        print("\n[SKIPPED PRODUCTS]")
        for s in skipped_products:
            print(f"  - {s['file']}")
            print(f"    Reason: {s['reason']}")
    
    print(f"\n{'=' * 60}")
    print("Update completed!")
    print(f"{'=' * 60}")
    
    return new_products, skipped_products

if __name__ == '__main__':
    main()
