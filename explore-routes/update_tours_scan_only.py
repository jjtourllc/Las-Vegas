#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游产品卡片自动化更新脚本 v5 - Final
综合 v3 和 v4 的优点：
- 用扁平化段落提取 product_code（v3 的方法最有效）
- 用表格+段落配对提取其他字段（v4 的方法更精确）
- 不修改 tours.json，只输出扫描报告
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
import re

OUTUAN_DOCX_DIR = r"D:\旅游工作\出团单"
TOURS_JSON_PATH = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tours.json"
TOUR_FILES_DIR = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tour-files"

NS_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_existing_product_codes():
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        tours = json.load(f)
    return {tour['product_code'] for tour in tours}

def parse_docx(file_path):
    with zipfile.ZipFile(file_path, 'r') as z:
        with z.open('word/document.xml') as doc_xml:
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            
            # 提取所有段落
            paragraphs = []
            for para in root.findall('.//' + NS_W + 'p'):
                texts = []
                for run in para.findall('.//' + NS_W + 't'):
                    if run.text:
                        texts.append(run.text)
                if texts:
                    paragraphs.append(''.join(texts))
            
            # 提取所有表格
            tables = []
            for table in root.findall('.//' + NS_W + 'tbl'):
                rows = []
                for row in table.findall('.//' + NS_W + 'tr'):
                    cells = []
                    for cell in row.findall('.//' + NS_W + 'tc'):
                        cell_texts = []
                        for p in cell.findall('.//' + NS_W + 'p'):
                            for run in p.findall('.//' + NS_W + 't'):
                                if run.text:
                                    cell_texts.append(run.text)
                        cells.append(''.join(cell_texts))
                    rows.append(cells)
                tables.append(rows)
            
            return paragraphs, tables

def extract_product_code_from_paragraphs(paragraphs):
    """用 v3 的方法：在扁平化段落中查找 product_code
    
    匹配模式：在"产品编号"标签的行中找 product_code 值
    如段落中同时包含标签和值（"产品编号: R0004737"），直接提取
    否则找"产品编号"后一行的值
    """
    for i, para in enumerate(paragraphs):
        # 方法1：标签和值在同一行
        m = re.search(r'产品编号\s*[：:]\s*(R\d+)', para)
        if m:
            return m.group(1)
        
        # 方法2：标签和值在不同行 - 标签行匹配
        if '产品编号' in para and not para.startswith('R'):
            # 检查下一行是否是 product_code 格式
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if re.match(r'R\d+', next_para):
                    return next_para
    
    return ''

def extract_info_from_paragraphs(paragraphs):
    """从扁平化段落中提取其他字段"""
    info = {}
    
    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()
        
        # 团号/线路编号
        m = re.search(r'(?:团号|线路编号|出团编号)\s*[：:]\s*([A-Za-z0-9\-]+)', para_stripped)
        if m:
            info['tour_code'] = m.group(1)
            continue
        
        # 如果当前行是"团号"标签，从下一行取值
        if para_stripped in ['团号', '线路编号', '出团编号', '团期编号'] and i + 1 < len(paragraphs):
            val = paragraphs[i + 1].strip()
            if val and len(val) < 20 and not val.startswith('$') and '说明' not in val and '产品' not in val:
                info.setdefault('tour_code', val)
        
        # 出发城市
        elif '出发城市' in para_stripped and '产品' not in para_stripped:
            m = re.search(r'出发城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000]+)', para_stripped)
            if m:
                info['departure_city'] = m.group(1).strip()
            elif i + 1 < len(paragraphs):
                val = paragraphs[i + 1].strip()
                if val and len(val) < 100 and '产品' not in val and '费用' not in val and '服务费' not in val:
                    info.setdefault('departure_city', val)
        
        # 目的地城市
        elif '目的地城市' in para_stripped:
            m = re.search(r'目的地城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000]+)', para_stripped)
            if m:
                info['arrival_city'] = m.group(1).strip()
            elif i + 1 < len(paragraphs):
                val = paragraphs[i + 1].strip()
                if val and len(val) < 100 and '产品' not in val:
                    info.setdefault('arrival_city', val)
        
        # 返回城市
        elif '返回城市' in para_stripped and 'arrival_city' not in info:
            m = re.search(r'返回城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000]+)', para_stripped)
            if m:
                info['arrival_city'] = m.group(1).strip()
        
        # 行程天数
        elif '行程天数' in para_stripped or '行程时间' in para_stripped:
            m = re.search(r'(?:行程天数|行程时间)\s*[：:]\s*(\d+\s*天\s*\d*\s*晚?)', para_stripped)
            if m:
                info['duration'] = m.group(1).strip()
            elif i + 1 < len(paragraphs):
                val = paragraphs[i + 1].strip()
                if val and '天' in val and '说明' not in val:
                    info.setdefault('duration', val)
        
        # 产品价格
        elif '产品价格' in para_stripped:
            prices = re.findall(r'[\$\d,]+\s*/\s*人', para_stripped)
            if prices:
                info['price'] = ', '.join(prices)
            elif i + 1 < len(paragraphs):
                val = paragraphs[i + 1].strip()
                if val and ('$' in val and '/人' in val):
                    info.setdefault('price', val)
        
        # 途经地点
        elif '途经地点' in para_stripped or '途经' in para_stripped:
            m = re.search(r'途经(?:地点)?\s*[：:]\s*(.+)', para_stripped)
            if m:
                info['route'] = m.group(1).strip()
            elif i + 1 < len(paragraphs):
                val = paragraphs[i + 1].strip()
                if val and len(val) < 500 and any(loc in val for loc in ['公园', 'National', 'Park', 'Canyon', 'Bay']):
                    info.setdefault('route', val)
    
    return info

