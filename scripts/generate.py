#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全球富豪家族财富传承新闻追踪系统 — 自动生成 index.html"""

import feedparser
import json
import re
import urllib.parse
import datetime
import time
from pathlib import Path
from collections import defaultdict

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
    print("✓ 翻译模块已启用")
except Exception as e:
    HAS_TRANSLATOR = False
    print(f"⚠ 翻译模块未启用: {e}")

ROOT = Path(__file__).resolve().parent.parent

# ── 国家颜色 ──────────────────────────────────────────────────────
COUNTRY_COLORS = {
    "中国内地": "#c62828",
    "香港":     "#ad1457",
    "澳门":     "#6a1b9a",
    "新加坡":   "#1565c0",
    "马来西亚": "#2e7d32",
    "印度尼西亚":"#00695c",
    "越南":     "#bf360c",
    "日本":     "#b71c1c",
    "美国":     "#0d47a1",
    "欧洲":     "#37474f",
    "中东":     "#e65100",
}

COUNTRY_ORDER = [
    "中国内地","香港","澳门","新加坡","马来西亚",
    "印度尼西亚","越南","日本","美国","欧洲","中东",
]

# ── 家族数据库（53个家族） ────────────────────────────────────────
FAMILIES = [

    # ═══════════════ 中国内地 ════════════════
    {"id":"wahaha","name":"娃哈哈集团（宗庆后家族）","country":"中国内地",
     "queries":["Wahaha Zong Qinghou trust inheritance lawsuit 2024 2025",
                "宗馥莉 遗产 信托 娃哈哈 香港"],
     "tags":["信托诉讼","非婚生子女","遗产执行"]},

    {"id":"dashang","name":"大商集团（牛钢家族）","country":"中国内地",
     "queries":["Dashang Group Niu Gang family inheritance equity dispute control",
                "大商集团 牛钢 股权 继承 控制权"],
     "tags":["股权代持","控制权纠纷"]},

    {"id":"longfor","name":"龙湖地产（吴亚军家族）","country":"中国内地",
     "queries":["Longfor Holdings Wu Yajun family trust divorce protection China",
                "吴亚军 龙湖 家族信托 离婚"],
     "tags":["双层家族信托","离婚保护","正面案例"]},

    {"id":"southbeauty","name":"俏江南（张兰家族）","country":"中国内地",
     "queries":["Zhang Lan South Beauty offshore trust creditor pierce veil",
                "张兰 俏江南 信托 债权人 击穿"],
     "tags":["信托被击穿","债务追索"]},

    {"id":"sany","name":"三一重工（梁稳根家族）","country":"中国内地",
     "queries":["SANY Heavy Industry Liang Wengen family succession governance",
                "梁稳根 三一重工 家族 接班 治理"],
     "tags":["企业传承","家族治理委员会"]},

    {"id":"shanshan","name":"杉杉集团（郑永刚家族）","country":"中国内地",
     "queries":["Shanshan Group Zheng Yonggang widow son control battle 2023 2024",
                "郑永刚 杉杉 遗孀 长子 控制权 争夺"],
     "tags":["遗产争夺","继室vs长子"]},

    # ═══════════════ 香港 ════════════════
    {"id":"kwok","name":"新鸿基地产（郭氏家族）","country":"香港",
     "queries":["Sun Hung Kai Properties Kwok family trust brothers dispute",
                "郭氏兄弟 新鸿基 信托 纠纷 郭老太"],
     "tags":["兄弟内斗","信托重组"]},

    {"id":"huo","name":"霍英东家族","country":"香港",
     "queries":["Huo Yingdong family estate Panyu South China lawsuit inheritance",
                "霍震宇 霍震寰 南沙 股权 遗产 诉讼"],
     "tags":["数十年遗产战","南沙项目"]},

    {"id":"stanley_ho","name":"赌王何鸿燊家族","country":"香港",
     "queries":["Stanley Ho family trust SJM casino estate four wives inheritance",
                "何鸿燊 家族信托 四房 澳博 分产"],
     "tags":["四房争产","多层信托架构"]},

    {"id":"great_eagle","name":"鹰君集团（罗鹰石家族）","country":"香港",
     "queries":["Great Eagle Holdings Lo Ying-shek HSBC trustee dispute remove",
                "鹰君集团 罗鹰石 汇丰信托 信托管理人 撤换"],
     "tags":["信托管理人争议","六子三女对立"]},

    {"id":"anita_mui","name":"梅艳芳家族","country":"香港",
     "queries":["Anita Mui testamentary trust mother lawsuit estate Hong Kong court",
                "梅艳芳 遗嘱信托 梅母 诉讼 推翻"],
     "tags":["防败家子信托","终身诉讼"]},

    {"id":"gaddi","name":"镛记酒家（甘氏家族）","country":"香港",
     "queries":["Yung Kee restaurant Kam family liquidation brothers dispute Hong Kong",
                "镛记酒家 甘氏兄弟 清盘 家族内耗"],
     "tags":["家族治理缺失","老字号分崩"]},

    # ═══════════════ 澳门 ════════════════
    {"id":"macau_gaming","name":"永利澳门 / 银河娱乐相关家族","country":"澳门",
     "queries":["Wynn Macau Galaxy Entertainment family trust inheritance offshore BVI",
                "澳门博彩 家族 离岸信托 继承 BVI 开曼"],
     "tags":["博彩业传承","跨境离岸架构"]},

    # ═══════════════ 新加坡 ════════════════
    {"id":"sg_hardware","name":"新加坡匿名硬件零售家族（高院案）","country":"新加坡",
     "queries":["Singapore High Court anonymous hardware billionaire estate undisclosed assets daughters 2026",
                "新加坡 高院 遗产 隐匿资产 女儿 执行人 2025 2026"],
     "tags":["1.5亿遗产尘封","资产追溯"]},

    {"id":"hongleong_sg","name":"丰隆集团（郭令明家族）","country":"新加坡",
     "queries":["Hong Leong Group Singapore Kwek Leng Beng family trust succession",
                "丰隆集团 郭令明 新加坡 家族信托 传承"],
     "tags":["兄弟分家","信托利益分歧"]},

    {"id":"tiger_balm","name":"虎标万金油（胡文虎家族）","country":"新加坡",
     "queries":["Tiger Balm Aw Boon Haw descendants trust inheritance Singapore tax",
                "虎标万金油 胡文虎 家族 信托 后代 税务"],
     "tags":["跨代信托稀释","税务管辖冲突"]},

    {"id":"uob","name":"大华银行（黄祖耀家族）","country":"新加坡",
     "queries":["United Overseas Bank Wee Cho Yaw family succession trust Singapore governance",
                "大华银行 黄祖耀 家族传承 信托 投票权"],
     "tags":["银行业传承","信托投票权锁定"]},

    {"id":"tan_kah_kee","name":"陈嘉庚家族后裔","country":"新加坡",
     "queries":["Tan Kah Kee family descendants charitable trust foundation lawsuit Singapore",
                "陈嘉庚 家族 慈善信托 后代 诉讼"],
     "tags":["慈善信托争议","历史遗留资产"]},

    # ═══════════════ 印度尼西亚 ════════════════
    {"id":"sinarmas","name":"金光集团（黄奕聪家族）","country":"印度尼西亚",
     "queries":["Sinar Mas Eka Tjipta Widjaja Freddy illegitimate heir inheritance lawsuit Indonesia",
                "金光集团 黄奕聪 Freddy Widjaja 非婚生 遗产 诉讼"],
     "tags":["非婚生子诉讼","千亿遗产争夺"]},

    {"id":"gudang_garam","name":"盐仓集团（蔡道行家族）","country":"印度尼西亚",
     "queries":["Gudang Garam Wonowidjojo family Indonesia tobacco inheritance CRS compliance",
                "盐仓集团 印尼 烟草 家族 海外资产 继承 CRS"],
     "tags":["跨国税务合规","CRS反洗钱"]},

    {"id":"salim","name":"三林集团（林绍良家族）","country":"印度尼西亚",
     "queries":["Salim Group Anthony Salim Liem Sioe Liong trust succession Indonesia First Pacific",
                "三林集团 林绍良 林逢生 信托 传承 政治关联"],
     "tags":["政治关联风险","双控股模式"]},

    {"id":"astra","name":"阿斯特拉（谢建隆家族）","country":"印度尼西亚",
     "queries":["Astra International Soeryadjaya family trust debt loss recovery Indonesia",
                "阿斯特拉 谢建隆 家族 债务危机 信托保护"],
     "tags":["债务危机失控","东山再起信托"]},

    {"id":"djarum","name":"针记集团（黄辉聪/黄辉祥家族）","country":"印度尼西亚",
     "queries":["Djarum Hartono Robert Michael family office BCA Indonesia succession wealth",
                "针记集团 黄辉聪 黄辉祥 家族办公室 BCA 印尼首富"],
     "tags":["家族办公室","资产多元化"]},

    # ═══════════════ 马来西亚 ════════════════
    {"id":"genting","name":"云顶集团（林高远/林国泰家族）","country":"马来西亚",
     "queries":["Genting Lim Kok Thay family inheritance lawsuit fraud Dikim Foundation 2025 2026",
                "云顶集团 林国泰 林高远 继承 诉讼 慈善基金会 遗嘱"],
     "tags":["5.22亿继承战","慈善基金会欺诈"]},

    {"id":"taib","name":"砂拉越CMS（泰益玛目家族）","country":"马来西亚",
     "queries":["Taib Mahmud Cahya Mata Sarawak CMS family estate inheritance 2024 2025 stepmother",
                "泰益玛目 砂拉越 CMS 遗产战 继母 股权转移"],
     "tags":["200亿遗产战","政治家族传承"]},

    {"id":"genting_lim_chet","name":"云顶长子（林致强分支）","country":"马来西亚",
     "queries":["Lim Chee Wah Genting family trust grandfather will manipulation Malaysia",
                "林致强 云顶 家族信托 遗嘱 受益权 操纵"],
     "tags":["长房受益权剥夺","信托操控"]},

    {"id":"ioi","name":"IOI集团（李深静家族）","country":"马来西亚",
     "queries":["IOI Group Lee Shin Cheng family trust palm oil succession Malaysia",
                "IOI集团 李深静 家族信托 棕榈油 传承"],
     "tags":["棕榈油帝国传承","信托锁定期"]},

    {"id":"publicbank","name":"大众银行（郑鸿标家族）","country":"马来西亚",
     "queries":["Public Bank Berhad Teh Hong Piow family trust succession Malaysia financial services act",
                "大众银行 郑鸿标 家族信托 金融服务法 持股限制"],
     "tags":["银行业合规危机","信托强制拆解"]},

    # ═══════════════ 越南 ════════════════
    {"id":"van_thinh_phat","name":"万盛发集团（张美兰家族）","country":"越南",
     "queries":["Truong My Lan Van Thinh Phat Vietnam fraud death sentence 2024 2025 asset freeze",
                "张美兰 万盛发 越南 死刑 资产冻结 洗钱"],
     "tags":["亚洲最大金融诈骗","死刑判决"]},

    {"id":"trung_nguyen","name":"中原咖啡（邓黎原武家族）","country":"越南",
     "queries":["Trung Nguyen coffee Dang Le Nguyen Vu Le Hoang Diep Thao divorce court Vietnam",
                "中原咖啡 邓黎原武 离婚 控股权 越南 诉讼"],
     "tags":["世纪离婚案","企业控权争夺"]},

    {"id":"tan_hiep_phat","name":"新协发集团（陈贵清家族）","country":"越南",
     "queries":["Tan Hiep Phat Tran Qui Thanh daughter arrested Vietnam money laundering",
                "新协发集团 陈贵清 女儿 逮捕 越南 洗钱 合规"],
     "tags":["洗钱指控","家族合规缺失"]},

    {"id":"dai_nam","name":"大南集团（黄威勇家族）","country":"越南",
     "queries":["Dai Nam Huynh Uy Dung Vietnam young son inheritance wife children",
                "大南集团 黄威勇 幼子 继承 前妻 子女 越南"],
     "tags":["幼子继承争议","前妻vs现妻"]},

    {"id":"khaisilk","name":"高丽丝绸（Khaisilk家族）","country":"越南",
     "queries":["Khaisilk Khai Vietnam silk fraud bankruptcy asset recovery creditor",
                "高丽丝绸 越南 欺诈 破产 资产追索 信托"],
     "tags":["欺诈破产","债权人追索"]},

    # ═══════════════ 日本 ════════════════
    {"id":"otsuka","name":"大塚家具（大塚胜久家族）","country":"日本",
     "queries":["Otsuka Katsuhisa Kumiko furniture company boardroom fight Japan takeover",
                "大塚家具 大塚胜久 久美子 父女 股东 夺权 董事会"],
     "tags":["父女反目夺权","品牌价值崩溃"]},

    {"id":"lotte","name":"乐天集团（辛格浩家族）","country":"日本",
     "queries":["Lotte Shin Kyuk-ho Dong-bin Dong-joo family trust succession Japan Korea battle",
                "乐天 辛格浩 辛东彬 辛东主 信托 两子夺嫡 日本"],
     "tags":["两子夺嫡","日韩跨境信托"]},

    {"id":"rohm","name":"罗姆半导体（佐藤研一郎家族）","country":"日本",
     "queries":["Rohm semiconductor Sato Kenichiro estate inheritance illegitimate charity foundation Japan",
                "罗姆半导体 佐藤研一郎 遗产 非婚生 慈善基金会 争夺"],
     "tags":["无婚生子遗产","多方争夺"]},

    {"id":"aoyama","name":"青山商事（洋服之青山）","country":"日本",
     "queries":["Aoyama Trading family office succession retail transformation Japan share buyback",
                "青山商事 洋服之青山 家族 资产配置 冲突 股份回购"],
     "tags":["代际战略冲突","强制股份回购"]},

    {"id":"nintendo","name":"任天堂（山内溥家族）","country":"日本",
     "queries":["Nintendo Yamauchi Hiroshi family estate inheritance tax Japan foundation stock",
                "任天堂 山内溥 遗产税 家族基金会 股权质押 传承"],
     "tags":["正面传承案例","遗产税规划"]},

    # ═══════════════ 美国 ════════════════
    {"id":"pritzker","name":"普利兹克家族（凯悦酒店）","country":"美国",
     "queries":["Pritzker family trust lawsuit Liesel Hyatt breach misappropriation",
                "普利兹克 家族信托 诉讼 莉泽 凯悦"],
     "tags":["信托资产挪用","19岁受益人诉父"]},

    {"id":"murdoch","name":"默多克家族（News Corp）","country":"美国",
     "queries":["Murdoch family trust irrevocable modification Lachlan James Nevada court 2024 2025",
                "默多克 家族信托 修改 不可撤销 拉克兰 投票权 2024"],
     "tags":["不可撤销信托争议","继承权剥夺"]},

    {"id":"sterling","name":"斯特林家族（洛杉矶快船队）","country":"美国",
     "queries":["Donald Shelly Sterling Clippers trust incapacity sale 2 billion",
                "斯特林 快船 信托 精神失能 出售"],
     "tags":["精神失能条款","信托单方控制"]},

    {"id":"koch","name":"科赫家族（Koch Industries）","country":"美国",
     "queries":["Koch brothers family trust lawsuit Charles David William Fred 20 years litigation",
                "科赫兄弟 家族信托 诉讼 内斗 私家侦探"],
     "tags":["兄弟20年内战","雇私家侦探"]},

    {"id":"getty","name":"保罗·盖蒂家族（Getty Oil）","country":"美国",
     "queries":["Getty family trust inheritance oil museum kidnapping estate lawsuit",
                "盖蒂 家族信托 遗产 绑架 割耳 诉讼"],
     "tags":["苛刻信托","家族悲剧连连"]},

    # ═══════════════ 欧洲 ════════════════
    {"id":"gucci","name":"古驰家族（Gucci - 意大利）","country":"欧洲",
     "queries":["Gucci family Maurizio murder estate inheritance governance Italy",
                "古驰 毛里齐奥 谋杀 遗产 家族治理"],
     "tags":["家族治理失控","姻亲风险极端案"]},

    {"id":"bettencourt","name":"贝当古·欧莱雅家族（法国）","country":"欧洲",
     "queries":["Bettencourt Meyers LOreal family trust incapacity artist France estate",
                "贝当古 欧莱雅 欺诈 监护权 女儿 信托"],
     "tags":["监护权争夺","十亿欧元骗局"]},

    {"id":"hermes_puech","name":"爱马仕·普伊奇家族（法国）","country":"欧洲",
     "queries":["Nicolas Puech Hermes gardener inheritance trust 13 billion lawsuit 2024 2025",
                "爱马仕 普伊奇 园丁 继承 信托 130亿 诉讼 2024"],
     "tags":["园丁继承案","130亿传承"]},

    {"id":"vw_family","name":"大众汽车·保时捷-皮耶希家族（德国）","country":"欧洲",
     "queries":["Porsche Piech family VW Volkswagen trust cross-shareholding succession Germany",
                "保时捷 皮耶希 大众 家族信托 交叉持股 传承"],
     "tags":["交叉持股信托","蛇吞象失败"]},

    {"id":"heineken","name":"海涅根家族（荷兰）","country":"欧洲",
     "queries":["Heineken family trust holding Netherlands succession governance",
                "海涅根 家族信托 控股 荷兰 双层架构"],
     "tags":["双层控股信托","正面防御案例"]},

    # ═══════════════ 中东 ════════════════
    {"id":"alwaleed","name":"阿尔瓦利德王子家族（沙特）","country":"中东",
     "queries":["Prince Alwaleed bin Talal Saudi Arabia family trust Ritz Carlton assets offshore",
                "阿尔瓦利德 王子 沙特 家族信托 利兹卡尔顿 反腐 开曼"],
     "tags":["主权风险","离岸架构冲突"]},

    {"id":"alghurair","name":"阿尔·古赖尔家族（迪拜）","country":"中东",
     "queries":["Al Ghurair family Dubai estate real estate bank inheritance arbitration",
                "古赖尔 家族 迪拜 遗产 银行 地产 仲裁"],
     "tags":["内部仲裁","数十亿资产重划"]},

    {"id":"alsayer","name":"阿尔·萨耶尔家族（科威特）","country":"中东",
     "queries":["Al Sayer family Kuwait succession family constitution governance",
                "萨耶尔 科威特 家族 宪章 传承 三四代争权"],
     "tags":["家族宪章引入","三四代争权"]},

    {"id":"binladen","name":"本·拉登集团家族（沙特）","country":"中东",
     "queries":["Saudi Binladen Group family inheritance estate reconstruction debt offshore",
                "本拉登 建筑集团 家族 遗产 继承人 资产冻结 重组"],
     "tags":["政治波折","数十继承人争产"]},

    {"id":"koc","name":"考奇家族（Koç Holding - 土耳其）","country":"中东",
     "queries":["Koc Holding family governance constitution Turkey three generations succession trust",
                "考奇 土耳其 家族治理 宪章 三代传承 信托"],
     "tags":["家族宪章典范","三代平稳传承"]},
]


