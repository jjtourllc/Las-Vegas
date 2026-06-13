#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游产品卡片自动化更新脚本 v4
从 DOCX 文件精确提取产品信息 - 修正版
关键改进：从表格的原始 XML 结构中提取数据，而非扁平化段落列表
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
import re

# 配置路径
OUTUAN_DOCX_DIR = r"D:\旅游工作\出团单"
TOURS_JSON_PATH = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tours.json"
TOUR_FILES_DIR = r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tour-files"

NS_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS_WPK = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def get_existing_product_codes():
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        tours = json.load(f)
    return {tour['product_code'] for tour in tours}

def parse_docx_raw(file_path):
    """解析 DOCX 文件，返回原始 XML 数据和解析后的段落/表格"""
    with zipfile.ZipFile(file_path, 'r') as z:
        with z.open('word/document.xml') as doc_xml:
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            
            # 提取原始段落文本
            paragraphs = []
            for para in root.findall('.//' + NS_W + 'p'):
                texts = []
                for run in para.findall('.//' + NS_W + 't'):
                    if run.text:
                        texts.append(run.text)
                if texts:
                    paragraphs.append(''.join(texts))
            
            # 从表格的原始 XML 结构提取数据
            tables = []
            for table_idx, table in enumerate(root.findall('.//' + NS_W + 'tbl')):
                rows_data = []
                for row in table.findall('.//' + NS_W + 'tr'):
                    cells_data = []
                    for cell in row.findall('.//' + NS_W + 'tc'):
                        # 从每个单元格中提取所有文本
                        cell_texts = []
                        for p in cell.findall('.//' + NS_W + 'p'):
                            for run in p.findall('.//' + NS_W + 't'):
                                if run.text:
                                    cell_texts.append(run.text)
                        cells_data.append(''.join(cell_texts))
                    rows_data.append(cells_data)
                tables.append(rows_data)
            
            return paragraphs, tables

