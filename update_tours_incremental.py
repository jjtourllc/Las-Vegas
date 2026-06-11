#!/usr/bin/env python3
"""增量更新团单数据：扫描出团单目录，提取新增团单信息，更新 tours.json"""

import json
import os
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# 路径配置
TOUR_DIR = Path(r"D:\旅游工作\出团单")
TOURS_JSON_PATH = Path(r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tours.json")
TOUR_FILES_DIR = Path(r"C:\Users\Johnny\WorkBuddy AI\长寿\explore-routes\tour-files")

def list_docx_files(directory):
    """列出目录下的所有 .docx 文件"""
    if not directory.exists():
        print(f"❌ 出团单目录不存在: {directory}")
        return []
    files = sorted([f for f in directory.iterdir() if f.suffix.lower() == '.docx'])
    print(f"📁 扫描到 {len(files)} 个 .docx 文件")
    for f in files:
        print(f"   - {f.name}")
    return files

def load_tours_json():
    """加载现有的 tours.json"""
    if not TOURS_JSON_PATH.exists():
        print(f"❌ tours.json 不存在: {TOURS_JSON_PATH}")
        return []
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_new_files(docx_files, existing_tours):
    """找出新增的团单文件"""
    existing_filenames = {t.get('filename', '') for t in existing_tours}
    new_files = []
    skipped_count = 0
    
    for f in docx_files:
        if f.name in existing_filenames:
            skipped_count += 1
        else:
            new_files.append(f)
    
    print(f"\n📊 已有 {len(existing_filenames)} 个团单在 tours.json 中")
    print(f"⏭️  跳过 {skipped_count} 个已处理的文件")
    print(f"🆕 新增 {len(new_files)} 个团单需要处理")
    return new_files

def extract_docx_content(docx_path):
    """从 docx 文件中提取文本内容"""
    try:
        with zipfile.ZipFile(docx_path, 'zip') as z:
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # 定义命名空间
                namespaces = {
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                }
                
                # 提取所有文本
                text_parts = []
                for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                    if texts:
                        text_parts.append(''.join(texts))
                
                return '\n'.join(text_parts)
    except Exception as e:
        print(f"❌ 解析 {docx_path.name} 失败: {e}")
        return ""

def extract_route_from_content(text, docx_name):
    """从团单文本中提取 route 字段（途径景点）"""
    route_parts = []
    
    # 方法1: 尝试从"途经地点"字段提取
    lines = text.split('\n')
    in_route_section = False
    for line in lines:
        line_stripped = line.strip()
        if '途经地点' in line or '途经' in line or '景点' in line:
            in_route_section = True
            continue
        if in_route_section:
            # 如果下一行是新的标题（不以顿号、、分隔），停止提取
            if line_stripped and not any(line_stripped.startswith(p) for p in ['、', '·', '·', '◆', '·']):
                if any(kw in line_stripped for kw in ['行程', '特色', '价格', '日期', '团期', '套餐', '酒店', '备注', '说明']):
                    break
            route_parts.append(line_stripped)
    
    if route_parts:
        return '、'.join(filter(None, route_parts))
    
    # 方法2: 从行程介绍中提取国家公园和著名景点
    national_parks = [
        '锡安国家公园', '布莱斯峡谷国家公园', '大峡谷国家公园',
        '大提顿国家公园', '黄石国家公园', '优胜美地国家公园',
        '约书亚树国家公园', '峡谷地国家公园', '拱门国家公园',
        '红木国家公园', '国王峡谷国家公园', ' Sequoia国家公园'
    ]
    
    famous_spots = [
        '羚羊彩穴', '下羚羊彩穴', '上羚羊彩穴', '马蹄湾',
        '七彩巨石', '大盐湖', '鲍威尔湖', '魔鬼塔', '疯马巨石',
        '总统山', '拉斯维加斯', '拱门', ' Zion', 'Yosemite',
        'Grand Canyon', 'Bryce Canyon', 'Yellowstone', 'Grand Teton'
    ]
    
    extracted_spots = []
    for line in lines:
        for park in national_parks:
            if park in line:
                if park not in extracted_spots:
                    extracted_spots.append(park)
        for spot in famous_spots:
            if spot.lower() in line.lower():
                spot_cn = spot
                if 'Zion' in spot: spot_cn = '锡安国家公园'
                elif 'Yosemite' in spot: spot_cn = '优胜美地国家公园'
                elif 'Grand Canyon' in spot: spot_cn = '大峡谷国家公园'
                elif 'Bryce Canyon' in spot: spot_cn = '布莱斯峡谷国家公园'
                elif 'Yellowstone' in spot: spot_cn = '黄石国家公园'
                elif 'Grand Teton' in spot: spot_cn = '大提顿国家公园'
                if spot_cn not in extracted_spots:
                    extracted_spots.append(spot_cn)
    
    return '、'.join(extracted_spots) if extracted_spots else ""

def extract_tour_info(docx_path, docx_name):
    """从团单文件中提取完整信息"""
    print(f"\n📖 正在解析: {docx_name}")
    
    text = extract_docx_content(docx_path)
    if not text:
        print(f"⚠️  文件内容为空，使用默认值")
        return {
            "name": docx_name.replace('.docx', ''),
            "filename": docx_name,
            "product_code": "",
            "tour_code": "",
            "departure_city": "",
            "arrival_city": "",
            "duration": "",
            "price": "",
            "dates": "",
            "highlights": "",
            "route": "",
            "active": True
        }
    
    # 提取团单名称
    name = docx_name.replace('.docx', '').strip()
    
    # 从文本中提取各个字段
    product_code = ""
    tour_code = ""
    departure_city = ""
    arrival_city = ""
    duration = ""
    price = ""
    dates = ""
    highlights = ""
    
    lines = text.split('\n')
    
    # 提取产品代码和产品名称
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if '产品代码' in line_stripped or '产品编码' in line_stripped:
            # 取冒号或等号后面的内容
            parts = line_stripped.replace('产品代码', '').replace('产品编码', '').replace(':', '').replace('：', '').replace('=', '').strip()
            # 提取代码部分（通常是字母数字组合）
            import re
            code_match = re.findall(r'[A-Z]{1,4}\d{1,5}|[A-Z]{2,4}', parts)
            if code_match:
                product_code = code_match[0].strip()
        if '产品名称' in line_stripped or '团名' in line_stripped:
            arrival_city = line_stripped.replace('产品名称', '').replace('团名', '').replace(':', '').replace('：', '').strip()
    
    # 从文件名提取出发城市和到达城市信息
    # 根据文件名中的城市信息推断
    city_patterns = {
        '洛杉矶': '洛杉矶 Los Angeles',
        '拉斯维加斯': '拉斯维加斯 Las Vegas',
        '盐湖城': '盐湖城 Salt Lake City',
    }
    
    departure_city = ""
    arrival_city = ""
    
    # 如果文件名以"洛杉矶"开头或包含"洛杉矶接机"，出发城市是洛杉矶
    if '洛杉矶接机' in docx_name or (docx_name.startswith('洛杉矶') and '接机' not in docx_name):
        departure_city = "洛杉矶 Los Angeles"
    
    # 如果文件名以"洛杉矶"结尾或包含"洛杉矶自由行"，到达城市是洛杉矶
    if '洛杉矶自由行' in docx_name or ('洛杉矶' in docx_name and '出发' not in docx_name and '接机' not in docx_name):
        arrival_city = "洛杉矶 Los Angeles"
    
    # 如果文件名以"盐湖城"开头，出发城市是盐湖城
    if docx_name.startswith('盐湖城') or '盐湖城进出' in docx_name:
        departure_city = "盐湖城 Salt Lake City"
        arrival_city = "盐湖城 Salt Lake City"
    
    # 如果文件名以"就是精品"开头，检查出发城市
    if '就是精品' in docx_name or '精品' in docx_name:
        if '盐湖城' in docx_name:
            departure_city = "盐湖城 Salt Lake City"
            arrival_city = "盐湖城 Salt Lake City"
        elif '拉斯维加斯' in docx_name or '拉斯维加斯接机' in docx_name:
            departure_city = "拉斯维加斯 Las Vegas"
            if '洛杉矶自由行' in docx_name:
                arrival_city = "洛杉矶 Los Angeles"
            else:
                arrival_city = "洛杉矶 Los Angeles"
        elif '洛杉矶' in docx_name:
            departure_city = "洛杉矶 Los Angeles"
            arrival_city = "洛杉矶 Los Angeles"
        elif '拉斯维加斯+锡安' in docx_name:
            departure_city = "拉斯维加斯 Las Vegas"
            arrival_city = "洛杉矶 Los Angeles"
    
    # 如果没有从文件名提取到，尝试从文本中提取
    if not departure_city:
        for line in lines:
            line_stripped = line.strip()
            if '出发城市' in line_stripped or '出发地' in line_stripped:
                parts = line_stripped.replace('出发城市', '').replace('出发地', '').replace(':', '').replace('：', '').strip()
                departure_city = parts
            if '到达城市' in line_stripped or '目的地' in line_stripped:
                parts = line_stripped.replace('到达城市', '').replace('目的地', '').replace(':', '').replace('：', '').strip()
                arrival_city = parts
    
    # 提取行程天数
    for line in lines:
        line_stripped = line.strip()
        if '行程天数' in line_stripped or '天数' in line_stripped or 'DURATION' in line_stripped:
            duration = line_stripped.replace('行程天数', '').replace('天数', '').replace('DURATION', '').replace(':', '').replace('：', '').strip()
            break
        # 从团名中提取天数
        import re
        duration_match = re.search(r'(\d+)日游', docx_name)
        if duration_match:
            days = int(duration_match.group(1))
            duration = f"{days} 天 {days-1} 晚"
    
    # 提取价格
    for line in lines:
        line_stripped = line.strip()
        if ('价格' in line_stripped or 'PRICE' in line_stripped) and ('套餐' not in line_stripped):
            # 跳过套餐标题行
            if '套餐' not in line_stripped or '价格' in line_stripped:
                parts = line_stripped.replace('价格', '').replace('PRICE', '').replace(':', '').replace('：', '').strip()
                if parts and '/人' in parts:
                    price = parts
                    break
    
    # 从文件名直接提取价格信息（如果文本中没有）
    if not price:
        price = ""
    
    # 提取团期
    for line in lines:
        line_stripped = line.strip()
        if '团期' in line_stripped or 'DATES' in line_stripped or '班期' in line_stripped:
            dates_parts = [line_stripped]
            # 收集后续几行
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j].strip()
                if next_line and not any(next_line.startswith(kw) for kw in ['行程', '特色', '价格', '备注', '说明', '酒店', '含']):
                    dates_parts.append(next_line)
                else:
                    break
            dates = '\n'.join(dates_parts)
            break
    
    # 从文件名提取团期（如果没有从文本中提取到）
    if not dates:
        dates = "两人成团，保证出发"
    
    # 提取行程特色/亮点
    highlights = ""
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if '行程特色' in line_stripped or '特色' in line_stripped or '亮点' in line_stripped:
            hl_parts = [line_stripped]
            for j in range(i+1, min(i+30, len(lines))):
                next_line = lines[j].strip()
                if next_line:
                    hl_parts.append(next_line)
                else:
                    break
            highlights = '\n'.join(hl_parts)
            break
    
    # 提取 route（途径景点）
    route = extract_route_from_content(text, docx_name)
    
    # 如果 route 为空，尝试从文件名提取景点
    if not route:
        park_spots = []
        spot_keywords = [
            '锡安国家公园', '布莱斯峡谷国家公园', '大峡谷国家公园',
            '大提顿国家公园', '黄石国家公园', '优胜美地国家公园',
            '约书亚树国家公园', '峡谷地国家公园', '拱门国家公园',
            '羚羊彩穴', '下羚羊彩穴', '马蹄湾', '七彩巨石', '大盐湖'
        ]
        for spot in spot_keywords:
            if spot in docx_name:
                park_spots.append(spot)
        route = '、'.join(park_spots) if park_spots else ""
    
    # 如果 route 仍然为空，从全文中提取
    if not route:
        park_spots = []
        spot_keywords = [
            '锡安国家公园', '布莱斯峡谷国家公园', '大峡谷国家公园',
            '大提顿国家公园', '黄石国家公园', '优胜美地国家公园',
            '约书亚树国家公园', '峡谷地国家公园', '拱门国家公园',
            '羚羊彩穴', '下羚羊彩穴', '上羚羊彩穴', '马蹄湾',
            '七彩巨石', '大盐湖', '鲍威尔湖', '魔鬼塔', '疯马巨石', '总统山', '拉斯维加斯'
        ]
        for spot in spot_keywords:
            if spot in text:
                park_spots.append(spot)
        route = '、'.join(park_spots) if park_spots else ""
    
    return {
        "name": name,
        "filename": docx_name,
        "product_code": product_code,
        "tour_code": tour_code,
        "departure_city": departure_city,
        "arrival_city": arrival_city,
        "duration": duration,
        "price": price,
        "dates": dates,
        "highlights": highlights,
        "route": route,
        "active": True
    }