# ─────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────

def is_mostly_chinese(text: str) -> bool:
    zh = len(re.findall(r'[一-鿿]', text))
    return zh > max(len(text.replace(' ', '')) * 0.2, 3)


def translate_zh(text: str) -> str:
    if not HAS_TRANSLATOR or is_mostly_chinese(text):
        return text
    try:
        time.sleep(0.25)
        result = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        return result or text
    except Exception:
        return text


def fetch_google_news(query: str, n: int = 6) -> list:
    url = (f"https://news.google.com/rss/search?"
           f"q={urllib.parse.quote(query)}&hl=en&gl=US&ceid=US:en")
    results = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:n]:
            dt = None
            if getattr(entry, 'published_parsed', None):
                try:
                    dt = datetime.datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            raw = entry.get('title', '').strip()
            # Strip trailing " - SourceName" appended by Google News
            title = re.sub(r'\s*[-–]\s*[^-–]{2,50}$', '', raw).strip() or raw

            source = ''
            try:
                source = entry.source.title
            except Exception:
                m = re.search(r'[-–]\s*([^-–]+)$', raw)
                if m:
                    source = m.group(1).strip()

            results.append({
                'title': title,
                'link': entry.get('link', '#'),
                'source': source,
                'date': dt.strftime('%Y-%m-%d') if dt else '',
                'date_raw': dt.isoformat() if dt else '0000',
            })
    except Exception as e:
        print(f"    ✗ 抓取失败: {e}")
    return results