def extract_highlights(paragraphs):
    """从段落提取行程特色"""
    highlights = []
    in_highlights = False
    
    for para in paragraphs:
        ps = para.strip()
        
        if '行程特色' in ps or '行程亮点' in ps:
            in_highlights = True
            if '：' in ps:
                content = ps.split('：', 1)[1].strip()
                if content and len(content) < 200:
                    highlights.append(content)
            continue
        
        if in_highlights and ps:
            if any(ps.startswith(m) for m in ['产品', '出发', '行程天数', '价格', '班期', '费用', '套餐', '预订']):
                in_highlights = False
                continue
            if any(skip in ps for skip in ['产品编号', '团号', '出发城市', '目的地', '返回城市', '天数', '价格', '途经', '实际出行过程', '导游或司机有权', '尊享旅行有权', '服务费', '燃油附加费', '预订', '接机']):
                continue
            if 10 < len(ps) < 500:
                highlights.append(ps)
    
    return ' | '.join(highlights[:5]) if highlights else ''

def extract_dates(tables):
    """从表格提取 dates"""
    dates_parts = []
    for table in tables:
        for row in table:
            for cell in row:
                if re.search(r'\d{2}/\d{2}/\d{4}', cell):
                    dates_parts.append(cell)
                    break
    
    if dates_parts:
        return '\n'.join(dates_parts[:20])
    return ''

def main():
    print("=" * 70)
    print("Travel Product Card Auto-Update - Scan Report (v5)")
    print("=" * 70)
    
    existing_codes = get_existing_product_codes()
    print(f"\nExisting products in tours.json: {len(existing_codes)}")
    print(f"Codes: {sorted(existing_codes)}")
    
    docx_files = sorted([f for f in os.listdir(OUTUAN_DOCX_DIR) if f.endswith('.docx')])
    print(f"\nDOCX files to scan: {len(docx_files)}")
    
    new_products = []
    skipped = []
    
    for docx_file in docx_files:
        file_path = os.path.join(OUTUAN_DOCX_DIR, docx_file)
        paragraphs, tables = parse_docx(file_path)
        
        # 提取信息
        product_code = extract_product_code_from_paragraphs(paragraphs)
        other_info = extract_info_from_paragraphs(paragraphs)
        highlights = extract_highlights(paragraphs)
        dates = extract_dates(tables)
        
        # 合并
        info = {'product_code': product_code}
        info.update(other_info)
        if highlights:
            info['highlights'] = highlights
        if dates:
            info['dates'] = dates
        
        # 从文件名获取 name
        name = docx_file.replace('.docx', '')
        name = re.sub(r'（套餐）\s*\.?$', '', name)
        
        # 显示结果
        print(f"\n{'=' * 70}")
        print(f"File: {docx_file[:60]}")
        print(f"  product_code: {product_code or '(NOT FOUND)'}")
        print(f"  tour_code: {info.get('tour_code', '(NONE)')}")
        print(f"  departure_city: {info.get('departure_city', '(NONE)')}")
        print(f"  arrival_city: {info.get('arrival_city', '(NONE)')}")
        print(f"  duration: {info.get('duration', '(NONE)')}")
        print(f"  price: {info.get('price', '(NONE)')[:60] if info.get('price') else '(NONE)'}")
        print(f"  route: {info.get('route', '(NONE)')[:60] if info.get('route') else '(NONE)'}")
        print(f"  highlights: {info.get('highlights', '(NONE)')[:60] if info.get('highlights') else '(NONE)'}")
        print(f"  dates: {'(FOUND)' if info.get('dates') else '(NONE)'}")
        
        # 判断是否重复
        is_dup = False
        reason = ""
        
        if product_code in existing_codes:
            is_dup = True
            reason = f"Product {product_code} already in tours.json"
        
        if os.path.exists(os.path.join(TOUR_FILES_DIR, docx_file)):
            is_dup = True
            reason = "File already in tour-files"
        
        if not product_code and not is_dup:
            skipped.append({'file': docx_file, 'reason': 'No product_code found'})
            print(f"  SKIP: No product_code")
            continue
        
        if is_dup:
            skipped.append({'file': docx_file, 'reason': reason})
            print(f"  SKIP: {reason}")
        else:
            new_products.append({
                'product_code': product_code,
                'name': name,
                'tour_code': info.get('tour_code', ''),
                'route': info.get('route', ''),
                'departure_city': info.get('departure_city', ''),
                'arrival_city': info.get('arrival_city', info.get('departure_city', '')),
                'duration': info.get('duration', ''),
                'price': info.get('price', ''),
                'highlights': info.get('highlights', ''),
                'dates': info.get('dates', '')
            })
            print(f"  NEW PRODUCT FOUND!")
    
    # 总结
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total scanned: {len(docx_files)}")
    print(f"New products: {len(new_products)}")
    print(f"Skipped: {len(skipped)}")
    
    if new_products:
        print("\n[NEW PRODUCTS TO ADD]")
        for p in new_products:
            print(f"\n  [{p['product_code']}] {p['name']}")
            print(f"    tour_code: {p['tour_code']}")
            print(f"    departure_city: {p['departure_city']}")
            print(f"    duration: {p['duration']}")
            print(f"    price: {p['price'][:80]}")
            if p.get('route'):
                print(f"    route: {p['route'][:100]}")
            if p.get('highlights'):
                print(f"    highlights: {p['highlights'][:100]}")
    
    if skipped:
        print("\n[SKIPPED]")
        for s in skipped:
            print(f"  - {s['file'][:60]}")
            print(f"    Reason: {s['reason']}")
    
    print(f"\n{'=' * 70}")
    
    return new_products, skipped

if __name__ == '__main__':
    main()
