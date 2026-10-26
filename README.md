# PPT 叙事大纲 · slide-story

> 先定唯一结论，再拆三个论点，把每页标题写成判断句。让「只读标题就能做决定」成为验收标准。

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-111827)](./SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e)](./LICENSE)
[![No deps](https://img.shields.io/badge/依赖-无-0ea5e9)](#)

职场五件套之一：[`resume-tailor`](https://github.com/zhbehx/resume-tailor) · [`interview-coach`](https://github.com/zhbehx/interview-coach) · [`weekly-report`](https://github.com/zhbehx/weekly-report) · [`slide-story`](https://github.com/zhbehx/slide-story) · [`meeting-actions`](https://github.com/zhbehx/meeting-actions)

---

## 为什么不是「帮我列个 PPT 大纲」

| | 直接让 AI 出大纲 | 用这个 Skill |
| --- | --- | --- |
| 起点 | 「你想讲什么」 | 「你要谁做什么决定」 |
| 结构 | 背景/现状/问题/方案/总结 | SCQA 或金字塔，按听众选 |
| 标题 | 「现状数据」「解决方案」 | 「流失的 63% 集中在小客户，使用率只有 12%」 |
| 页数 | 越多越"完整" | 时长 × 0.6~1.0，废页直接删 |
| 验收 | 看着挺全 | 脚本打分：废页数 / 判断句率 / 结论位置 |

检验标准只有一条：**把每页标题单独抄下来，能不能读成一段完整的论证。**

---

## 安装

```bash
git clone https://github.com/zhbehx/slide-story.git ~/.claude/skills/slide-story
```

## 30 秒上手

```
帮我做个 PPT 大纲，10 分钟给 VP 看，要批 2 个交付人力，主题是下季度续费改进
```

它会先给一句「听完之后希望谁做什么决定」，这句话不对，整份 PPT 都会跑偏——所以它一定会先跟你确认。

### 你会拿到什么

```markdown
# 一句话结论（谁 + 做什么决定 + 因为什么）
# 大纲：P1…Pn，每页「判断句标题 + 一个主体（图/表/对比）+ 一句说明」
# 关键页要点（可直接抄进 PPT 的文字）
# 删掉的页（说明为什么删）
# 自检：判断句 X/Y · 废页 0 · 页数 7/10 分钟
```

完整示例：[`examples/01-outline.md`](./examples/01-outline.md)（从 **0 分**的「目录+背景+总结」式大纲改成 **100 分**）

## 自检脚本

零依赖，Python 3.9+：

```bash
python scripts/check_outline.py outline.md --minutes 10

页数        ：10（10 分钟建议 6–10 页）
结论在前 3 页：是
废页        ：0
非判断句标题：0
评分        ：100/100
```

- 识别「目录 / 背景 / 现状 / 总结 / 谢谢 / 竞品分析」等**无判断页**
- 判断标题里有没有动词、因果、对比或数字
- 标题超过 40 字会报警（投影和手机看不清）
- `--strict` 有废页或名词标题时退出码 1，可挂 CI
- `--json` 结构化输出

## 核心规则（写在 SKILL.md 里）

1. **一页一个判断** —— 页与页之间是「因此」，不是「接下来」。
2. **标题写结论** —— 名词短语标题等于没有标题。
3. **结论先行** —— 第 2 页给总判断，后面全是证据。
4. **页数 = 结论数** —— 删页不删字；10 分钟 ≈ 6–10 页。
5. **一页一图一句** —— 视觉主体 ≤1 个，留白 ≥30%。

## 仓库结构

```
slide-story/
├── SKILL.md                      # 五原则 + Step 0–6 + 交付格式 + 反模式
├── references/
│   ├── story-structures.md       # SCQA/金字塔/问题树/对比/时间线/PREP + 10 页决策模板
│   └── slide-patterns.md         # 12 种页型、该删的页、四种排布
├── scripts/
│   └── check_outline.py          # 废页 / 判断句 / 结论位置 / 页数与时长匹配
└── examples/
    └── 01-outline.md             # 10 分钟决策汇报：0 → 100 分
```

## 自定义

1. **换场景**：把 `references/story-structures.md` 的「10 页决策汇报」改成你们公司的汇报模板。
2. **企业 PPT 规范**：在 `slide-patterns.md` 加一节公司字体/配色/页脚规则。
3. **调阈值**：`check_outline.py` 里改标题长度（40 字）与每页时长系数（0.6–1.0）。

## FAQ

**Q：一定要用 SCQA 吗？**
A：不一定。决策者用 SCQA，评审用金字塔，客户用「问题-代价-方案」，5 分钟同步用 PREP。选错结构比写错标题更致命。

**Q：老板就爱看「背景」怎么办？**
A：把背景压成 1 页，且写成判断句——「行业增速从 30% 降到 8%，靠拉新已经不够」。他要的是背景里的**结论**，不是背景本身。

**Q：能直接生成 pptx 吗？**
A：这个 skill 只做叙事与大纲（这一步决定 80% 的质量）。生成 pptx 是另一个动作，有需要可以接 Office 类 skill。

## License

[MIT](./LICENSE)