def dedup(articles: list) -> list:
    seen, out = set(), []
    for a in articles:
        key = re.sub(r'\W', '', a['title'].lower())[:50]
        if key and key not in seen:
            seen.add(key)
            out.append(a)
    return out


def fetch_family_news(family: dict) -> list:
    all_arts = []
    for q in family['queries']:
        arts = fetch_google_news(q, n=5)
        all_arts.extend(arts)
        time.sleep(0.7)

    all_arts = dedup(all_arts)
    all_arts.sort(key=lambda x: x['date_raw'], reverse=True)
    all_arts = all_arts[:8]

    for art in all_arts:
        art['zh_title'] = translate_zh(art['title'])

    return all_arts


def esc(s) -> str:
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')


def sid(country: str) -> str:
    """Safe ASCII id from country name."""
    mapping = {
        "中国内地":"cn","香港":"hk","澳门":"mo","新加坡":"sg",
        "马来西亚":"my","印度尼西亚":"id","越南":"vn","日本":"jp",
        "美国":"us","欧洲":"eu","中东":"me",
    }
    return mapping.get(country, re.sub(r'\W','_', country))


# ─────────────────────────────────────────────────────────────
# HTML 生成
# ─────────────────────────────────────────────────────────────

def build_html(data: list, generated_at: str) -> str:
    total_arts = sum(len(d['articles']) for d in data)

    by_country = defaultdict(list)
    for item in data:
        by_country[item['family']['country']].append(item)

    countries = [c for c in COUNTRY_ORDER if c in by_country]
    countries += [c for c in by_country if c not in COUNTRY_ORDER]

    # ── Navigation ──
    nav_html = ''
    for c in countries:
        col = COUNTRY_COLORS.get(c, '#455a64')
        count = len(by_country[c])
        nav_html += (f'<button class="nav-btn" onclick="goto(\'{sid(c)}\')" '
                     f'style="--c:{col}">{esc(c)}'
                     f'<span class="nbadge">{count}</span></button>\n')

    # ── Country Sections ──
    sections_html = ''
    for c in countries:
        col = COUNTRY_COLORS.get(c, '#455a64')
        cid = sid(c)
        items = by_country[c]

        fams_html = ''
        for item in items:
            fam = item['family']
            arts = item['articles']

            tags_html = ''.join(
                f'<span class="tag">{esc(t)}</span>' for t in fam.get('tags', []))

            if arts:
                cards_html = ''
                for art in arts:
                    zh = art.get('zh_title', '') or art['title']
                    orig = art['title']
                    orig_block = (f'<div class="art-orig">{esc(orig)}</div>'
                                  if zh != orig and zh else '')
                    src_block = (f'<span class="art-src">{esc(art["source"])}</span>'
                                 if art.get('source') else '')
                    date_block = (f'<span class="art-date">{esc(art["date"])}</span>'
                                  if art.get('date') else '')
                    cards_html += f'''\
<a class="art-card" href="{esc(art['link'])}" target="_blank" rel="noopener noreferrer">
  <div class="art-zh">{esc(zh)}</div>
  {orig_block}
  <div class="art-foot">{src_block}{date_block}</div>
</a>'''
            else:
                cards_html = '<div class="no-news">暂无最新相关报道，请稍后再查</div>'

            fams_html += f'''\
<div class="fam-card" id="f-{esc(fam['id'])}">
  <div class="fam-hd" style="border-left-color:{col}">
    <div class="fam-name">{esc(fam['name'])}</div>
    <div class="fam-tags">{tags_html}</div>
  </div>
  <div class="fam-body">{cards_html}</div>
</div>'''

        sections_html += f'''\
<section class="country-sec" id="c-{cid}">
  <div class="country-bar" style="background:{col}">
    <span class="cbar-name">{esc(c)}</span>
    <span class="cbar-count">{len(items)} 个家族</span>
  </div>
  <div class="fam-grid">{fams_html}</div>
</section>'''

    # ── Full Page ──
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>全球富豪家族 · 财富传承新闻追踪</title>
<meta name="description" content="实时追踪全球53个超高净值家族的信托诉讼、遗产争夺、继承危机最新动态">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#f4f6f9;
  --card:#ffffff;
  --border:#e2e8f0;
  --border-hover:#b0bec5;
  --txt:#1a202c;
  --txt2:#4a5568;
  --txt3:#718096;
  --shadow:0 1px 4px rgba(0,0,0,0.06),0 2px 12px rgba(0,0,0,0.04);
  --shadow-hover:0 4px 20px rgba(0,0,0,0.10);
  --r:10px;
  --r-sm:6px;
}}
html{{scroll-behavior:smooth}}
body{{
  font-family:'Noto Sans SC','Inter',system-ui,sans-serif;
  background:var(--bg);color:var(--txt);line-height:1.65;
  font-size:15px;
}}

