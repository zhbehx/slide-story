#!/usr/bin/env python3
"""检查 PPT 大纲：页标题是不是判断句、有没有废页、页数是否匹配时长。

大纲写法（每页一行，取第一个冒号后的内容作标题）：
    P1 封面：把续费率从 71% 做到 80% 的三件事
    P2 结论：小客户不用核心功能，是流失的主因
    或：- P3 竞品靠低价，我们靠交付速度

用法：
    python scripts/check_outline.py outline.md
    python scripts/check_outline.py outline.md --minutes 10 --strict
    python scripts/check_outline.py outline.md --json

退出码：0 正常；--strict 下存在非判断句标题或废页时为 1；文件错误 2。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 纯名词短语：出现这些且没有判断标记，视为"没有信息量的标题"
NOUN_ONLY = {
    "背景", "现状", "目录", "谢谢", "总结", "简介", "概述", "团队介绍", "附录",
    "问题", "方案", "数据", "分析", "规划", "计划", "用户画像", "竞品分析",
    "市场分析", "技术架构", "产品介绍", "q&a", "qa", "下一步", "结束语",
}

# 判断句标记：因果、对比、数量、行动、结论
JUDGE = [
    "因为", "所以", "主因", "源于", "导致", "造成", "差在", "优于", "不如", "高于", "低于",
    "只需", "建议", "应该", "要做", "先做", "可以", "是", "在", "比", "vs", "会", "能",
    "没有", "不是", "已经", "仍", "还", "必须", "拆", "改", "加", "砍",
]
NUMBER_RE = re.compile(r"\d")
PAGE_RE = re.compile(r"(?:^|\s)(?:P|p|第)\s*(\d+)\s*(?:页)?\s*[:：、.]?\s*(.+)$")


def parse_pages(text: str) -> list[dict]:
    pages = []
    for raw in text.splitlines():
        line = raw.strip().lstrip("-*•· ")
        if not line:
            continue
        m = PAGE_RE.search(line)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()
        title = re.sub(r"^[*#\s]+", "", title)
        # 去掉"主体：…"这类补充说明，只留标题
        title = re.split(r"\s*[—–-]{1,2}\s*(?:主体|内容|图|要点)[:：]", title)[0]
        title = title.split("　")[0].strip()
        pages.append({"page": num, "title": title})
    pages.sort(key=lambda p: p["page"])
    return pages


def cjk_len(s: str) -> int:
    return len(re.sub(r"\s", "", s))


def analyze(text: str, minutes: float | None) -> dict:
    pages = parse_pages(text)
    issues = []
    non_sentence = []
    waste = []

    for p in pages:
        t = p["title"]
        low = t.lower().strip(" ：:。.")
        is_noun = low in NOUN_ONLY or (cjk_len(t) <= 4 and not NUMBER_RE.search(t))
        has_judge = any(k in low for k in JUDGE) or bool(NUMBER_RE.search(t))
        if is_noun and not has_judge:
            waste.append(f"P{p['page']} {t}")
        elif not has_judge:
            non_sentence.append(f"P{p['page']} {t}")
        if cjk_len(t) > 40:
            issues.append(f"P{p['page']} 标题 {cjk_len(t)} 字，超过 40 字（手机/投影看不清）")

    # 结论是否在前 3 页
    head = " ".join(p["title"] for p in pages[:3])
    conclusion_early = bool(re.search(r"结论|建议|只需|应该|我推荐|请求", head))

    expected = None
    if minutes:
        # 每页约 1–1.5 分钟：10 分钟 → 6–10 页
        expected = (max(3, round(minutes * 0.6)), max(4, round(minutes * 1.0)))

    page_count = len(pages)
    over = bool(expected and page_count > expected[1])
    under = bool(expected and page_count < expected[0])

    score = 100
    score -= len(waste) * 20
    score -= len(non_sentence) * 12
    score -= 15 if not conclusion_early else 0
    score -= 10 if over else 0
    score -= 5 if under else 0
    score -= min(10, len([i for i in issues if "超过" in i]) * 5)
    score = max(0, score)

    return {
        "page_count": page_count,
        "titles": [p["title"] for p in pages],
        "waste_pages": waste,
        "non_sentence_titles": non_sentence,
        "conclusion_in_first_3": conclusion_early,
        "expected_range": expected,
        "too_many_pages": over,
        "too_few_pages": under,
        "length_issues": issues,
        "score": score,
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="检查 PPT 大纲质量")
    ap.add_argument("file", help="大纲文件")
    ap.add_argument("--minutes", type=float, default=None, help="汇报时长（分钟），用于页数校验")
    ap.add_argument("--strict", action="store_true", help="存在废页/非判断句标题时退出码 1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    p = Path(args.file)
    if not p.is_file():
        print(f"找不到文件：{p}", file=sys.stderr)
        return 2

    r = analyze(p.read_text(encoding="utf-8-sig"), args.minutes)
    if r["page_count"] == 0:
        print("没解析到页面。每页一行，写成 `P1 封面：标题` 或 `P3 结论：…`。", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"页数        ：{r['page_count']}"
              + (f"（{args.minutes:g} 分钟建议 {r['expected_range'][0]}–{r['expected_range'][1]} 页）" if r["expected_range"] else ""))
        print(f"结论在前 3 页：{'是' if r['conclusion_in_first_3'] else '否'}")
        print(f"废页        ：{len(r['waste_pages'])}")
        print(f"非判断句标题：{len(r['non_sentence_titles'])}")
        print(f"评分        ：{r['score']}/100")

        if r["waste_pages"]:
            print("\n废页（没有独立判断，删掉或合并）：")
            for s in r["waste_pages"]:
                print(f"  - {s}")
        if r["non_sentence_titles"]:
            print("\n标题是名词短语，改成判断句（要有动词/因果/对比/数字）：")
            for s in r["non_sentence_titles"]:
                print(f"  - {s}")
        if r["too_many_pages"]:
            print(f"\n页数偏多：删掉没有独立判断的页，而不是删字。")
        if r["too_few_pages"]:
            print("\n页数偏少：可能缺证据页（每论点至少 1 页支撑）。")
        for i in r["length_issues"]:
            print(f"  - {i}")

    if args.strict and (r["waste_pages"] or r["non_sentence_titles"]):
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main(sys.argv[1:]))
