"""HTML renderer for the 6-year updating infographic."""

from __future__ import annotations

import html
from pathlib import Path

_CSS_PATH = Path(__file__).resolve().parent / "six_years.css"


def _css_block() -> str:
    return f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>"


def _table(headers: list[tuple[str, str]], rows: list[list[str]], table_class: str = "") -> str:
    class_attr = f' class="data-table {table_class}"' if table_class else ' class="data-table"'
    head_cells = "".join(
        f'<th class="{html.escape(css)}">{html.escape(label)}</th>' for label, css in headers
    )
    body_rows = []
    for row in rows:
        cells = "".join(f"<td{cell_attr}>{cell_html}</td>" for cell_attr, cell_html in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        f'<div class="data-table-wrap"><table{class_attr}>'
        f"<thead><tr>{head_cells}</tr></thead>"
        f'<tbody>{"".join(body_rows)}</tbody></table></div>'
    )


def render_6years_infographic_html() -> str:
    content_table = _table(
        [("类型", ""), ("篇数", "center"), ("作用", "")],
        [
            [("", "读书笔记"), (' class="num"', "134"), ("", "读完书就有当周素材")],
            [("", "生活日记"), (' class="num"', "103"), ("", "记录当下")],
            [("", "地铁日记 / 30分钟日记"), (' class="num"', "74"), ("", "通勤或即兴，低门槛即时输出")],
            [("", "季度 / 年终总结"), (' class="num"', "60"), ("", "定期盘点，也是一篇更新")],
        ],
    )

    writing_table = _table(
        [("", ""), ("一鼓作气", ""), ("赶交差", "")],
        [
            [(" class=\"label\"", "时长"), ("", "一般 1 小时以内"), ("", "三四小时")],
            [(" class=\"label\"", "状态"), ("", "内心想表达，顺畅一次性写完"), ("", "周末时间不够，向自己交差")],
            [(" class=\"label\"", "典型"), ("", "地铁日记、30分钟日记"), ("", "25 年好些周末更新")],
        ],
        table_class="compare",
    )

    motive_table = _table(
        [("阶段", ""), ("动机", "")],
        [
            [(" class=\"label\"", "最初"), ("", "睡后收入（最早每月约 8 块）")],
            [(" class=\"label\"", "后来"), ("", "记录自己、认识自己")],
            [(" class=\"label\"", "更远"), ("", "写一本诉说平凡的书")],
        ],
        table_class="stats",
    )

    stats_table = _table(
        [("项目", ""), ("数据", "")],
        [
            [(" class=\"label\"", "周更"), ("", "快 6 年，518 篇原创")],
            [(" class=\"label\"", "阅读"), ("", "每天 1 小时+，连续 1299 天，累计 2119 小时")],
            [(" class=\"label\"", "读完"), ("", "130+ 本，年均约 30 本")],
        ],
        table_class="stats",
    )

    body = f"""
    <div class="infographic">
      <div class="hero-title">我是怎么做到<br/>持续 6 年更新的</div>
      <div class="hero-quote">
        <span class="accent">一句话：</span>不是靠灵感，是靠一条简单规则 + 读书喂内容 + 碎片时间格子化 + 允许写得不够好。
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">1</div>
          <div class="section-title">起点很世俗，规则很简单</div>
        </div>
        <div class="section-body">
          <div class="section-text">
            <span class="accent">2020 年 8 月底</span>开始周更公众号。动机是「大龄程序员的焦虑」和「想要睡后收入」。
          </div>
          <div class="rule-box">不管写什么，每周必须完成一篇更新。</div>
          <div class="flow-box">
            写作 <span class="flow-arrow">──没素材──▶</span> 读书 <span class="flow-arrow">──有内容──▶</span> 写作<br/>
            <span class="flow-loop">└──────── 互相喂着走 · 六年没断过 ────────┘</span>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">2</div>
          <div class="section-title">有先例：我相信「每天一点点」</div>
        </div>
        <div class="section-body">
          <div class="section-text">
            周更的信心，来自<span class="accent">背单词 2000 天</span>。像背单词一样，每天花 10 分钟写点东西、看看书，也能慢慢积攒许多东西。
          </div>
          <div class="section-text">
            日记、读书、周更、11 点睡觉——同一套逻辑：<span class="accent">稀疏平常的每日行为，攒久了就不用意志力了。</span>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">3</div>
          <div class="section-title">内容有流水线，不怕没东西写</div>
        </div>
        <div class="section-body">
          {content_table}
          <div class="section-text">持续阅读 + 输出 = <span class="accent">「养成游戏」</span>——进度看得见，就不轻易停。</div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">4</div>
          <div class="section-title">两种写法，都不追求完美</div>
        </div>
        <div class="section-body">
          {writing_table}
          <div class="section-text">不追求完美，才能持续。</div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">5</div>
          <div class="section-title">时间从碎片里来</div>
        </div>
        <div class="section-body">
          <div class="section-text">通勤把一天切成<span class="accent">格子</span>，每个格子里做那格子里想做的事：</div>
          <div class="scene-grid">
            <div class="scene-card"><div class="scene-icon">🚇</div><div class="scene-label">地铁<br/>听书、写地铁日记</div></div>
            <div class="scene-card"><div class="scene-icon">🛏️</div><div class="scene-label">早上被窝<br/>看书、改本周草稿</div></div>
            <div class="scene-card"><div class="scene-icon">🛋️</div><div class="scene-label">沙发<br/>继续写</div></div>
          </div>
          <div class="section-text">更新不是额外挤出来的，是<span class="accent">嵌进生活里</span>的。</div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">6</div>
          <div class="section-title">规则可松，但不放弃</div>
        </div>
        <div class="section-body">
          <div class="bullet-list">
            <div class="bullet-item"><span class="bullet-dot"></span><span>周日必须更新 → 有一周拖到周一，焦虑后接受了：<span class="accent">偶尔打破常规并非坏事</span></span></div>
            <div class="bullet-item"><span class="bullet-dot"></span><span>沉迷过游戏、拖更过、焦虑过 → <span class="accent">松一天，不会整段放弃</span></span></div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">7</div>
          <div class="section-title">动机变了，习惯留下来了</div>
        </div>
        <div class="section-body">
          {motive_table}
          <div class="section-text">前人早已分享过人生，自己想分享并不特殊——<span class="accent">三十岁正是英年，该为热爱的事全力以赴。</span></div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <div class="section-num">8</div>
          <div class="section-title">数字作证</div>
        </div>
        <div class="section-body">
          {stats_table}
        </div>
      </div>

      <div class="closing">
        <div class="closing-quote">永远不灰心，永远充满热情去生活、读书、写作，三五年后一成习惯，你就会从这个习惯看出自己生命的力量。</div>
        <div class="closing-author">——沈从文</div>
        <div class="closing-cta">保持在场，持续写，惊喜会来的。</div>
      </div>

      <div class="footer-meta">wygmjdd.github.io · 518 篇原创 · 2020.08 — 至今</div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  {_css_block()}
</head>
<body>
  {body}
</body>
</html>"""