/* ── HEADER ── */
.site-header{{
  position:sticky;top:0;z-index:200;
  background:rgba(255,255,255,0.96);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);
  box-shadow:0 2px 20px rgba(0,0,0,0.05);
}}
.header-top{{
  max-width:1520px;margin:0 auto;padding:14px 24px 10px;
  display:flex;align-items:center;justify-content:space-between;gap:16px;
  flex-wrap:wrap;
}}
.site-title{{
  font-size:1.3rem;font-weight:700;letter-spacing:-.3px;
  background:linear-gradient(130deg,#1a202c 30%,#4a5568);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.site-sub{{
  font-size:0.75rem;color:var(--txt3);margin-top:3px;font-weight:300;
}}
.update-box{{text-align:right;flex-shrink:0;}}
.update-time{{font-size:0.82rem;color:var(--txt2);font-weight:500;}}
.update-freq{{
  display:inline-block;margin-top:4px;
  background:#ebf4ff;color:#2b6cb0;
  font-size:0.68rem;padding:2px 9px;border-radius:12px;font-weight:600;
  letter-spacing:.3px;
}}
.stat-chips{{
  display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;
}}
.stat-chip{{
  font-size:0.7rem;background:#f7fafc;border:1px solid var(--border);
  color:var(--txt3);padding:2px 9px;border-radius:10px;
}}

/* ── NAV ── */
.country-nav{{
  max-width:1520px;margin:0 auto;padding:6px 24px 12px;
  display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;
  align-items:center;
}}
.country-nav::-webkit-scrollbar{{display:none}}
.nav-btn{{
  --c:#455a64;
  flex-shrink:0;
  display:inline-flex;align-items:center;gap:5px;
  padding:5px 13px;border-radius:20px;
  border:1.5px solid var(--c);background:white;color:var(--c);
  font-size:0.78rem;font-weight:600;cursor:pointer;
  transition:all .18s ease;font-family:inherit;
  white-space:nowrap;
}}
.nav-btn:hover,.nav-btn.active{{
  background:var(--c);color:white;
  box-shadow:0 3px 10px rgba(0,0,0,0.13);
  transform:translateY(-1px);
}}
.nbadge{{
  background:var(--c);color:white;
  font-size:0.65rem;padding:1px 6px;border-radius:10px;
  transition:background .18s;
}}
.nav-btn:hover .nbadge,.nav-btn.active .nbadge{{background:rgba(255,255,255,.3)}}
.nav-top{{
  margin-left:auto;flex-shrink:0;
  padding:5px 12px;border-radius:20px;border:1.5px solid var(--border);
  background:white;color:var(--txt3);font-size:0.78rem;font-weight:500;
  cursor:pointer;transition:all .18s;font-family:inherit;
}}
.nav-top:hover{{border-color:var(--border-hover);color:var(--txt2);}}

/* ── MAIN ── */
main{{max-width:1520px;margin:0 auto;padding:24px 20px 64px;}}

/* ── COUNTRY SECTION ── */
.country-sec{{margin-bottom:36px;border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow);}}
.country-bar{{
  display:flex;align-items:center;justify-content:space-between;
  padding:11px 20px;color:white;
}}
.cbar-name{{font-size:1rem;font-weight:700;letter-spacing:.4px;}}
.cbar-count{{font-size:0.75rem;opacity:.85;background:rgba(255,255,255,.15);padding:2px 10px;border-radius:12px;}}

