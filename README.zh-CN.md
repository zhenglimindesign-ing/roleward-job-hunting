# Roleward Job Hunting

[English](README.md) | **简体中文**

**判断哪些机会值得投入，再真实地呈现你的职业背景。**

[Roleward](https://roleward.liminzheng.com/) 是一个 AI 职业工作台。
**Roleward Job Hunting** 是其中开源、可移植的求职 Agent Skill。

它帮助你把有限的求职精力放在少量真正值得投入的机会里，同时考虑两类信息：

- **你从哪里来**：真实的职业经历、证据、优势和缺口；
- **你想去哪里**：当前的职业方向、职业价值和你在意的取舍。

目标不是帮你投得更多，而是帮你**投得更好**。

> **Alpha · 设计上可移植，目前完整验证路径是 Codex。** Roleward Job Hunting
> 遵循开放的 Agent Skills 结构，而不是 Codex 私有的指令格式。当前完整验证过的
> Alpha 使用方式，是把本仓库作为专用的本地 Codex 求职工作区。Claude 等兼容
> 宿主仍是 portability target，但 second-host acceptance 尚未完成。详见
> [Alpha 状态](docs/ALPHA-STATUS.md)。

## 为什么是 Roleward？

很多 AI 求职工具拿到 JD 以后才开始：

**JD → 匹配分数 → 改简历 → 投递**

Roleward 会先问前面一个更重要的问题：

> **这个机会本身值得我花时间吗？**

一份工作可能非常符合你的过去，却未必是你下一步真正想去的地方。
另一份工作也可能存在一些 stretch，但仍然值得尝试。

所以 Roleward 不会把所有问题压缩成一个模糊的“匹配度”，而是分开看：

- **能力匹配（Capability Match）：** 你的真实证据实际证明了什么？
- **筛选可读性（Screening Legibility）：** 招聘方能否看懂一个可信的录用理由？
- **职业价值（Career Value）：** 这份工作是否把你带向下一步想去的方向？
- **受雇可行性（Employability）：** 地点、签证、sponsorship 等现实约束是否让机会可以推进？
- **证据可信度（Evidence Confidence）：** 什么已经知道，什么只是推断，什么仍然不确定？

这些信号最终服务于一个更简单的决定：

**值得投入（Pursue） · 先核实（Verify first） · 放弃（Pass）**

分数只是辅助理解的方向性信号，不是面试概率。

## Roleward 替你承担哪些费时的工作？

求职真正耗时间的，通常不只是“写一份简历”。

更多时间消耗在不断重复的工作里：

**找职位 → 筛职位 → 查缺失信息 → 判断值不值得投 → 想怎么定位自己 →
改申请材料 → 跟踪结果 → 再调整下一轮搜索**

Roleward 希望接手其中大量重复的搜索、整理、分析和准备工作，让你的注意力
留给真正需要自己判断的地方。

| 求职阶段 | Roleward 可以替你做 | 你主要需要做 |
| --- | --- | --- |
| **第一次建立上下文** | 从简历、职业笔记或已有 AI 上下文中提取和整理职业经历、证据、当前方向、地域和工作许可信息 | 提供已有材料，修正少量真正重要的错误或缺失 |
| **寻找机会** | 搜索当前职位、尽量核实来源、去重、应用已确认约束，再把结果压缩成很短的名单 | 需要时触发一次 Scan，并决定哪些机会值得继续 |
| **Fit / Pursuit 分析** | 把能力匹配、招聘方是否容易理解你的录用理由、职业价值、地点/签证等可行性分开判断，并主动研究能够查清的重要未知信息 | 审核推理，做最终的 Pursue / Verify first / Pass 决定 |
| **形成申请定位** | 从真实经历中选择最有说服力的证据，整理 Positioning Brief：为什么可能录用你、强调什么、弱化什么、有哪些可信度缺口 | 确认或修改这个定位 |
| **准备 Application Pack** | 按需准备 Tailored Resume、Cover Letter、0–3 位可信联系人以及 LinkedIn / InMail 草稿；简历使用稳定模板输出 | 最终审核材料，并自己决定是否提交或发送 |
| **跟踪和学习** | 保存机会、判断、申请状态和结果；把明确反馈带回后续搜索，同时避免因为一次拒绝就过度总结 | 告诉 Roleward 实际发生了什么，并纠正不合理的推断 |

第一次把上下文建立好以后，你不应该每看到一个职位，就重新向 AI 解释一遍：

> “我是谁、以前做过什么、为什么想转这个方向、哪些东西对我重要。”

同一套结构化上下文会持续用于之后的搜索、机会判断、定位和申请材料。

### 现在手动触发 Scan，之后可以接定时触发

当前 Public Alpha 支持你**手动触发 Precision Scan**：

```text
帮我找几个这周真正值得关注的职位。
只使用我们已经确认过的地域和约束。
如果没有足够好的机会，不要为了凑数量返回结果。
```

Roleward 会负责搜索、核实、去重、过滤和第一轮判断，而不是直接丢给你几十条链接。

Scan 底层工作流已经按 `manual | scheduled` 设计，因此以后 scheduler 可以调用同一套流程。
但 **production-grade 的自动定时扫描目前还没有作为 Public Alpha 能力交付**。

## 它适合谁？

Roleward Alpha 更适合这样的求职者：

- 已经在求职过程中使用 AI；
- 职业经历比较复杂，无法简单归结为关键词匹配；
- 正在转换职能、行业、级别、地域或职业方向；
- 希望把更多精力放在少数真正有价值的机会里；
- 在意真实可信的定位，而不是尽量把 JD 关键词塞进简历；
- 希望 AI 帮忙，但不希望把重要的职业判断完全交给自动化。

如果你的主要目标是海量投递、自动申请、自动 LinkedIn 外联、不顾真实性地最大化
关键词覆盖，或者获得一个“面试概率保证”，它可能并不适合。

## 快速开始：当前完整验证过的 Alpha 路径

目前完整验证过的使用方式，是专用的本地 Codex 工作区。

1. 克隆或下载[本仓库](https://github.com/zhenglimindesign-ing/roleward-job-hunting)。
2. 把得到的 `roleward-job-hunting` 文件夹作为本地项目在 Codex 打开。
3. 附上简历、职业资料或一个 Job/JD，然后说：

```text
读取 SKILL.md，使用 Roleward Job Hunting。

根据我附上的材料和接下来想做的方向，帮我开始。
先使用已有信息，再只问真正影响下一步的问题。
```

如果已经有一个具体职位：

```text
读取 SKILL.md，使用 Roleward Job Hunting。

这个职位值得我投入吗？
<职位链接或完整 JD>
```

第一次 Scan 只需要足够的上下文来理解：

- 你实际做过什么；
- 你下一步想去哪里；
- 地域 / Remote 范围；
- 工作许可或 sponsorship 状态。

“不确定”也是有效答案。

你可以直接使用中文或其他语言；Roleward 应该跟随你使用的语言回复，本地持久化的
schema 字段仍保持 canonical English。

设置与隐私见[开始使用](docs/GETTING-STARTED.zh-CN.md)，日常请求见
[使用指南](docs/USAGE.zh-CN.md)。

## 先决定是否值得投，再准备申请

一个典型机会分析应该先告诉你判断和原因，而不是先扔出一大张 requirement 表：

```text
值得投入（PURSUE）

为什么可能值得你投入
你的企业级 B2B 产品和强监管系统经历，可以真实地衔接到这份工作的核心要求；
同时，这个职位也能帮助你继续向当前希望发展的 AI 产品方向移动。

主要顾虑
JD 希望候选人拥有更深的正式生产环境 AI 经历，而你目前的证据还不能完全证明这一点。

在招聘流程中核实
团队究竟把这项要求看成严格硬门槛，还是接受相邻的企业产品经验作为可信过渡。
```

如果你决定 Pursue，Roleward 会先生成一份 **定位简报（Positioning Brief）**：
为什么可能录用你、最强证据是什么、该强调和弱化什么、有哪些可信度缺口，以及推荐
怎样讲述你的职业背景。

你先审核或修改定位，之后才按需生成真正对外的材料。

## 定制简历，不等于重新发明一份简历

如果已经存在一份可用的基础简历，Roleward 会把它作为 **artifact baseline**。

定制主要发生在：

- 内容选择；
- 强调程度；
- 顺序；
- 压缩；
- 表达方式。

Career Evidence 和已经审核的 Positioning 用来帮助选择和验证内容，而不是授权 AI
从零重建你的职业历史。

当前 Resume 路径会保护重要职业事实和最强证据，明确区分独立项目与正式生产经验，
并使用一套固定的 Roleward 模板输出。可选的本地文档运行环境可用时，会交付可编辑的
**DOCX + PDF** 并检查真实导出文件；不会尝试复刻任意原始 PDF 的排版。

详见[简历运行环境](docs/RESUME-RUNTIME.md)。

## 人工审核是产品的一部分

人工审核不是“自动化还没做完”，而是 Roleward 有意保留的边界。

你应该审核：

- 导入后真正重要的职业信息；
- 一个职位究竟是否值得投入；
- 对外定位；
- 最终的简历或消息。

Roleward **不会自动提交申请，也不会自动发送职业社交消息**。

AI 负责减少搜索、整理、比较和准备工作的负担；最终职业判断和真正对外的动作仍然
由你掌握。

## 本地文件与连续使用

专用工作区会把：

- 私人源材料保存在 `sources/`；
- 结构化状态保存在 `state/roleward-state.json`；
- 生成的申请材料保存在 `application-files/`。

这些运行目录已被 Git 忽略。不要把真实简历、私人职业上下文、申请历史或本地状态
提交到公开仓库。

新对话可以读取同一份状态继续工作。本地文件不是云备份；Skill 也不会自动与
Roleward Web、招聘网站或收件箱同步。

## 哪些仍处于 Alpha？

Skill 的核心设计是可移植的，但**目前只有 Codex 有完整验证过的 Alpha 使用路径**。
这不代表 Roleward 是 Codex-only 产品：Claude 等兼容宿主仍是明确的 portability
target，只是 second-host acceptance 尚未关闭。

其他仍未关闭的 Gate 包括：

- Pursuit 建议稳定性仍处于 **HOLD**，等待 PM adjudication；
- 实时搜索的 aggregate worth-review precision 尚未正式验收；
- Resume 固定模板、DOCX/PDF 和 fidelity guard 已实现，但建议的人工质量标准仍需要 PM 验收；
- 独立新用户 first-user usefulness check 仍未完成；
- production scheduled Scan、通用安装/自动更新、后端同步和自动外部动作都不属于当前 Alpha。

技术测试通过并不等于推荐质量或真实招聘结果已经被证明。详见
[Alpha 状态](docs/ALPHA-STATUS.md)。

## 反馈

如果 Roleward：

- 推荐了一个明显不值得投入的机会；
- 漏掉了一个真正重要的 Pursue 理由；
- 重复询问材料里已经存在的信息；
- 编造或夸大职业证据；
- 定制后的简历反而明显比原版更差；
- 因为一次求职结果就过度总结规律；

欢迎通过 [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues)
反馈。

请只提供脱敏后的请求、预期结果、实际行为和版本 / commit 信息。
不要公开完整简历或本地 Roleward 状态。

## 面向贡献者与开发者

欢迎贡献。先看[贡献指南](CONTRIBUTING.zh-CN.md)和
[公开贡献约定](docs/CONTRIBUTOR-CONTRACT.md)（英文）。文档与可复现修复可以直接提交 PR；
新流程或判断规则先通过 Issue 讨论。尤其欢迎合成行为案例及有理由的分歧，请勿公开私人职业资料。

包验证需要 Python 3.11+ 和 PyYAML 6.0.3。可选文档检查还需要
`requirements-resume.txt`。

```sh
python -B scripts/validate_skill.py
python -B scripts/eval_runner.py
python -B scripts/smoke_journey.py
python -B scripts/smoke_resume.py
```

`.github/workflows/skill-checks.yml` 列出完整回归。
合成用例不能证明模型质量或真实投递结果。

内部产品与评测权威仍保留在私有 Roleward 仓库中；这个公开仓库是可分发的实现层。

## License

[MIT](LICENSE)。附带的 Noto Sans 字体保留
[SIL OFL 条款](assets/fonts/OFL.txt)。
