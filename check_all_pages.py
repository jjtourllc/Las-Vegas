#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全面检查三个网页"""
import os
import re
from pathlib import Path

base = Path("C:/Users/Johnny/WorkBuddy AI/长寿")

def check_file(filepath, label):
    print(f"\n{'='*60}")
    print(f"📄 检查: {label}")
    print(f"{'='*60}")
    
    path = base / filepath
    if not path.exists():
        print(f"❌ 文件不存在: {filepath}")
        return
    
    content = path.read_text(encoding='utf-8')
    issues = []
    
    # 1. 检查图片路径
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', content)
    for img in imgs:
        if not img.startswith('http') and not img.startswith('data:'):
            img_path = base / Path(img)
            if not img_path.exists():
                issues.append(f"🖼 图片不存在: {img}")
    
    # 2. 检查锚点链接
    anchors = re.findall(r'href="(#\w+)"', content)
    sections = re.findall(r'id="(\w+)"', content)
    for a in anchors:
        if a != '#' and a not in ['#', '#contact']:
            if a not in ['#tours', '#features', '#fleet', '#contact'] + [f'#{s}' for s in sections]:
                issues.append(f"🔗 锚点可能不存在: {a}")
    
    # 3. 检查 openModal / closeModal
    opens = re.findall(r"openModal\('([^']+)'\)", content)
    closes = re.findall(r"closeModal\('([^']+)'\)", content)
    modals = re.findall(r'id="modal-tour([^"]+)"', content)
    
    for o in opens:
        if o not in modals:
            issues.append(f"❌ openModal('tour{o}') 对应的 modal-tour{o} 不存在")
    
    for c in closes:
        if c not in modals:
            issues.append(f"⚠️ closeModal('tour{c}') 但 modal-tour{c} 不存在")
    
    # 4. 检查下载链接
    downloads = re.findall(r'href="(tour-docs/[^"]+)"', content)
    if filepath == 'index.html':
        tour_docs = (base / 'tour-docs')
        if tour_docs.exists():
            actual_files = [f.name for f in tour_docs.iterdir() if f.is_file()]
            for d in downloads:
                # 提取文件名
                filename = os.path.basename(d)
                # 模糊匹配
                found = any(filename.replace(' ', '') == f.replace(' ', '') for f in actual_files)
                if not found:
                    issues.append(f"⚠️ 下载链接文件可能不存在: {filename}")
    
    # 5. 检查 JS 函数定义
    js_functions = re.findall(r'function (\w+)', content)
    calls = re.findall(r'(\w+)\(\)', content)
    for call in calls:
        if call in ['toggleNav', 'closeNav', 'openModal', 'closeModal', 'openQrOverlay', 'closeQrOverlay', 'copyEmail', 'animateOnScroll'] and call not in js_functions:
            issues.append(f"⚠️ 函数 {call}() 被调用但未在页面中定义")
    
    # 6. 检查 HTML 结构完整性
    open_tags = len(re.findall(r'<[a-z][^>]+>', content, re.IGNORECASE))
    close_tags = len(re.findall(r'</[a-z]+>', content, re.IGNORECASE))
    # 不精确检查，只是提示
    
    # 7. 检查 explore-routes 链接
    explore_links = re.findall(r'href="(explore-routes/[^"]+)"', content)
    for link in explore_links:
        explore_path = base / link
        if not explore_path.exists():
            issues.append(f"🔗 链接不存在: {link}")
    
    # 8. 检查 photo-gallery 链接
    gallery_links = re.findall(r'href="(photo-gallery\.html)"', content)
    gallery_path = base / 'photo-gallery.html'
    for link in gallery_links:
        if not gallery_path.exists():
            issues.append(f"🔗 相册页面不存在")
    
    if issues:
        print(f"\n⚠️ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n✅ 没有发现严重问题")
    
    # 统计信息
    print(f"\n📊 统计:")
    print(f"  图片: {len(imgs)} 个")
    print(f"  Modal 映射: {len(opens)} 个 openModal, {len(modals)} 个 modal")
    print(f"  下载链接: {len(downloads)} 个")
    print(f"  锚点链接: {len([a for a in anchors if a != '#'])} 个")
    print(f"  JS 函数: {len(js_functions)} 个")

# 检查三个页面
check_file('index.html', '首页 (index.html)')
check_file('photo-gallery.html', '景点相册 (photo-gallery.html)')
check_file('explore-routes/index.html', '探索线路 (explore-routes/index.html)')

print(f"\n{'='*60}")
print("✅ 全面检查完成")
print(f"{'='*60}")
