#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅游产品卡片自动化更新脚本
扫描出团单文件夹中的 DOCX 文件，解析产品信息，与 tours.json 对比，发现新产品并添加
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import os
import shutil
import re
import sys
import locale

# 设置控制台编码为 UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except:
    pass

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

def parse_docx_text(file_path):
    """解析 DOCX 文件，返回所有段落文本列表"""
    with zipfile.ZipFile(file_path, 'r') as z:
        # 读取 word/document.xml
        with z.open('word/document.xml') as doc_xml:
            tree = ET.parse(doc_xml)
            root = tree.getroot()
            
            paragraphs = []
            tables = []
            
            # 提取所有段落
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

def extract_product_info(file_name, paragraphs, tables):
    """从 DOCX 文件中提取产品信息"""
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
    
    # 从文件名提取产品名称（去掉后缀）
    name = file_name.replace('.docx', '')
    # 去掉"（套餐）"等后缀
    name = re.sub(r'（套餐）\s*\.?$', '', name)
    info['name'] = name
    
    # --- 从表格提取 product_code, tour_code ---
    # 通常第一个表格是产品信息表
    if len(tables) > 0:
        product_table = tables[0]
        for row in product_table:
            for cell in row:
                cell = cell.strip()
                # 匹配 product_code
                pc_match = re.search(r'(?:产品编号|product_code|产品代码|产品编码)\s*:?\s*(R\d+)', cell)
                if pc_match:
                    info['product_code'] = pc_match.group(1)
                
                # 匹配 tour_code
                tc_match = re.search(r'(?:线路编号|tour_code|团期编号|出团编号)\s*:?\s*([A-Z0-9]+)', cell)
                if tc_match:
                    info['tour_code'] = tc_match.group(1)
                
                # 匹配出发城市
                dc_match = re.search(r'(?:出发城市|departure_city|出发地)\s*:?\s*([\u4e00-\u9fa5a-zA-Z\s,]+?)(?:\s*$|\s*[，,])', cell)
                if dc_match:
                    city_text = dc_match.group(1).strip()
                    if city_text and len(city_text) < 50 and '：' not in city_text and '产品' not in city_text:
                        info['departure_city'] = city_text
                
                # 匹配返回城市
                ac_match = re.search(r'(?:返回城市|arrival_city|返回地)\s*:?\s*([\u4e00-\u9fa5a-zA-Z\s,]+?)(?:\s*$|\s*[，,])', cell)
                if ac_match:
                    city_text = ac_match.group(1).strip()
                    if city_text and len(city_text) < 50 and '：' not in city_text and '产品' not in city_text:
                        info['arrival_city'] = city_text
                
                # 匹配天数
                dur_match = re.search(r'(?:天数|duration|行程天数|行程时间)\s*:?\s*(\d+\s*天\s*\d+\s*晚?)', cell)
                if dur_match:
                    info['duration'] = dur_match.group(1).strip()
    
    # --- 从第二个表格提取价格信息 ---
    if len(tables) > 1:
        price_table = tables[1]
        price_parts = []
        for row in price_table:
            for cell in row:
                cell = cell.strip()
                # 匹配价格模式（包含 /人 的数字）
                prices = re.findall(r'[\d,]+\s*/\s*人', cell)
                if prices:
                    for p in prices:
                        price_parts.append(p.strip())
        if price_parts:
            info['price'] = ', '.join(price_parts)
    
    # --- 从班期表提取 dates 信息（通常是第5个表格，索引4）---
    if len(tables) > 4:
        dates_table = tables[4]
        dates_lines = []
        for row in dates_table:
            for cell in row:
                cell = cell.strip()
                if cell and len(cell) > 2:
                    dates_lines.append(cell)
        if dates_lines:
            info['dates'] = '\n'.join(dates_lines)
    
    # --- 从正文段落提取 highlights（行程特色）---
    highlights_lines = []
    in_highlights = False
    in_route = False
    route_marker_found = False
    
    for para in paragraphs:
        para_stripped = para.strip()
        
        # 检测行程特色标题
        if any(marker in para_stripped for marker in ['行程特色', '行程亮点', '特色说明', '特色：']):
            in_highlights = True
            in_route = False
            # 提取特色说明内容
            if '：' in para_stripped:
                content = para_stripped.split('：', 1)[1].strip()
                if content:
                    highlights_lines.append(content)
            elif ':' in para_stripped:
                content = para_stripped.split(':', 1)[1].strip()
                if content:
                    highlights_lines.append(content)
            continue
        
        # 检测途径路径标记
        if any(marker in para_stripped for marker in ['途经', '途径', '途径城市', 'route:', '途经城市']):
            in_route = True
            in_highlights = False
            # 提取路径内容
            if '：' in para_stripped:
                content = para_stripped.split('：', 1)[1].strip()
                if content:
                    info['route'] = content
            elif ':' in para_stripped:
                content = para_stripped.split(':', 1)[1].strip()
                if content:
                    info['route'] = content
            route_marker_found = True
            continue
        
        # 在 highlights 区域内收集内容
        if in_highlights and para_stripped:
            # 排除一些不应该属于 highlights 的行
            if not any(skip in para_stripped for skip in ['途经', '途径', '产品名称', '产品编号', '出发城市', '返回城市', '天数', ' Departure']):
                highlights_lines.append(para_stripped)
        
        # 在 route 区域内收集内容（如果有）
        if in_route and para_stripped and not route_marker_found:
            # 如果前面没有从行首提取到 route，则从后续段落收集
            pass
    
    if highlights_lines:
        info['highlights'] = ' '.join(highlights_lines[:5])  # 限制长度
    
    # 如果 route 为空，尝试从 highlights 之后的文本中寻找路径信息
    if not info['route']:
        collecting_route = False
        route_parts = []
        for para in paragraphs:
            para_stripped = para.strip()
            if any(marker in para_stripped for marker in ['途经', '途径', '途径城市']):
                collecting_route = True
                continue
            if collecting_route and para_stripped:
                # 遇到下一个标题或空行停止
                if para_stripped.startswith('行程') or para_stripped.startswith('产品') or para_stripped.startswith('出发'):
                    break
                if len(para_stripped) > 5 and len(para_stripped) < 500:
                    # 看起来像路径的文本
                    if any(loc in para_stripped for loc in ['公园', 'National', 'Park', ' Canyon', ' River', ' Bay']):
                        route_parts.append(para_stripped)
        if route_parts:
            info['route'] = '、'.join(route_parts)
    
    return info