def extract_from_table_0(table):
    """从产品信息表（通常是第一个表格）提取关键字段
    
    根据调试结果，表格结构是键值对形式，每行可能包含：
    - 标签: 值
    或者标签和值在不同的单元格中
    """
    info = {}
    
    if not table or len(table) == 0:
        return info
    
    # 方法1：遍历所有行，查找"标签: 值"格式
    for row in table:
        for cell in row:
            cell = cell.strip()
            if not cell:
                continue
            
            # 匹配 "标签：值" 或 "标签: 值" 格式
            # 产品编号
            m = re.search(r'产品编号\s*[：:]\s*(R\d+)', cell)
            if m:
                info['product_code'] = m.group(1)
                continue
            
            # 团号
            m = re.search(r'(?:团号|线路编号|出团编号)\s*[：:]\s*([A-Za-z0-9\-]+)', cell)
            if m:
                info['tour_code'] = m.group(1)
                continue
            
            # 出发城市
            m = re.search(r'出发城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000 ]+?)(?:\s*$|[\n\r])', cell)
            if m:
                city = m.group(1).strip()
                if city and len(city) < 50:
                    info['departure_city'] = city
                continue
            
            # 目的地城市
            m = re.search(r'目的地城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000 ]+?)(?:\s*$|[\n\r])', cell)
            if m:
                city = m.group(1).strip()
                if city and len(city) < 50:
                    info['arrival_city'] = city
                continue
            
            # 返回城市
            m = re.search(r'返回城市\s*[：:]\s*([\u4e00-\u9fa5a-zA-Z\u3000 ]+?)(?:\s*$|[\n\r])', cell)
            if m and 'arrival_city' not in info:
                city = m.group(1).strip()
                if city and len(city) < 50:
                    info['arrival_city'] = city
                continue
            
            # 行程天数
            m = re.search(r'(?:行程天数|行程时间|天数)\s*[：:]\s*(\d+\s*天\s*\d*\s*晚?)', cell)
            if m:
                info['duration'] = m.group(1).strip()
                continue
            
            # 价格
            m = re.search(r'产品价格\s*[：:]?', cell)
            if m:
                # 价格可能在同一行或下一行
                prices = re.findall(r'[\$\d,]+\s*/\s*人', cell)
                if prices:
                    info['price'] = ', '.join(prices)
                continue
            
            # 途经地点
            m = re.search(r'途经(?:地点)?\s*[：:]\s*(.+?)(?:\s*$)', cell)
            if m:
                info['route'] = m.group(1).strip()
                continue
            
            # 出发班期
            m = re.search(r'出发班期\s*[：:]?', cell)
            if m:
                info['dates_found'] = True
                continue
            
            # 行程特色
            m = re.search(r'行程特色\s*[：:]?\s*(.+)', cell)
            if m:
                info['highlights_start'] = True
                info['highlights'] = m.group(1).strip()
                continue
    
    # 方法2：遍历所有单元格，尝试提取"标签"在一行，"值"在另一行的情况
    # 将整个表格拼接成一个文本列表
    all_cells = []
    for row in table:
        for cell in row:
            all_cells.append(cell.strip())
    
    # 查找键值配对
    for i, cell in enumerate(all_cells):
        # 产品编号
        if cell == '产品编号' and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val.startswith('R') and val.isdigit():
                info.setdefault('product_code', val)
        
        # 团号
        elif cell in ['团号', '线路编号', '出团编号', '团期编号'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and len(val) < 20 and not val.startswith('$') and '说明' not in val:
                info.setdefault('tour_code', val)
        
        # 出发城市
        elif cell in ['出发城市', '出发地'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and len(val) < 100 and '产品' not in val and '费用' not in val:
                info.setdefault('departure_city', val)
        
        # 目的地城市
        elif cell in ['目的地城市', '目的地'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and len(val) < 100 and '产品' not in val:
                info.setdefault('arrival_city', val)
        
        # 返回城市
        elif cell in ['返回城市', '返回地'] and i + 1 < len(all_cells) and 'arrival_city' not in info:
            val = all_cells[i + 1].strip()
            if val and len(val) < 100 and '产品' not in val:
                info.setdefault('arrival_city', val)
        
        # 行程天数
        elif cell in ['行程天数', '行程时间', '天数'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and '天' in val:
                info.setdefault('duration', val)
        
        # 产品价格
        elif cell in ['产品价格', '价格'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and ('$' in val or '/人' in val):
                info.setdefault('price', val)
        
        # 出发班期
        elif cell in ['出发班期', '班期'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val:
                info.setdefault('dates', val)
        
        # 途经地点
        elif cell in ['途经地点', '途经', '途径'] and i + 1 < len(all_cells):
            val = all_cells[i + 1].strip()
            if val and len(val) < 500:
                info.setdefault('route', val)
    
    return info

def extract_highlights_from_paragraphs(paragraphs):
    """从正文段落提取行程特色"""
    highlights = []
    in_highlights = False
    
    for para in paragraphs:
        para_stripped = para.strip()
        
        if '行程特色' in para_stripped or '行程亮点' in para_stripped:
            in_highlights = True
            # 提取冒号后的内容
            if '：' in para_stripped:
                content = para_stripped.split('：', 1)[1].strip()
                if content and len(content) < 200:
                    highlights.append(content)
            continue
        
        if in_highlights and para_stripped:
            # 停止条件：遇到新的章节标题
            if any(para_stripped.startswith(m) for m in ['产品', '出发', '行程天数', '价格', '班期', '费用', '特殊', '套餐', '预订']):
                in_highlights = False
                continue
            # 排除标签行
            if any(skip in para_stripped for skip in ['产品编号', '团号', '出发城市', '目的地', '返回城市', '天数', '价格', '途经']):
                continue
            # 收集内容（排除条款类文本）
            if len(para_stripped) > 10 and len(para_stripped) < 500:
                if not any(skip in para_stripped for skip in ['实际出行过程', '导游或司机有权', '尊享旅行有权', '服务费', '燃油附加费', '预订']):
                    highlights.append(para_stripped)
    
    return ' | '.join(highlights[:5]) if highlights else ''

def extract_dates_from_tables(tables):
    """从班期表提取 dates 信息"""
    # 班期通常在行程特色表之后，尝试查找包含日期模式的表格
    dates_parts = []
    
    for table in tables:
        # 查找包含日期格式的表格（如 MM/DD/YYYY）
        date_rows = []
        for row in table:
            for cell in row:
                if re.search(r'\d{2}/\d{2}/\d{4}', cell):
                    date_rows.append(cell)
                    break
        
        if date_rows:
            if not dates_parts:  # 优先取第一个含日期的表格
                dates_parts = date_rows
    
    if dates_parts:
        return '\n'.join(dates_parts[:20])  # 限制行数
    return ''

def create_card(info, file_name):
    """创建标准化产品卡片"""
    # 清理文件名作为 name
    name = file_name.replace('.docx', '')
    name = re.sub(r'（套餐）\s*\.?$', '', name)
    
    card = {
        'product_code': info.get('product_code', ''),
        'name': name,
        'tour_code': info.get('tour_code', ''),
        'route': info.get('route', ''),
        'departure_city': info.get('departure_city', ''),
        'arrival_city': info.get('arrival_city', info.get('departure_city', '')),
        'duration': info.get('duration', ''),
        'price': info.get('price', ''),
        'highlights': info.get('highlights', ''),
        'dates': info.get('dates', '')
    }
    return card

def main():
    print("=" * 60)
    print("Product Card Auto-Update Script v4 - Corrected Parser")
    print("=" * 60)
    
    # 1. 读取已有产品
    existing_codes = get_existing_product_codes()
    print(f"\nExisting products: {len(existing_codes)}")
    print(f"Codes: {sorted(existing_codes)}")
    
    # 2. 扫描 DOCX
    docx_files = sorted([f for f in os.listdir(OUTUAN_DOCX_DIR) if f.endswith('.docx')])
    print(f"\nDOCX files to scan: {len(docx_files)}")
    
    # 3. 解析每个文件
    new_products = []
    skipped = []
    
    for docx_file in docx_files:
        file_path = os.path.join(OUTUAN_DOCX_DIR, docx_file)
        print(f"\nProcessing: {docx_file}")
        
        paragraphs, tables = parse_docx_raw(file_path)
        
        # 从第一个表格提取基本信息
        info = {}
        if tables:
            info = extract_from_table_0(tables[0])
        
        # 从段落提取 highlights
        highlights = extract_highlights_from_paragraphs(paragraphs)
        if highlights:
            info['highlights'] = highlights
        
        # 从表格提取 dates
        dates = extract_dates_from_tables(tables)
        if dates:
            info['dates'] = dates
        
        pc = info.get('product_code', '')
        print(f"  product_code: {pc or '(NONE)'}")
        print(f"  tour_code: {info.get('tour_code', '(NONE)')}")
        print(f"  departure_city: {info.get('departure_city', '(NONE)')}")
        print(f"  arrival_city: {info.get('arrival_city', '(NONE)')}")
        print(f"  duration: {info.get('duration', '(NONE)')}")
        print(f"  price: {info.get('price', '(NONE)')[:60] if info.get('price') else '(NONE)'}")
        print(f"  route: {info.get('route', '(NONE)')[:60] if info.get('route') else '(NONE)'}")
        print(f"  highlights: {info.get('highlights', '(NONE)')[:60] if info.get('highlights') else '(NONE)'}")
        print(f"  dates: {'(FOUND)' if info.get('dates') else '(NONE)'}")
        
        # 检查是否重复
        is_dup = False
        reason = ""
        
        if pc in existing_codes:
            is_dup = True
            reason = f"Product {pc} already in tours.json"
        
        dest_file = os.path.join(TOUR_FILES_DIR, docx_file)
        if os.path.exists(dest_file) and not is_dup:
            is_dup = True
            reason = "File already in tour-files"
        
        if not pc and not is_dup:
            skipped.append({'file': docx_file, 'reason': 'No product_code found'})
            print(f"  SKIP: No product_code")
            continue
        
        if is_dup:
            skipped.append({'file': docx_file, 'reason': reason})
            print(f"  SKIP: {reason}")
        else:
            card = create_card(info, docx_file)
            new_products.append(card)
            print(f"  NEW: [{pc}] {card['name'][:40]}")
    
    # 4. 输出总结
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total scanned: {len(docx_files)}")
    print(f"New products: {len(new_products)}")
    print(f"Skipped: {len(skipped)}")
    
    if new_products:
        print("\n[NEW PRODUCTS]")
        for p in new_products:
            print(f"  [{p['product_code']}] {p['name'][:50]}")
            print(f"    Departure: {p['departure_city']} | Duration: {p['duration']}")
    
    if skipped:
        print("\n[SKIPPED]")
        for s in skipped:
            print(f"  - {s['file']}")
            print(f"    Reason: {s['reason']}")
    
    return new_products, skipped

if __name__ == '__main__':
    main()