/* ── FAMILY GRID ── */
.fam-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(390px,1fr));
  gap:1px;background:var(--border);
}}

/* ── FAMILY CARD ── */
.fam-card{{background:var(--card);}}
.fam-hd{{
  padding:13px 16px 9px;
  border-left:4px solid #ddd;
  background:#fafbfe;
  border-bottom:1px solid var(--border);
}}
.fam-name{{font-size:0.88rem;font-weight:700;color:var(--txt);line-height:1.4;}}
.fam-tags{{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}}
.tag{{
  font-size:0.65rem;padding:2px 8px;border-radius:12px;
  background:#edf2ff;color:#3c4fa8;font-weight:600;letter-spacing:.2px;
}}
.fam-body{{padding:10px;display:flex;flex-direction:column;gap:7px;}}

/* ── ARTICLE CARD ── */
.art-card{{
  display:block;text-decoration:none;color:inherit;
  padding:10px 12px;border-radius:var(--r-sm);
  border:1px solid var(--border);background:white;
  transition:border-color .15s,box-shadow .15s,transform .15s;
}}
.art-card:hover{{
  border-color:var(--border-hover);
  box-shadow:var(--shadow-hover);
  transform:translateY(-1px);
}}
.art-zh{{
  font-size:0.85rem;font-weight:500;line-height:1.5;
  color:var(--txt);
}}
.art-orig{{
  font-size:0.72rem;color:var(--txt3);margin-top:4px;
  line-height:1.45;font-style:italic;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
}}
.art-foot{{
  display:flex;align-items:center;justify-content:space-between;
  margin-top:8px;gap:8px;
}}
.art-src{{
  font-size:0.67rem;color:var(--txt2);
  background:#f7f8fa;padding:2px 8px;border-radius:10px;
  max-width:55%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  flex-shrink:0;
}}
.art-date{{font-size:0.67rem;color:var(--txt3);white-space:nowrap;}}
.no-news{{
  font-size:0.8rem;color:var(--txt3);
  padding:18px;text-align:center;font-style:italic;
  background:#fafafa;border-radius:var(--r-sm);
  border:1px dashed var(--border);
}}

