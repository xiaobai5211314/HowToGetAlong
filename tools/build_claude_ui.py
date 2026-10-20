#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《人情世故指南》Claude 官方 UI 主题的纯净单页检索站。
Domain: renqingshigu.21212121.xyz
Design: Claude Official UI Theme (Warm Paper / Terracotta)
"""

import os
import re
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'

def parse_book():
    chapters = []
    entries = []
    
    scene_set = set()
    person_set = set()
    topic_set = set()
    
    files = sorted(BOOK_DIR.glob('[0-9][0-9]-*.md'))
    for file in files:
        content = file.read_text(encoding='utf-8')
        lines = content.splitlines()
        if not lines:
            continue
        chapter_raw = lines[0].removeprefix('# ').strip()
        # 提取章节号和章节纯标题
        # 例: 1. 校园合作：把约定说清楚
        m_chap = re.match(r'^(\d+)\.\s*(.+)$', chapter_raw)
        if m_chap:
            chap_num = int(m_chap.group(1))
            chap_title = m_chap.group(2).strip()
        else:
            chap_num = int(file.name[:2])
            chap_title = chapter_raw
        
        chap_entries = []
        
        # 分割条目
        # ### 1. 同学找你帮忙时，先确认帮到哪一步
        parts = re.split(r'^### (\d+)\. (.+)$', content, flags=re.M)
        for i in range(1, len(parts), 3):
            item_num = int(parts[i])
            item_title = parts[i + 1].strip()
            item_body = parts[i + 2].strip()
            
            # 提取标签
            # <!-- 标签: 场景=校园 对象=同学 主题=帮忙,拒绝 -->
            tags = {'scene': [], 'person': [], 'topic': []}
            tag_match = re.search(r'<!--\s*标签:\s*(.+?)\s*-->', item_body)
            if tag_match:
                tag_str = tag_match.group(1)
                for kv in tag_str.split():
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        vals = [x.strip() for x in re.split(r'[,，]', v) if x.strip()]
                        if k == '场景':
                            tags['scene'] = vals
                            scene_set.update(vals)
                        elif k == '对象':
                            tags['person'] = vals
                            person_set.update(vals)
                        elif k == '主题':
                            tags['topic'] = vals
                            topic_set.update(vals)
            
            # 提取键值对
            # - 键：值
            pairs = re.findall(r'^- ([^：\n]+)：([^\n]+(?:\n[ \t]+[^\n]+)*)', item_body, re.M)
            fields = {}
            branches = []
            for k, v in pairs:
                k = k.strip()
                v = re.sub(r'\n[ \t]+', '\n', v).strip()
                if k.startswith('如果'):
                    branches.append({'label': k, 'text': v})
                else:
                    fields[k] = v
            
            entry = {
                'id': f"{chap_num}.{item_num}",
                'sec': chap_num,
                'n': item_num,
                'title': item_title,
                'tags': tags,
                'situation': fields.get('遇到的情况', ''),
                'judgment': fields.get('判断关键', ''),
                'preparation': fields.get('行动前准备', ''),
                'action': fields.get('先做什么', ''),
                'say': fields.get('可以怎么说', ''),
                'contexts': fields.get('分情境处理', ''),
                'cost': fields.get('花掉什么', ''),
                'gain': fields.get('可能换回什么', ''),
                'change': fields.get('何时换办法', ''),
                'exception': fields.get('例外与代价', ''),
                'basis': fields.get('依据', ''),
                'related': fields.get('相关条目', ''),
                'branches': branches
            }
            
            # 生成全局检索词
            hay_parts = [
                f"{chap_num}.{item_num}",
                item_title,
                entry['situation'],
                entry['judgment'],
                entry['preparation'],
                entry['action'],
                entry['say'],
                entry['contexts'],
                entry['cost'],
                entry['gain'],
                entry['change'],
                entry['exception'],
                entry['basis'],
                entry['related'],
                ' '.join(tags['scene']),
                ' '.join(tags['person']),
                ' '.join(tags['topic'])
            ] + [f"{b['label']} {b['text']}" for b in branches]
            entry['hay'] = ' '.join(hay_parts).lower()
            
            chap_entries.append(entry)
            entries.append(entry)
            
        chapters.append({
            'sec': chap_num,
            'title': chap_title,
            'file': file.name,
            'count': len(chap_entries),
            'items': [{'id': e['id'], 'n': e['n'], 'title': e['title']} for e in chap_entries]
        })
        
    return chapters, entries, sorted(scene_set), sorted(person_set), sorted(topic_set)


def render_html(chapters, entries, scenes, persons, topics):
    # 将 entries 和 chapters 转换为紧凑安全的 JSON
    corpus_json = json.dumps({'chapters': chapters, 'entries': entries}, ensure_ascii=False)
    
    html_template = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>人情世故指南 · 校园、职场与日常交往的处世相处宝典</title>
<meta name="description" content="面向大学生与职场新人的处世相处指南：10 个章节 77 个实战情境。讲清怎么做、怎么说，以及可能付出什么代价。每条包含判断关键、准备动作、示例表达、情境分支与依据，支持场景与对象即时检索。">
<meta name="keywords" content="人情世故,处世指南,沟通技巧,职场情商,社交礼节,拒绝技巧,职场沟通,校园社交,言语表达">
<meta name="author" content="人情世故指南">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#f5f4ed" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141413" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="https://renqing.21212121.xyz/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23c96442'/%3E%3Cpath d='M20 23h24c2.2 0 4 1.8 4 4v14c0 2.2-1.8 4-4 4H32l-8 7v-7h-4c-2.2 0-4-1.8-4-4V27c0-2.2 1.8-4 4-4z' fill='none' stroke='white' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='26' cy='34' r='2.5' fill='white'/%3E%3Ccircle cx='34' cy='34' r='2.5' fill='white'/%3E%3Ccircle cx='42' cy='34' r='2.5' fill='white'/%3E%3C/svg%3E">
<link rel="alternate icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="人情世故指南">
<meta property="og:locale" content="zh_CN">
<meta property="og:url" content="https://renqing.21212121.xyz/">
<meta property="og:title" content="人情世故指南 · 校园、职场与日常交往的相处指南">
<meta property="og:description" content="面向大学生与职场新人的处世相处指南：10 个章节 77 个实战情境。讲清怎么做、怎么说，以及可能付出什么代价。">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="人情世故指南">
<meta name="twitter:description" content="面向大学生与初入职场者的处世指南：讲清怎么做、怎么说，以及可能付出什么代价。">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "人情世故指南",
  "url": "https://renqing.21212121.xyz/",
  "description": "面向大学生与职场新人的处世相处指南：10 个章节 77 个实战情境。讲清怎么做、怎么说，以及可能付出什么代价。",
  "inLanguage": "zh-CN"
}}
</script>

<script>
(function(){{
  try {{
    var s = localStorage.getItem('theme');
    var d = s ? s === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    if (d) document.documentElement.classList.add('dark');
  }} catch(e) {{}}
}})();
</script>

<style>
/* Claude 官方 UI 调色板与排版体系 */
:root {{
  --bg: #f5f4ed;
  --bg-alt: #edebe1;
  --bg-soft: #faf9f5;
  --bg-mute: #e8e6dc;
  --bg-elv: #faf9f5;
  --divider: #e0ddcf;
  --gutter: #e8e6dc;
  --t1: #141413;
  --t2: #5e5d59;
  --t3: #87867f;
  --brand-1: #c96442;
  --brand-2: #b4573a;
  --brand-3: #d97757;
  --brand-soft: rgba(201, 100, 66, 0.10);
  --brand-border: rgba(201, 100, 66, 0.28);
  --green-1: #4d7c5f;
  --green-soft: rgba(77, 124, 95, 0.12);
  --blue-1: #35678f;
  --blue-soft: rgba(53, 103, 143, 0.11);
  --yellow-1: #96602e;
  --yellow-soft: rgba(201, 140, 80, 0.14);
  --mark: rgba(217, 119, 87, 0.25);
  --shadow: 0 1px 3px rgba(40, 35, 25, 0.05), 0 4px 20px rgba(40, 35, 25, 0.05);
  --font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  --font-serif: "Noto Serif SC", "Source Han Serif SC", "Songti SC", Georgia, serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --nav-h: 64px;
  --side-w: 284px;
  color-scheme: light;
}}

html.dark {{
  --bg: #141413;
  --bg-alt: #1a1a17;
  --bg-soft: #1f1f1b;
  --bg-mute: #2b2b27;
  --bg-elv: #232320;
  --divider: #30302e;
  --gutter: #000000;
  --t1: #faf9f5;
  --t2: #b0aea5;
  --t3: #87867f;
  --brand-1: #d97757;
  --brand-2: #e08a6d;
  --brand-3: #c96442;
  --brand-soft: rgba(217, 119, 87, 0.15);
  --brand-border: rgba(217, 119, 87, 0.32);
  --green-1: #8fbf9d;
  --green-soft: rgba(143, 191, 157, 0.14);
  --blue-1: #7aaedb;
  --blue-soft: rgba(122, 174, 219, 0.14);
  --yellow-1: #d9a066;
  --yellow-soft: rgba(217, 160, 102, 0.15);
  --mark: rgba(217, 119, 87, 0.32);
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
  color-scheme: dark;
}}

* {{ box-sizing: border-box; }}
html {{ scroll-padding-top: calc(var(--nav-h) + 16px); scrollbar-gutter: stable; }}
body {{ margin: 0; background: var(--bg); color: var(--t1); font: 14.5px/1.7 var(--font); -webkit-font-smoothing: antialiased; }}
a {{ color: var(--brand-1); text-decoration: none; transition: color .2s; }}
a:hover {{ color: var(--brand-2); text-decoration: underline; text-underline-offset: 2px; }}
button {{ font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }}
:focus-visible {{ outline: 2px solid var(--brand-1); outline-offset: 2px; border-radius: 4px; }}
::selection {{ background: var(--mark); }}
mark {{ background: var(--mark); color: inherit; border-radius: 2px; padding: 0 2px; }}

/* 顶部导航 */
.nav {{ position: fixed; top: 0; left: 0; right: 0; height: var(--nav-h); z-index: 40; background: var(--bg); border-bottom: 1px solid var(--divider); }}
.nav-in {{ height: 100%; display: flex; align-items: center; gap: 14px; padding: 0 24px; }}
.title {{ display: flex; align-items: center; gap: 10px; font-family: var(--font-serif); font-weight: 600; font-size: 17.5px; color: var(--t1); white-space: nowrap; }}
.title:hover {{ text-decoration: none; color: var(--t1); }}
.logo {{ width: 28px; height: 28px; border-radius: 8px; background: var(--brand-1); display: grid; place-items: center; color: #fff; }}
.logo svg {{ width: 17px; height: 17px; }}
.nav-badge {{ font-size: 11px; padding: 2px 7px; border-radius: 999px; background: var(--brand-soft); color: var(--brand-1); font-weight: 600; font-family: var(--font); letter-spacing: 0.04em; }}

.search {{ flex: 1; max-width: 480px; margin-left: auto; position: relative; }}
.search input {{ width: 100%; height: 38px; padding: 0 42px 0 38px; border-radius: 10px; border: 1px solid transparent; background: var(--bg-mute); color: var(--t1); font: inherit; font-size: 14px; transition: border-color .2s, background .2s, box-shadow .2s; }}
.search input:hover {{ border-color: var(--divider); }}
.search input:focus {{ outline: 0; border-color: var(--brand-1); background: var(--bg-elv); box-shadow: 0 0 0 3px var(--brand-soft); }}
.search input::placeholder {{ color: var(--t3); }}
.search svg {{ position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; fill: none; stroke: var(--t3); stroke-width: 2; pointer-events: none; }}
.search kbd {{ position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font: 500 11px/1 var(--mono); color: var(--t3); border: 1px solid var(--divider); border-radius: 4px; padding: 3px 5px; background: var(--bg-elv); pointer-events: none; }}

.nav-links {{ display: flex; align-items: center; gap: 12px; font-size: 13.5px; }}
.nav-links a {{ color: var(--t2); text-decoration: none; padding: 6px 8px; border-radius: 6px; transition: all .2s; }}
.nav-links a:hover {{ color: var(--t1); background: var(--bg-mute); text-decoration: none; }}
.nav-links a.special {{ color: var(--brand-1); font-weight: 500; }}

.switch {{ position: relative; width: 40px; height: 22px; border-radius: 11px; border: 1px solid var(--divider); background: var(--bg-mute); transition: border-color .2s, background .2s; flex: none; }}
.switch:hover {{ border-color: var(--t3); }}
.switch .knob {{ position: absolute; top: 1px; left: 1px; width: 18px; height: 18px; border-radius: 50%; background: var(--bg-elv); box-shadow: var(--shadow); transition: transform .25s; display: grid; place-items: center; }}
html.dark .switch .knob {{ transform: translateX(18px); }}
.switch svg {{ width: 12px; height: 12px; fill: var(--t2); }}
.switch .sun {{ display: block; }} .switch .moon {{ display: none; }}
html.dark .switch .sun {{ display: none; }} html.dark .switch .moon {{ display: block; }}
.menu-btn {{ display: none; width: 36px; height: 36px; border-radius: 8px; place-items: center; color: var(--t2); }}

/* 左侧边栏 */
.sidebar {{ position: fixed; top: var(--nav-h); bottom: 0; left: 0; width: var(--side-w); background: var(--bg-alt); padding: 24px 20px 80px; overflow-y: auto; overscroll-behavior: contain; z-index: 20; border-right: 1px solid var(--divider); }}
.group {{ padding-bottom: 18px; margin-bottom: 18px; border-bottom: 1px solid var(--divider); }}
.group:last-of-type {{ border-bottom: 0; }}
.gt {{ font-size: 13.5px; font-weight: 700; color: var(--t1); line-height: 20px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: baseline; }}
.gt small {{ font-weight: 400; font-size: 12px; color: var(--t3); }}

.sec-links {{ display: flex; flex-direction: column; gap: 2px; }}
.sec-link {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 6px; font-size: 13.5px; font-weight: 500; color: var(--t2); line-height: 20px; text-align: left; transition: all .15s; cursor: pointer; }}
.sec-link:hover {{ color: var(--t1); background: var(--bg-mute); }}
.sec-link[aria-pressed="true"] {{ color: var(--brand-1); background: var(--brand-soft); font-weight: 600; }}
.sec-link i {{ font-style: normal; font-size: 12px; color: var(--t3); font-variant-numeric: tabular-nums; }}
.sec-link .fold {{ display: grid; place-items: center; width: 20px; height: 20px; border-radius: 4px; color: var(--t3); margin-left: 4px; }}
.sec-link .fold:hover {{ color: var(--t1); background: var(--bg-soft); }}
.sec-link .fold svg {{ width: 14px; height: 14px; fill: none; stroke: currentColor; stroke-width: 2; transform: rotate(-90deg); transition: transform .2s; }}
.sec-link.open .fold svg {{ transform: none; }}

.toc-sub {{ display: flex; flex-direction: column; margin: 2px 0 6px 12px; padding-left: 8px; border-left: 1.5px solid var(--divider); }}
.toc-sub a {{ display: flex; gap: 6px; padding: 3px 6px; border-radius: 4px; font-size: 12.5px; line-height: 18px; color: var(--t2); text-decoration: none; transition: color .15s, background .15s; }}
.toc-sub a:hover {{ color: var(--t1); background: var(--bg-mute); text-decoration: none; }}
.toc-sub a i {{ font-style: normal; flex: none; color: var(--t3); font-variant-numeric: tabular-nums; }}
.toc-sub a span {{ display: -webkit-box; -webkit-line-clamp: 1; line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }}
.toc-sub a.on {{ color: var(--brand-1); font-weight: 600; }}

.chips {{ display: flex; flex-wrap: wrap; gap: 5px; }}
.chip {{ border: 1px solid var(--divider); background: var(--bg-elv); color: var(--t2); border-radius: 999px; padding: 2px 9px; font-size: 12px; font-weight: 500; line-height: 18px; transition: all .15s; }}
.chip:hover {{ border-color: var(--brand-3); color: var(--t1); }}
.chip[aria-pressed="true"] {{ background: var(--brand-soft); border-color: var(--brand-1); color: var(--brand-1); font-weight: 600; }}
.chip.blue[aria-pressed="true"] {{ background: var(--blue-soft); border-color: var(--blue-1); color: var(--blue-1); }}

.reset-btn {{ display: inline-flex; align-items: center; justify-content: center; gap: 6px; width: 100%; margin-top: 10px; padding: 6px 12px; border: 1px solid var(--divider); border-radius: 8px; font-size: 12.5px; font-weight: 500; color: var(--t2); background: var(--bg-elv); transition: all .2s; }}
.reset-btn:hover {{ border-color: var(--brand-1); color: var(--brand-1); }}

.backdrop {{ display: none; }}

/* 主内容区 */
.content {{ padding: calc(var(--nav-h) + 36px) 36px 96px calc(var(--side-w) + 36px); min-height: 100vh; }}
.main-wrap {{ max-width: 860px; margin: 0 auto; }}

/* Hero 说明 */
.hero {{ margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid var(--divider); }}
.hero-tag {{ font-size: 12px; letter-spacing: 0.12em; color: var(--brand-1); font-weight: 700; margin-bottom: 8px; text-transform: uppercase; }}
.hero h1 {{ font-family: var(--font-serif); font-size: 32px; line-height: 1.25; font-weight: 600; margin: 0 0 10px; color: var(--t1); }}
.hero p {{ margin: 0 0 8px; color: var(--t2); font-size: 15.5px; line-height: 1.6; }}
.hero-stats {{ display: flex; flex-wrap: wrap; gap: 14px; font-size: 13px; color: var(--t3); margin-top: 12px; }}
.hero-stats span b {{ color: var(--brand-1); font-weight: 600; }}

/* 状态栏 */
.toolbar-state {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; font-size: 13.5px; color: var(--t2); }}
.toggle-all {{ font-size: 13px; color: var(--brand-1); }}
.toggle-all:hover {{ text-decoration: underline; }}

/* 章节大分割 */
.sec-heading {{ margin: 36px 0 16px; padding-top: 16px; border-top: 2px solid var(--divider); scroll-margin-top: calc(var(--nav-h) + 16px); }}
.sec-heading h2 {{ font-family: var(--font-serif); font-size: 21px; margin: 0 0 4px; color: var(--t1); font-weight: 600; }}
.sec-heading span {{ font-size: 13px; color: var(--t3); }}

/* 卡片 */
.card-list {{ display: flex; flex-direction: column; gap: 18px; }}
.card {{ background: var(--bg-elv); border: 1px solid var(--divider); border-radius: 12px; padding: 22px 24px; box-shadow: var(--shadow); transition: border-color .2s, box-shadow .2s; scroll-margin-top: calc(var(--nav-h) + 18px); position: relative; }}
.card:hover {{ border-color: var(--brand-border); }}
.card.flash {{ animation: xflash 1.8s ease-out; }}
@keyframes xflash {{ 0%, 35% {{ background: var(--brand-soft); border-color: var(--brand-1); }} 100% {{ background: var(--bg-elv); }} }}

.card-top {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 10px; }}
.card-num {{ font-family: var(--mono); font-size: 13px; font-weight: 600; color: var(--brand-1); background: var(--brand-soft); padding: 2px 7px; border-radius: 4px; white-space: nowrap; }}
.card-tags {{ display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }}
.tag-badge {{ font-size: 11.5px; padding: 1px 7px; border-radius: 4px; background: var(--bg-mute); color: var(--t2); line-height: 16px; }}
.tag-badge.scene {{ background: var(--green-soft); color: var(--green-1); }}
.tag-badge.person {{ background: var(--blue-soft); color: var(--blue-1); }}

.card-title {{ font-size: 19px; line-height: 1.45; font-weight: 600; color: var(--t1); margin: 0 0 12px; }}
.card-title a {{ color: inherit; }}
.card-title a:hover {{ color: var(--brand-1); text-decoration: none; }}

/* 遇到的情况 */
.field-situation {{ background: var(--bg-mute); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 13.5px; color: var(--t2); line-height: 1.6; display: flex; gap: 8px; }}
.field-situation .lbl {{ flex: none; font-weight: 600; color: var(--t1); }}

/* 判断关键 */
.field-judgment {{ font-size: 14px; color: var(--t1); margin-bottom: 12px; line-height: 1.65; }}
.field-judgment b {{ color: var(--brand-1); font-weight: 600; }}

/* 可以怎么说（核心话术台词块） */
.field-say {{ background: var(--brand-soft); border-left: 3.5px solid var(--brand-1); border-radius: 8px; padding: 12px 14px; margin: 12px 0 14px; position: relative; }}
.say-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
.say-label {{ font-size: 12.5px; font-weight: 700; color: var(--brand-1); letter-spacing: 0.05em; display: flex; align-items: center; gap: 5px; }}
.say-copy-btn {{ font-size: 12px; color: var(--brand-1); background: var(--bg-elv); border: 1px solid var(--brand-border); padding: 3px 9px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px; transition: all .15s; }}
.say-copy-btn:hover {{ background: var(--brand-1); color: #fff; }}
.say-copy-btn svg {{ width: 13px; height: 13px; fill: currentColor; }}
.say-text {{ font-size: 15px; line-height: 1.7; color: var(--t1); font-weight: 500; font-family: var(--font); margin: 0; white-space: pre-line; }}

/* 先做什么 & 准备 */
.field-action {{ font-size: 14px; color: var(--t1); margin-bottom: 12px; line-height: 1.65; }}
.field-action b {{ font-weight: 600; color: var(--green-1); }}

/* 折叠扩展部分 */
.card-details {{ margin-top: 10px; border-top: 1px dashed var(--divider); padding-top: 10px; }}
.card-details summary {{ font-size: 13px; color: var(--brand-1); cursor: pointer; user-select: none; padding: 4px 0; font-weight: 500; display: inline-flex; align-items: center; gap: 5px; }}
.card-details summary:hover {{ text-decoration: underline; }}
.details-body {{ padding-top: 10px; font-size: 13.5px; line-height: 1.7; color: var(--t2); display: flex; flex-direction: column; gap: 10px; }}
.detail-row b {{ color: var(--t1); font-weight: 600; display: inline; }}
.branch-block {{ background: var(--bg-mute); border-radius: 6px; padding: 8px 12px; font-size: 13px; margin: 4px 0; }}
.branch-block b {{ color: var(--brand-1); }}

/* 交叉引用浮动小标签 */
.xref {{ color: var(--brand-1); cursor: pointer; border-bottom: 1px dashed currentColor; padding-bottom: 1px; }}
.xref:hover {{ color: var(--brand-2); border-bottom-style: solid; }}
#xref-pop {{ position: absolute; z-index: 100; width: min(440px, calc(100vw - 28px)); background: var(--bg-elv); border: 1px solid var(--divider); border-radius: 10px; box-shadow: var(--shadow); padding: 14px 16px; font-size: 13.5px; line-height: 1.65; display: none; }}
#xref-pop .xp-h {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 6px; font-weight: 600; color: var(--t1); }}
#xref-pop .xp-action {{ font-size: 13px; color: var(--t2); }}
#xref-pop .xp-say {{ margin-top: 8px; background: var(--brand-soft); border-left: 2px solid var(--brand-1); padding: 6px 10px; border-radius: 4px; font-size: 13px; color: var(--t1); }}

/* Toast */
.toast {{ position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px); opacity: 0; pointer-events: none; background: #141413; color: #fff; font-size: 13px; padding: 9px 18px; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.25); z-index: 200; transition: all .25s ease; }}
html.dark .toast {{ background: #faf9f5; color: #141413; }}
.toast.show {{ transform: translateX(-50%) translateY(0); opacity: 1; }}

/* 空状态 */
.empty-box {{ text-align: center; padding: 64px 20px; background: var(--bg-elv); border: 1px dashed var(--divider); border-radius: 12px; margin-top: 20px; }}
.empty-box h3 {{ font-size: 18px; margin: 0 0 8px; color: var(--t1); }}
.empty-box p {{ font-size: 14px; color: var(--t3); margin: 0 0 16px; }}

/* 响应式 */
@media (max-width: 900px) {{
  :root {{ --side-w: 0px; }}
  .sidebar {{ transform: translateX(-100%); transition: transform .25s ease; width: 280px; z-index: 50; box-shadow: 0 0 30px rgba(0,0,0,.2); }}
  .sidebar.open {{ transform: translateX(0); }}
  .backdrop.open {{ display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 45; }}
  .content {{ padding-left: 20px; padding-right: 20px; }}
  .menu-btn {{ display: grid; }}
  .nav-in {{ padding: 0 16px; }}
  .nav-links {{ display: none; }}
  .search {{ max-width: none; }}
}}

@media (max-width: 640px) {{
  .nav-in {{ padding: 0 10px; gap: 8px; }}
  .title .nav-badge {{ display: none; }}
  .search kbd {{ display: none; }}
  .search input {{ height: 34px; padding: 0 10px 0 32px; font-size: 13px; }}
  .search svg {{ left: 9px; width: 14px; height: 14px; }}
  .menu-btn {{ width: 34px; height: 34px; }}
  .content {{ padding-left: 12px; padding-right: 12px; }}
  .hero {{ margin-bottom: 18px; padding-bottom: 14px; }}
  .hero h1 {{ font-size: 22px; line-height: 1.3; }}
  .hero p {{ font-size: 13.5px; }}
  .hero-stats {{ gap: 8px 12px; font-size: 12px; }}
  .card {{ padding: 14px 14px; border-radius: 10px; }}
  .card-top {{ gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }}
  .card-title {{ font-size: 16px; line-height: 1.4; margin: 0 0 10px; }}
  .field-situation {{ padding: 8px 10px; font-size: 12.5px; }}
  .field-judgment {{ font-size: 13px; line-height: 1.6; }}
  .details-body {{ font-size: 13px; }}
}}

@media (max-width: 440px) {{
  .title span:not(.logo) {{ font-size: 15px; }}
  .switch {{ width: 36px; height: 20px; }}
  .switch .knob {{ width: 16px; height: 16px; }}
  html.dark .switch .knob {{ transform: translateX(16px); }}
}}
</style>
</head>
<body>

<!-- 顶部导航 -->
<header class="nav">
  <div class="nav-in">
    <button class="menu-btn" id="menu-btn" aria-label="打开侧边导航">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <a class="title" href="./">
      <div class="logo">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.2L4 17.2V4h16v12z"/></svg>
      </div>
      人情世故指南
      <span class="nav-badge">77条</span>
    </a>

    <div class="search">
      <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input id="q" type="search" placeholder="输入关键词、场景、条号如 1.2..." autocomplete="off">
      <kbd>/</kbd>
    </div>

    <div class="nav-links">
      <a class="special" href="https://rensheng.21212121.xyz/" target="_blank" rel="noopener">高性价比人生 ↗</a>
      <a href="https://github.com/xiaobai5211314/HowToGetAlong" target="_blank" rel="noopener">GitHub ↗</a>
      <a href="阅读全文.html">阅读全文</a>
    </div>

    <button class="switch" id="theme-btn" aria-label="切换浅色/暗黑主题" title="切换浅色/暗黑主题">
      <div class="knob">
        <svg class="sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <svg class="moon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
    </button>
  </div>
</header>

<div class="backdrop" id="backdrop"></div>

<!-- 左侧边栏 -->
<aside class="sidebar" id="sidebar">
  <div class="group">
    <div class="gt">
      <span>章节索引</span>
      <small id="chap-count">10 节</small>
    </div>
    <div class="sec-links" id="sec-list">
      <button class="sec-link all" data-sec="" aria-pressed="true">
        <span>全部章节</span>
        <i id="all-count">77</i>
      </button>
      <!-- 动态生成章节列表 -->
    </div>
  </div>

  <div class="group">
    <div class="gt">
      <span>按场景筛选</span>
      <small>多选</small>
    </div>
    <div class="chips" id="scene-chips">
      <!-- 动态生成场景 -->
    </div>
  </div>

  <div class="group">
    <div class="gt">
      <span>按对象筛选</span>
      <small>多选</small>
    </div>
    <div class="chips" id="person-chips">
      <!-- 动态生成对象 -->
    </div>
  </div>

  <div class="group">
    <button class="reset-btn" id="reset-all">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
      重置所有筛选
    </button>
  </div>
  
  <div class="group" style="font-size:12.5px; color:var(--t3); line-height:1.6;">
    <p style="margin:0 0 6px;">💡 <b>提示：</b>按 <kbd style="font-family:var(--mono); border:1px solid var(--divider); padding:1px 4px; border-radius:3px;">/</kbd> 键可快速聚焦搜索框。点击台词卡片右上角可一键复制表达。</p>
    <p style="margin:0;"><a href="https://rensheng.21212121.xyz/" target="_blank" rel="noopener">高性价比人生指南 ↗</a> · <a href="https://github.com/xiaobai5211314/HowToGetAlong" target="_blank" rel="noopener">GitHub 源码</a></p>
  </div>
</aside>

<!-- 主内容区 -->
<main class="content">
  <div class="main-wrap">
    <div class="hero">
      <div class="hero-tag">PRACTICAL GUIDE · EVIDENCE & EXPERIENCE</div>
      <h1>人情世故指南</h1>
      <p>面向大学生与职场新人的处世相处指南：讲清怎么做、怎么说，以及可能付出什么代价。</p>
      <p style="font-size:13.5px; color:var(--t3);">纯净无广告 · 聚焦实际情境与示例表达 · 不搞动机推测与人设空话</p>
      <div class="hero-stats">
        <span><b>10</b> 个核心章节</span>
        <span><b>77</b> 个实战场景</span>
        <span><b>100%</b> 结构化解析</span>
        <span>已收录 <b>300+</b> 句参考表达</span>
      </div>
    </div>

    <div class="toolbar-state">
      <span id="result-summary">正在展示全部 77 条建议</span>
      <button class="toggle-all" id="toggle-details-btn">展开所有细节</button>
    </div>

    <!-- 列表容器 -->
    <div class="card-list" id="cards-container"></div>

    <div class="empty-box" id="empty-state" hidden>
      <h3>没有找到匹配的条目</h3>
      <p>试试更换关键词、清除部分场景/对象筛选，或者点击下方按钮重置。</p>
      <button class="reset-btn" id="empty-reset" style="display:inline-flex; width:auto;">重置筛选</button>
    </div>
  </div>
</main>

<!-- 交叉引用预览弹窗 -->
<div id="xref-pop">
  <div class="xp-h">
    <span class="xp-title">条目标题</span>
    <span class="xp-id">1.1</span>
  </div>
  <div class="xp-action">先做什么内容</div>
  <div class="xp-say">可以怎么说</div>
</div>

<!-- 提示 Toast -->
<div class="toast" id="toast">已复制</div>

<!-- 完整内嵌语料 -->
<script id="corpus" type="application/json">{corpus_json}</script>

<script>
(function(){{
  // 数据与状态
  let CORPUS = null;
  try {{
    CORPUS = JSON.parse(document.getElementById('corpus').textContent);
  }} catch(e) {{
    console.error('Failed to parse corpus', e);
  }}
  
  const state = {{
    q: '',
    sec: '', // 章节（单选，空表示全部）
    scenes: new Set(),
    persons: new Set()
  }};

  const ID_MAP = new Map();
  if (CORPUS && CORPUS.entries) {{
    for (const e of CORPUS.entries) {{
      ID_MAP.set(e.id, e);
    }}
  }}

  // DOM 元素
  const qInput = document.getElementById('q');
  const secList = document.getElementById('sec-list');
  const sceneChips = document.getElementById('scene-chips');
  const personChips = document.getElementById('person-chips');
  const cardsContainer = document.getElementById('cards-container');
  const emptyState = document.getElementById('empty-state');
  const resultSummary = document.getElementById('result-summary');
  const toggleDetailsBtn = document.getElementById('toggle-details-btn');
  const resetAllBtn = document.getElementById('reset-all');
  const emptyResetBtn = document.getElementById('empty-reset');
  const themeBtn = document.getElementById('theme-btn');
  const menuBtn = document.getElementById('menu-btn');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('backdrop');
  const toast = document.getElementById('toast');
  const xrefPop = document.getElementById('xref-pop');

  let toastTimer = null;
  function showToast(msg) {{
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
  }}

  // 主题切换
  themeBtn.addEventListener('click', () => {{
    const isDark = document.documentElement.classList.toggle('dark');
    try {{ localStorage.setItem('theme', isDark ? 'dark' : 'light'); }} catch(e){{}}
  }});

  // 移动端菜单
  function toggleMenu(open) {{
    sidebar.classList.toggle('open', open);
    backdrop.classList.toggle('open', open);
  }}
  menuBtn.addEventListener('click', () => toggleMenu(true));
  backdrop.addEventListener('click', () => toggleMenu(false));

  // 快捷键 / 聚焦
  document.addEventListener('keydown', (e) => {{
    if (e.key === '/' && document.activeElement !== qInput) {{
      e.preventDefault();
      qInput.focus();
      qInput.select();
    }} else if (e.key === 'Escape') {{
      qInput.blur();
      toggleMenu(false);
      xrefPop.style.display = 'none';
    }}
  }});

  // 渲染侧边栏
  function renderSidebar() {{
    if (!CORPUS) return;
    
    // 渲染章节列表
    let chapHtml = '<button class="sec-link all" data-sec="" aria-pressed="' + (state.sec === '' ? 'true' : 'false') + '"><span>全部章节</span><i>' + CORPUS.entries.length + '</i></button>';
    for (const c of CORPUS.chapters) {{
      const on = state.sec === String(c.sec);
      chapHtml += `
        <div class="sec-item">
          <div class="sec-link ${{on ? 'open' : ''}}" data-sec="${{c.sec}}" aria-pressed="${{on}}">
            <span style="flex:1;">${{c.sec}}. ${{escapeHtml(c.title)}}</span>
            <i>${{c.count}}</i>
            <button class="fold" type="button" aria-label="展开目录" data-fold="${{c.sec}}">
              <svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
            </button>
          </div>
          <div class="toc-sub" id="toc-sec-${{c.sec}}" ${{on ? '' : 'hidden'}}>
            ${{c.items.map(it => `<a href="#e-${{c.sec}}-${{it.n}}" data-nav="${{it.id}}"><i>${{it.id}}</i><span>${{escapeHtml(it.title)}}</span></a>`).join('')}}
          </div>
        </div>
      `;
    }}
    secList.innerHTML = chapHtml;

    // 渲染场景 Chips
    const scenes = {json.dumps(scenes, ensure_ascii=False)};
    sceneChips.innerHTML = scenes.map(s => 
      `<button class="chip" data-scene="${{s}}" aria-pressed="${{state.scenes.has(s)}}">${{s}}</button>`
    ).join('');

    // 渲染对象 Chips
    const persons = {json.dumps(persons, ensure_ascii=False)};
    personChips.innerHTML = persons.map(p => 
      `<button class="chip blue" data-person="${{p}}" aria-pressed="${{state.persons.has(p)}}">${{p}}</button>`
    ).join('');
  }}

  // 转义 HTML
  function escapeHtml(str) {{
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }}

  // 格式化文本中的交叉引用：见 1.2、见 2.4 等
  function formatXrefs(text) {{
    if (!text) return '';
    let res = escapeHtml(text);
    res = res.replace(/见\s*(\d+\.\d+)(?:\s*（([^）]+)）)?/g, (m, id, hint) => {{
      const target = ID_MAP.get(id);
      const title = hint || (target ? target.title : '');
      return `<span class="xref" data-ref="${{id}}" title="点击预览 ${{id}} ${{escapeHtml(title)}}">见 ${{id}}${{title ? `（${{escapeHtml(title)}}）` : ''}}</span>`;
    }});
    return res;
  }}

  // 渲染卡片
  let allCardsHtml = '';
  function buildCards() {{
    if (!CORPUS) return;
    const cards = [];
    let currentSec = null;

    for (const e of CORPUS.entries) {{
      if (e.sec !== currentSec) {{
        currentSec = e.sec;
        const chap = CORPUS.chapters.find(c => c.sec === currentSec);
        cards.push(`
          <div class="sec-heading" id="sec-head-${{currentSec}}">
            <h2>第 ${{currentSec}} 章 · ${{escapeHtml(chap ? chap.title : '')}}</h2>
            <span>共 ${{chap ? chap.count : 0}} 个情境条目</span>
          </div>
        `);
      }}

      const branchesHtml = e.branches && e.branches.length ? `
        <div class="detail-row">
          <b>分支应对：</b>
          ${{e.branches.map(b => `
            <div class="branch-block">
              <b>${{escapeHtml(b.label)}}：</b>${{formatXrefs(b.text)}}
            </div>
          `).join('')}}
        </div>
      ` : '';

      const contextsHtml = e.contexts ? `<div class="detail-row"><b>分情境处理：</b>${{formatXrefs(e.contexts)}}</div>` : '';
      const prepHtml = e.preparation ? `<div class="detail-row"><b>行动前准备：</b>${{formatXrefs(e.preparation)}}</div>` : '';
      const costHtml = e.cost ? `<div class="detail-row"><b>花掉什么：</b>${{formatXrefs(e.cost)}}</div>` : '';
      const gainHtml = e.gain ? `<div class="detail-row"><b>可能换回什么：</b>${{formatXrefs(e.gain)}}</div>` : '';
      const changeHtml = e.change ? `<div class="detail-row"><b>何时换办法：</b>${{formatXrefs(e.change)}}</div>` : '';
      const excHtml = e.exception ? `<div class="detail-row"><b>例外与代价：</b>${{formatXrefs(e.exception)}}</div>` : '';
      const basisHtml = e.basis ? `<div class="detail-row"><b>依据：</b>${{formatXrefs(e.basis)}}</div>` : '';
      const relHtml = e.related ? `<div class="detail-row"><b>相关条目：</b>${{formatXrefs(e.related)}}</div>` : '';

      cards.push(`
        <article class="card" id="e-${{e.sec}}-${{e.n}}" data-id="${{e.id}}" data-sec="${{e.sec}}">
          <div class="card-top">
            <a class="card-num" href="#e-${{e.sec}}-${{e.n}}" title="点击复制直链">${{e.id}} 🔗</a>
            <div class="card-tags">
              ${{e.tags.scene.map(s => `<span class="tag-badge scene">${{s}}</span>`).join('')}}
              ${{e.tags.person.map(p => `<span class="tag-badge person">${{p}}</span>`).join('')}}
              ${{e.tags.topic.map(t => `<span class="tag-badge">${{t}}</span>`).join('')}}
            </div>
          </div>

          <h3 class="card-title">
            <a href="#e-${{e.sec}}-${{e.n}}">${{escapeHtml(e.title)}}</a>
          </h3>

          ${{e.situation ? `
            <div class="field-situation">
              <span class="lbl">遇到的情况</span>
              <span>${{formatXrefs(e.situation)}}</span>
            </div>
          ` : ''}}

          ${{e.judgment ? `
            <div class="field-judgment">
              <b>判断关键：</b>${{formatXrefs(e.judgment)}}
            </div>
          ` : ''}}

          ${{e.say ? `
            <div class="field-say">
              <div class="say-header">
                <span class="say-label">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V3c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"/></svg>
                  可以怎么说（参考表达）
                </span>
                <button class="say-copy-btn" type="button" data-copy="${{escapeHtml(e.say)}}">
                  <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                  复制表达
                </button>
              </div>
              <p class="say-text">${{escapeHtml(e.say)}}</p>
            </div>
          ` : ''}}

          ${{e.action ? `
            <div class="field-action">
              <b>先做什么：</b>${{formatXrefs(e.action)}}
            </div>
          ` : ''}}

          <details class="card-details">
            <summary>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
              查看准备、不同情境、分支应对与代价
            </summary>
            <div class="details-body">
              ${{prepHtml}}
              ${{contextsHtml}}
              ${{costHtml}}
              ${{gainHtml}}
              ${{branchesHtml}}
              ${{changeHtml}}
              ${{excHtml}}
              ${{basisHtml}}
              ${{relHtml}}
            </div>
          </details>
        </article>
      `);
    }}

    cardsContainer.innerHTML = cards.join('');
  }}

  // 筛选核心
  function applyFilter() {{
    const q = state.q.toLowerCase().trim();
    const sec = state.sec;
    const scenes = state.scenes;
    const persons = state.persons;

    const tokens = q ? q.split(/\s+/).filter(Boolean) : [];
    let matchCount = 0;

    const cards = cardsContainer.querySelectorAll('.card');
    const headings = cardsContainer.querySelectorAll('.sec-heading');

    const secVisibleMap = new Map();

    for (const card of cards) {{
      const id = card.dataset.id;
      const entry = ID_MAP.get(id);
      if (!entry) continue;

      let ok = true;

      // 章节筛选
      if (sec && String(entry.sec) !== sec) {{
        ok = false;
      }}

      // 场景筛选 (只要包含所选场景中的任一个即符合，或者全包含)
      if (ok && scenes.size > 0) {{
        let hit = false;
        for (const s of scenes) {{
          if (entry.tags.scene.includes(s)) {{ hit = true; break; }}
        }}
        if (!hit) ok = false;
      }}

      // 对象筛选
      if (ok && persons.size > 0) {{
        let hit = false;
        for (const p of persons) {{
          if (entry.tags.person.includes(p)) {{ hit = true; break; }}
        }}
        if (!hit) ok = false;
      }}

      // 关键词搜索
      if (ok && tokens.length > 0) {{
        for (const t of tokens) {{
          if (!entry.hay.includes(t)) {{ ok = false; break; }}
        }}
      }}

      card.hidden = !ok;
      if (ok) {{
        matchCount++;
        secVisibleMap.set(entry.sec, (secVisibleMap.get(entry.sec) || 0) + 1);
      }}
    }}

    // 控制章节大标题的显隐
    for (const h of headings) {{
      const secNum = parseInt(h.id.replace('sec-head-', ''));
      h.hidden = !secVisibleMap.has(secNum);
    }}

    // 更新状态栏与空提示
    resultSummary.textContent = tokens.length || sec || scenes.size || persons.size
      ? `筛选匹配结果：共 ${{matchCount}} 条场景建议`
      : `正在展示全部 ${{matchCount}} 条建议`;

    emptyState.hidden = matchCount !== 0;

    // 更新 URL hash 或 query，方便分享
    syncUrl();
  }}

  function syncUrl() {{
    const params = new URLSearchParams();
    if (state.q) params.set('q', state.q);
    if (state.sec) params.set('sec', state.sec);
    if (state.scenes.size) params.set('scenes', Array.from(state.scenes).join(','));
    if (state.persons.size) params.set('persons', Array.from(state.persons).join(','));
    const str = params.toString();
    const newUrl = location.pathname + (str ? '?' + str : '') + location.hash;
    history.replaceState(null, '', newUrl);
  }}

  function readUrl() {{
    const params = new URLSearchParams(location.search);
    if (params.has('q')) {{
      state.q = params.get('q');
      qInput.value = state.q;
    }}
    if (params.has('sec')) {{
      state.sec = params.get('sec');
    }}
    if (params.has('scenes')) {{
      params.get('scenes').split(',').filter(Boolean).forEach(s => state.scenes.add(s));
    }}
    if (params.has('persons')) {{
      params.get('persons').split(',').filter(Boolean).forEach(p => state.persons.add(p));
    }}
  }}

  // 事件监听绑定
  function bindEvents() {{
    // 搜索输入（防抖）
    let searchTimer = null;
    qInput.addEventListener('input', () => {{
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {{
        state.q = qInput.value;
        applyFilter();
      }}, 100);
    }});

    // 章节点击
    secList.addEventListener('click', (e) => {{
      const foldBtn = e.target.closest('[data-fold]');
      if (foldBtn) {{
        const secNum = foldBtn.dataset.fold;
        const sub = document.getElementById(`toc-sec-${{secNum}}`);
        const item = foldBtn.closest('.sec-link');
        if (sub) {{
          sub.hidden = !sub.hidden;
          item.classList.toggle('open', !sub.hidden);
        }}
        return;
      }}

      const btn = e.target.closest('.sec-link');
      if (btn) {{
        const s = btn.dataset.sec;
        state.sec = s;
        // 更新按钮状态
        secList.querySelectorAll('.sec-link').forEach(b => {{
          b.setAttribute('aria-pressed', b.dataset.sec === s ? 'true' : 'false');
        }});
        applyFilter();
        // 手机端自动关抽屉
        if (window.innerWidth <= 900) toggleMenu(false);
      }}
    }});

    // 场景 Chips
    sceneChips.addEventListener('click', (e) => {{
      const btn = e.target.closest('[data-scene]');
      if (btn) {{
        const s = btn.dataset.scene;
        if (state.scenes.has(s)) state.scenes.delete(s);
        else state.scenes.add(s);
        btn.setAttribute('aria-pressed', state.scenes.has(s) ? 'true' : 'false');
        applyFilter();
      }}
    }});

    // 对象 Chips
    personChips.addEventListener('click', (e) => {{
      const btn = e.target.closest('[data-person]');
      if (btn) {{
        const p = btn.dataset.person;
        if (state.persons.has(p)) state.persons.delete(p);
        else state.persons.add(p);
        btn.setAttribute('aria-pressed', state.persons.has(p) ? 'true' : 'false');
        applyFilter();
      }}
    }});

    // 重置
    function resetAll() {{
      state.q = '';
      qInput.value = '';
      state.sec = '';
      state.scenes.clear();
      state.persons.clear();

      secList.querySelectorAll('.sec-link').forEach(b => {{
        b.setAttribute('aria-pressed', b.dataset.sec === '' ? 'true' : 'false');
      }});
      sceneChips.querySelectorAll('.chip').forEach(b => b.setAttribute('aria-pressed', 'false'));
      personChips.querySelectorAll('.chip').forEach(b => b.setAttribute('aria-pressed', 'false'));

      applyFilter();
      showToast('已重置所有筛选');
    }}
    resetAllBtn.addEventListener('click', resetAll);
    emptyResetBtn.addEventListener('click', resetAll);

    // 全部展开/折叠
    let detailsOpened = false;
    toggleDetailsBtn.addEventListener('click', () => {{
      detailsOpened = !detailsOpened;
      document.querySelectorAll('.card-details').forEach(d => d.open = detailsOpened);
      toggleDetailsBtn.textContent = detailsOpened ? '收起所有细节' : '展开所有细节';
    }});

    // 一键复制表达
    document.addEventListener('click', async (e) => {{
      const copyBtn = e.target.closest('.say-copy-btn');
      if (copyBtn) {{
        const text = copyBtn.dataset.copy;
        try {{
          await navigator.clipboard.writeText(text);
          showToast('已复制示例表达 ✨');
        }} catch(err) {{
          showToast('复制失败，请手动选取文字');
        }}
      }}
    }});

    // 点击条号复制直链
    document.addEventListener('click', async (e) => {{
      const numLink = e.target.closest('.card-num');
      if (numLink) {{
        e.preventDefault();
        const hash = numLink.getAttribute('href');
        const fullUrl = location.origin + location.pathname + hash;
        try {{
          await navigator.clipboard.writeText(fullUrl);
          showToast('已复制条目直链链接 🔗');
          location.hash = hash;
        }} catch(err) {{
          location.hash = hash;
        }}
      }}
    }});

    // 交叉引用悬停/点击
    document.addEventListener('click', (e) => {{
      const xr = e.target.closest('.xref');
      if (xr) {{
        const refId = xr.dataset.ref;
        const target = ID_MAP.get(refId);
        if (!target) return;

        // 如果在可视区域内，先尝试浮窗提示
        const rect = xr.getBoundingClientRect();
        xrefPop.querySelector('.xp-id').textContent = target.id;
        xrefPop.querySelector('.xp-title').textContent = target.title;
        xrefPop.querySelector('.xp-action').textContent = target.action || target.judgment || '';
        xrefPop.querySelector('.xp-say').textContent = target.say || '';
        xrefPop.querySelector('.xp-say').hidden = !target.say;

        xrefPop.style.display = 'block';
        const popW = Math.min(440, window.innerWidth - 28);
        let left = rect.left + window.scrollX;
        if (left + popW > window.innerWidth - 14) {{
          left = window.innerWidth - popW - 14;
        }}
        xrefPop.style.left = Math.max(14, left) + 'px';
        xrefPop.style.top = (rect.bottom + window.scrollY + 6) + 'px';
      }} else if (!e.target.closest('#xref-pop')) {{
        xrefPop.style.display = 'none';
      }}
    }});

    // 处理页面初始 hash 定位
    if (location.hash) {{
      setTimeout(() => {{
        const target = document.querySelector(location.hash);
        if (target) {{
          target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
          target.classList.add('flash');
        }}
      }}, 150);
    }}
  }}

  // 初始化
  renderSidebar();
  buildCards();
  readUrl();
  bindEvents();
  applyFilter();
}})();
</script>
</body>
</html>
'''
    return html_template

def main():
    print("开始解析人情世故指南正文...")
    chapters, entries, scenes, persons, topics = parse_book()
    print(f"成功解析 {len(chapters)} 个章节，{len(entries)} 个条目！")
    print(f"发现场景: {len(scenes)} 个，对象: {len(persons)} 个，主题: {len(topics)} 个。")
    
    html_content = render_html(chapters, entries, scenes, persons, topics)
    out_file = ROOT / 'index.html'
    out_file.write_text(html_content, encoding='utf-8')
    print(f"成功生成 Claude 官方 UI 主题检索页: {out_file} ({len(html_content)} 字节)")

if __name__ == '__main__':
    main()
