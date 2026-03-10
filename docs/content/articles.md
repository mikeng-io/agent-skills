# Content for Agent Skills Repository Launch

---

## 1. English Article

### What If Your AI Agent Had a Devil's Advocate?

I've been using AI coding agents daily — Claude Code, Cursor, Copilot — and I noticed a pattern: they're great at finding things, but terrible at challenging themselves.

Ask an AI agent to review your code and it will produce a list of findings. Some are real. Some are pattern-matched noise. The problem is, you can't tell which is which without doing the review yourself — which defeats the purpose.

This is the same failure mode you see in human code reviews when only one person reviews: no one pushes back. Every finding looks equally valid. Real issues get buried under false positives. Critical assumptions go unchallenged.

I wanted AI agents that argue with each other.

#### The Debate Protocol

So I built one. The [Deep Skills Suite](https://github.com/mikeng-io/agent-skills) is a set of composable skills for AI agents that introduces structured adversarial debate into multi-agent analysis.

Here's how the core debate protocol works in 5 phases:

**Phase 1 — Independent Investigation.** Multiple domain experts analyze your artifact in parallel. No communication between them. This prevents anchoring bias — no expert can influence another's initial findings.

**Phase 2 — Finding Publication.** All findings are collected and shared. Read-only. Everyone sees what everyone else found.

**Phase 3 — Challenge Rounds.** This is where it gets interesting. A Devil's Advocate agent is required to challenge every CRITICAL and HIGH severity finding. But challenges must be substantive — "I disagree" isn't enough. Valid challenges must identify a missing assumption, propose an alternative explanation, or surface a non-applicability scenario. Reviewers defend their findings with evidence or withdraw them.

**Phase 4 — Synthesis.** Findings that survived debate are confirmed. Overlapping findings are merged. Each finding is tagged: confirmed, withdrawn, disputed, merged, or discovered-during-debate.

**Phase 5 — Verdict.** PASS, CONCERNS, or FAIL — based on what survived, not what was initially found.

The result: findings that have been stress-tested. When something comes out of the debate as "confirmed," it means an adversarial agent tried to tear it apart and couldn't.

#### Beyond Single-Model Thinking

The suite goes further with the Deep Council — a multi-model review architecture. It dispatches the same task to Claude, Gemini, Codex, and OpenCode in parallel. Each model family runs its own internal analysis. Then a cross-model debate challenges the aggregated findings.

Why does this matter? Every model has blind spots. Claude reasons differently from Gemini. When three model families independently find the same issue, confidence goes up. When they disagree, that disagreement itself is valuable — it surfaces assumptions that a single model would never question.

#### It Audited Itself

The most satisfying moment was running the suite on its own codebase. The Deep Council found 13 legitimate issues in the skills that compose it. We fixed all 13. There's something poetic about a review system that can credibly review itself.

#### Model-Agnostic by Design

Nothing in the suite is hardcoded to a specific model. Skills reference capability levels (`highest`, `high`, `standard`) instead of model names. Bridges to different AI runtimes are pluggable — if you don't have Gemini CLI installed, the council skips it and proceeds with what's available. No missing tool ever halts execution.

The same skills work for code reviews, financial audits, marketing copy reviews, UX critiques, compliance checks, and research synthesis. A domain registry drives expert selection, so the suite automatically picks the right reviewers for whatever you're analyzing.

#### Try It

```bash
# Install individual skills
npx skills add mikeng-io/agent-skills --skill deep-review
npx skills add mikeng-io/agent-skills --skill deep-council

# Or install everything
npx skills add mikeng-io/agent-skills --all
```

Then just type `/deep-review` in Claude Code. No configuration. The suite reads your conversation context and figures out what to analyze.

The repo is open source: [github.com/mikeng-io/agent-skills](https://github.com/mikeng-io/agent-skills)

If you think AI agents should do more than generate — they should challenge, verify, and debate — give it a look.

---

## 2. LinkedIn Post

AI agents are great at generating code reviews. They're terrible at questioning their own findings.

I built a skill suite that makes AI agents debate each other. A Devil's Advocate agent is required to challenge every critical finding. Challenges must be substantive — identify a missing assumption, propose an alternative explanation, or prove non-applicability. Findings that survive are confirmed. Findings that don't are withdrawn.

It goes further: the Deep Council dispatches the same task to multiple AI model families (Claude, Gemini, Codex) in parallel, then runs a cross-model debate on the aggregated results. Multi-model agreement = higher confidence. Disagreement = surfaced blind spots.

The best part? I ran it on its own codebase. It found 13 real issues in itself. All fixed.

Open source, model-agnostic, works for code, compliance, research, and more.

https://github.com/mikeng-io/agent-skills

---

## 3. Short Chinese X Post

开源了一套 AI Agent 多智能体技能库 — Deep Skills Suite。

核心机制：结构化对抗辩论。多个 Agent 独立分析，Devil's Advocate 强制挑战所有关键发现，只有经受住质疑的 finding 才会被确认。还支持跨模型 Council（Claude + Gemini + Codex 并行 + 跨模型辩论）。

模型无关、领域无关、开箱即用。

https://github.com/mikeng-io/agent-skills

---

## 4. Long Chinese X Article

### 让 AI Agent 互相辩论：我开源了一套多智能体对抗分析技能库

我每天都在用 AI coding agent — Claude Code、Cursor、Copilot、Codex、Gemini。用久了发现一个问题：单个 Agent 做 code review 时，它很擅长找问题，但从不质疑自己的发现。

结果就是：一堆 findings 摆在你面前，有些是真问题，有些是模式匹配的误报。你分不清哪个是哪个，除非自己再审一遍 — 那还要 Agent 干嘛？

这跟人工 code review 只有一个 reviewer 的问题一样：没人 push back，所有发现看起来都同等重要，真正的关键问题反而被淹没了。

我想要的是 **会互相争论的 AI Agent**。

#### Debate Protocol：5 阶段结构化对抗辩论

这是整个技能库的核心机制，设计目标是消除确认偏差，区分"真正经得起推敲的发现"和"模式匹配的噪音"。

**Phase 1 — 独立调查。** 多个 domain expert Agent 并行分析同一个目标。关键规则：Agent 之间禁止通信。这防止了锚定偏差 — 没有哪个 expert 能影响其他人的初始判断。

**Phase 2 — 发现公示。** 所有 findings 被收集并广播给全体参与者。只读，不允许回应。为下一阶段的挑战做准备。

**Phase 3 — 挑战轮（最多 5 轮）。** 这是最关键的阶段。一个 Devil's Advocate（魔鬼代言人）Agent 被**强制要求**挑战每一个 CRITICAL 和 HIGH 级别的发现。但挑战必须是实质性的 — 不能只说"我不同意"。

合法的挑战必须做到以下之一：
- **指出遗漏的前提假设** — "这个发现假设了 X，但 X 在这个上下文中不成立，因为 Y"
- **提出替代解释** — "你发现的症状有另一个原因：Z"
- **证明不适用性** — "当条件 W 为真时，这个发现不适用"

Reviewer 必须用额外证据为自己的发现辩护，或者承认撤回。

**Phase 4 — 综合。** 经过辩论的 findings 被标记状态：`confirmed`（确认）、`withdrawn`（撤回）、`disputed`（争议中）、`merged`（与其他发现合并）、`discovered`（辩论中新发现）。重叠度超过 70% 的发现自动合并。

**Phase 5 — 最终裁定。** PASS / CONCERNS / FAIL — 基于**存活下来**的发现，而不是最初找到的发现。

效果：一个 finding 被标记为 confirmed，意味着一个专门的对抗性 Agent 试图推翻它但失败了。这比"AI 说有问题"可信得多。

#### Deep Council：跨模型多智能体审查

Debate Protocol 解决的是"单模型内部如何对抗"。Deep Council 解决的是"不同模型之间如何交叉验证"。

架构是两层辩论：

**第二层（Bridge 内部）：** 每个模型家族（Claude、Gemini、Codex、OpenCode）在自己内部跑完整的分析流程。Claude bridge 会运行完整的 5 阶段 Debate Protocol；Gemini 和 Codex 各自运行 Post-Analysis Protocol。

**第一层（跨 Bridge）：** 所有 bridge 的结果汇总后，一个 Debate Coordinator 对聚合后的发现发起挑战：
- **Stage A** — 机械去重：跨 bridge 重叠度 >70% 的 findings 自动合并
- **Stage B** — 跨模型辩论：Devil's Advocate 挑战那些多模型一致同意的发现 — "如果所有模型都同意，它们是否共享了某个盲点？"
- Integration Checker 检查跨 bridge 的整合缺口

**最终裁定逻辑：**
- FAIL — 多模型确认的 CRITICAL，或来自高深度 bridge 的单源 CRITICAL
- CONCERNS — 1-2 个多模型确认的 HIGH
- PASS — 只有 MEDIUM/LOW/INFO

**为什么跨模型重要？** 每个模型家族都有盲点。Claude 擅长抽象推理，Gemini 擅长多模态，Codex 擅长代码。当三个不同的模型家族独立发现同一个问题时，置信度显著上升。当它们产生分歧时，分歧本身就是有价值的 — 它暴露了单一模型永远不会质疑的假设。

#### 数据智能层：让 Agent 先做功课再开口

辩论和跨模型审查解决的是"如何分析"。但还有一个前置问题："Agent 在分析之前，是否充分理解了上下文？"

这套技能库内置了一个数据智能层，在分析开始前自动收集和索引信息：

**DeepWiki — 代码库级别的语义理解。** 集成了 Devin 的 DeepWiki MCP server，能对任何 GitHub 仓库做结构化文档查询。普通的 grep/read 给你的是"代码写了什么"，DeepWiki 给你的是"代码意味着什么" — 架构意图、组件关系、设计决策。支持三种查询模式：浏览文档结构、读取特定主题的文档、用自然语言提问。公有和私有仓库都支持。

**QMD — 本地文档的向量搜索。** 所有 skill 的输出（review 报告、audit 结果、exploration map）都会自动索引到 QMD 的 collection 中。这意味着之前的分析结果可以被后续分析检索和引用 — Agent 不会每次都从零开始。QMD 索引的是你的本地 markdown 文档（specs、ADRs、设计文档），和 DeepWiki 互补而非重叠。

**Perplexity — AI 合成的 web 搜索。** 不同于返回一堆 URL 的传统搜索，Perplexity 返回的是带内联引用的 AI 合成答案。适合回答"当前社区对 X 的共识是什么？"、"A 和 B 的对比？"这类需要综合多个信息源的问题。和 Brave Search 搭配使用 — Brave 提供独立索引的原始搜索结果，Perplexity 提供合成后的理解。

**Context 技能 — 智能路由的前置分析。** 在任何 deep-* skill 执行前，context 技能会自动分析当前对话：你在讨论什么类型的 artifact（代码？金融？营销？）、涉及哪些领域、应该用哪种执行路径（parallel-workflow、debate-protocol、还是 deep-council）。这一切都是对话驱动的 — 你不需要指定任何参数。

这些数据源都是**非阻塞**的：DeepWiki 没配？跳过，用 Glob/Grep + QMD 替代。Perplexity API 没设置？跳过，Brave Search 继续。没有任何缺失的工具会中断执行流程。

#### 自我审计

最有意思的是我拿这套技能库审查了它自己。Deep Council 跨模型运行后，在组成它的 skills 中发现了 13 个真实问题。全部修复。一个审查系统能可信地审查自己 — 这本身就是对机制有效性的证明。

#### 设计哲学

**模型无关：** 没有任何地方 hardcode 了具体的模型名。Skills 只引用 capability level（`highest`、`high`、`standard`）。Bridge 是可插拔的 — 如果你没装 Gemini CLI，Council 跳过它继续跑。任何缺失的工具都不会让执行中断。

**领域无关：** 同一套 skills 适用于 code review、合规审计、营销文案审查、UX 评估、学术研究。一个 domain registry 驱动 expert 选择 — 给它一段支付处理代码，它自动调出安全和金融领域的 experts。

**对话驱动：** 不需要关键词、不需要配置。Skills 从你的对话上下文中提取信息。讨论一个 TypeScript API？它自动检测技术领域并路由到对应的 reviewers。

**渐进增强：** 每个 skill 独立可用。加上 Debate Protocol 提升置信度。加上 Deep Council 获得跨模型验证。组织可以从简单开始，逐步升级。

#### 开始使用

```bash
# 安装单个 skill
npx skills add mikeng-io/agent-skills --skill deep-review
npx skills add mikeng-io/agent-skills --skill deep-council

# 安装全部
npx skills add mikeng-io/agent-skills --all
```

在 Claude Code 中输入 `/deep-review` 即可使用。无需配置。

GitHub: https://github.com/mikeng-io/agent-skills

如果你也认为 AI Agent 不应该只是生成 — 它们应该挑战、验证、互相辩论 — 欢迎试用和 star。