def copy_to_tour_files(source_path, dest_dir):
    """复制文件到 tour-files 目录"""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / source_path.name
    try:
        shutil.copy2(source_path, dest_path)
        print(f"✅ 已复制到 tour-files: {dest_path.name}")
        return True
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 团单数据增量更新工具")
    print("=" * 60)
    
    # 第一步：扫描出团单目录
    print("\n📋 第一步：扫描出团单目录")
    docx_files = list_docx_files(TOUR_DIR)
    if not docx_files:
        print("⚠️ 出团单目录为空，跳过")
        return
    
    # 第二步：增量比对
    print("\n📋 第二步：增量比对")
    existing_tours = load_tours_json()
    new_files = find_new_files(docx_files, existing_tours)
    
    if not new_files:
        print("\n✅ 没有新团单需要更新")
        return
    
    # 第三、四步：复制并提取信息
    print("\n📋 第三、四步：复制文件并提取信息")
    new_tours = []
    for f in new_files:
        if copy_to_tour_files(f, TOUR_FILES_DIR):
            tour_info = extract_tour_info(f, f.name)
            new_tours.append(tour_info)
    
    # 第五步：更新 tours.json
    print("\n📋 第五步：更新 tours.json")
    if new_tours:
        existing_tours.extend(new_tours)
        with open(TOURS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(existing_tours, f, ensure_ascii=False, indent=2)
        print(f"✅ 已更新 tours.json，新增 {len(new_tours)} 个团单")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 执行结果汇总")
    print("=" * 60)
    print(f"扫描到文件数: {len(docx_files)}")
    print(f"新增团单数: {len(new_files)}")
    print(f"跳过已处理: {len(docx_files) - len(new_files)}")
    
    if new_tours:
        print("\n新增团单详情:")
        for t in new_tours:
            print(f"  - {t['name']}")
            print(f"    出发: {t['departure_city']}")
            print(f"    到达: {t['arrival_city']}")
            print(f"    行程: {t['duration']}")
            print(f"    价格: {t['price']}")
            print(f"    途径: {t['route'][:50]}..." if len(t['route']) > 50 else f"    途径: {t['route']}")
            print()
    
    print("请手动执行 git 提交和推送，以及 CloudStudio 部署")

if __name__ == '__main__':
    main()