/* ── FOOTER ── */
footer{{
  text-align:center;padding:28px 20px 36px;
  border-top:1px solid var(--border);
  color:var(--txt3);font-size:0.78rem;line-height:2;
  background:white;
}}
footer strong{{color:var(--txt2);}}

/* ── RESPONSIVE ── */
@media(max-width:900px){{
  .fam-grid{{grid-template-columns:1fr;}}
}}
@media(max-width:640px){{
  .header-top{{flex-direction:column;align-items:flex-start;gap:6px;}}
  .update-box{{text-align:left;}}
  .site-title{{font-size:1.05rem;}}
  main{{padding:14px 10px 48px;}}
  .country-nav{{padding:5px 10px 10px;}}
}}
</style>
</head>
<body>

<header class="site-header">
  <div class="header-top">
    <div>
      <div class="site-title">🌏 全球富豪家族 · 财富传承新闻追踪</div>
      <div class="site-sub">覆盖信托诉讼 · 遗产争夺 · 继承危机 · 家族治理 · 来自全球主流媒体、X与Facebook</div>
      <div class="stat-chips">
        <span class="stat-chip">📊 {len(data)} 个家族</span>
        <span class="stat-chip">📰 {total_arts} 条最新报道</span>
        <span class="stat-chip">🌍 {len(countries)} 个地区</span>
      </div>
    </div>
    <div class="update-box">
      <div class="update-time">🔄 {esc(generated_at)}</div>
      <div><span class="update-freq">每 3 天自动更新</span></div>
    </div>
  </div>
  <nav class="country-nav">
    {nav_html}
    <button class="nav-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑ 顶部</button>
  </nav>
