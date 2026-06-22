# Trading Skills

股票投资 / 交易类 Claude Code skills。

## 来源

- 上游仓库：[tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)
- 引入 commit：`b556610`
- 引入日期：2026-06-16
- 共 56 个 skill，按 7 类组织（市场环境 / 核心组合 / 波段机会 / 交易计划 / 交易复盘 / 策略研究 / 进阶卫星策略）

> 仅供个人研究使用，不构成投资建议；不下单、不提供信号服务，人工决策环节始终保留。

## Python 依赖

多数 skill 的脚本需要以下依赖（每个 skill 自带 `scripts/` 和 `references/`，互不耦合）：

```bash
pip install jsonschema pyyaml requests scipy yfinance
# 图表识别类 skill（如 breadth-chart-analyst）另需：
pip install pillow opencv-python
```

## API Key 配置

部分 skill 需要外部数据源（用到时再配，未配置也能跑那些 local-only 的 skill）：

| 数据源 | 用途 | 环境变量 | 免费额度 |
|---|---|---|---|
| FMP (Financial Modeling Prep) | 大部分筛选器、基本面数据 | `FMP_API_KEY` | 250 次/天 |
| Alpaca | 实时组合 / 模拟交易 | `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` | 有免费档 |
| FINVIZ Elite | 加速分红筛选（可选） | — | 付费 |

### 免 API 的入门 skill（先跑这几个）

- `market-breadth-analyzer` — 市场宽度
- `uptrend-analyzer` — 趋势
- `position-sizer` — 仓位计算
- `trader-memory-core` — 交易日志
- `signal-postmortem` — 复盘

## 路径注意

上游 SKILL.md 内的示例命令路径是相对仓库根写的（如 `skills/vcp-screener/scripts/...`）。
在本仓库 skill 实际位于 `.claude/skills/<name>/`，调用脚本时对应改为：

```bash
python3 .claude/skills/vcp-screener/scripts/screen_vcp.py ...
```

## 升级

重新从上游 `skills/` 拷贝对应文件夹覆盖即可，并更新本文件的引入 commit。