def check_if_new_product(product_code, existing_codes):
    """检查是否为新产品"""
    if not product_code:
        return False, "未找到 product_code"
    if product_code in existing_codes:
        return False, f"产品 {product_code} 已存在"
    return True, ""

def main():
    print("=" * 60)
    print("Travel Product Card Auto Update Script")
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
        
        paragraphs, tables = parse_docx_text(file_path)
        info = extract_product_info(docx_file, paragraphs, tables)
        
        pc_display = info['product_code'] or '(NOT FOUND)'
        tc_display = info['tour_code'] or '(NOT FOUND)'
        print(f"  product_code: {pc_display}")
        print(f"  tour_code: {tc_display}")
        print(f"  departure_city: {info['departure_city']}")
        print(f"  arrival_city: {info['arrival_city']}")
        print(f"  duration: {info['duration']}")
        price_short = info['price'][:50] + '...' if len(info['price']) > 50 else info['price']
        print(f"  price: {price_short}")
        highlights_short = info['highlights'][:50] + '...' if len(info['highlights']) > 50 else info['highlights']
        print(f"  highlights: {highlights_short}")
        
        # 检查是否为新产品的逻辑（通过文件名对比 tour-files 中已存在的文件）
        is_duplicate = False
        reason = ""
        
        # 检查 product_code 是否已有
        if info['product_code'] in existing_codes:
            is_duplicate = True
            reason = f"Product {info['product_code']} already in tours.json"
        
        # 检查文件是否已经在 tour-files 目录中（文件名匹配）
        dest_dir = TOUR_FILES_DIR
        dest_file = os.path.join(dest_dir, docx_file)
        if os.path.exists(dest_file):
            is_duplicate = True
            reason = f"文件已在 tour-files 目录中"
        
        # 如果 product_code 为空，可能是新产品但无法识别
        if not info['product_code'] and not is_duplicate:
            print(f"  WARNING: No product_code recognized, skipping (possibly new format)")
            skipped_products.append({'file': docx_file, 'reason': 'No product_code recognized'})
            continue
        
        if is_duplicate:
            skipped_products.append({'file': docx_file, 'reason': reason})
            print(f"  SKIP: {reason}")
        else:
            # 确定 arrival_city（如果没有则用 departure_city）
            if not info['arrival_city']:
                info['arrival_city'] = info['departure_city']
            
            new_products.append(info)
            print(f"  NEW: {info['name'][:40]}...")
    
    # 4. 输出结果
    print(f"\n{'=' * 60}")
    print("Update Results Summary")
    print(f"{'=' * 60}")
    print(f"DOCX files parsed: {len(docx_files)}")
    print(f"New products found: {len(new_products)}")
    print(f"Skipped products: {len(skipped_products)}")
    
    if new_products:
        print("\n[NEW PRODUCTS]")
        for p in new_products:
            print(f"  [{p['product_code']}] {p['name'][:50]}")
            print(f"    Departure: {p['departure_city']} | Duration: {p['duration']}")
    
    if skipped_products:
        print("\n[SKIPPED PRODUCTS]")
        for s in skipped_products:
            print(f"  - {s['file']}")
            print(f"    Reason: {s['reason']}")
    
    return new_products, skipped_products

if __name__ == '__main__':
    main()