</header>

<main>
{sections_html}
</main>

<footer>
  <p><strong>数据来源</strong>：Google News · Reuters · Bloomberg · Financial Times · South China Morning Post · WSJ · X · Facebook</p>
  <p>标题已翻译为中文，正文保留原文。涵盖信托诉讼、遗产争夺、家族治理等核心议题</p>
  <p>本站内容仅供专业研究参考，不构成任何投资或法律建议</p>
  <p>最后更新：<strong>{esc(generated_at)}</strong> · 每 3 天通过 GitHub Actions 自动刷新</p>
</footer>

<script>
function goto(id) {{
  const el = document.getElementById('c-' + id);
  if (!el) return;
  const h = document.querySelector('.site-header').offsetHeight + 12;
  window.scrollTo({{top: el.getBoundingClientRect().top + window.pageYOffset - h, behavior: 'smooth'}});
}}

// Active nav highlight on scroll
const secs = document.querySelectorAll('.country-sec');
const btns = document.querySelectorAll('.nav-btn');
const obs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      const id = e.target.id.replace('c-','');
      btns.forEach(b => {{
        const onclick = b.getAttribute('onclick') || '';
        b.classList.toggle('active', onclick.includes("'" + id + "'"));
      }});
    }}
  }});
}}, {{rootMargin: '-15% 0px -75% 0px'}});
secs.forEach(s => obs.observe(s));
</script>

</body>
</html>'''


# ─────────────────────────────────────────────────────────────
# 主程序
# ─────────────────────────────────────────────────────────────

def main():
    print(f"🚀 全球富豪家族新闻追踪 · 开始抓取")
    print(f"   总计 {len(FAMILIES)} 个家族 / {len(COUNTRY_ORDER)} 个地区\n")

    all_data = []
    for i, fam in enumerate(FAMILIES, 1):
        print(f"[{i:02d}/{len(FAMILIES)}] [{fam['country']}] {fam['name']}")
        arts = fetch_family_news(fam)
        print(f"         → {len(arts)} 条报道")
        all_data.append({'family': fam, 'articles': arts})
        time.sleep(0.4)

    now = datetime.datetime.utcnow()
    generated_at = now.strftime('%Y年%m月%d日 %H:%M UTC')
    total = sum(len(d['articles']) for d in all_data)

    # Save JSON cache
    data_dir = ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / 'news.json', 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': generated_at,
            'total_articles': total,
            'families': all_data,
        }, f, ensure_ascii=False, indent=2, default=str)

    # Generate HTML
    html = build_html(all_data, generated_at)
    out = ROOT / 'index.html'
    out.write_text(html, encoding='utf-8')

    print(f"\n✅ 完成！")
    print(f"   家族数: {len(all_data)}")
    print(f"   报道数: {total}")
    print(f"   输出: {out}")


if __name__ == '__main__':
    main()
