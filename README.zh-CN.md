# Roleward Job Hunting

[English](README.md) | **简体中文**

> 本文是 [README.md](README.md) 的中文翻译。如与英文版有出入，以英文版为准。

**一个“精准优先”的 AI 求职 Skill，帮你判断精力到底值得花在哪里。**

Roleward 会了解你真实的职业背景，帮你寻找或评估机会，判断哪些值得投入，再把这个判断转化为真实可信的定位和申请材料。

它的目标是帮你投得**更好，而不是更多**。

> **Alpha · Codex 优先。** 当前推荐的 Alpha 用法，是把本仓库作为一个专用的本地 Codex 求职工作区。此前的本机用户级安装已验证发现、更新及私人资料保留；本次整合包尚未替换该安装包，通用安装/更新流程仍待验收。

## 为什么是 Roleward？

通用 AI 可以改写简历，也可以总结职位描述（JD）。Roleward 围绕的是一个更难的问题：

> **这个机会真的值得我投入吗？**

它会把几件容易混为一谈的事情分开来看：

- 你实际能做什么；
- 你的录用理由在招聘方眼里有多清晰；
- 这个职位是否推进你当前的职业方向；
- 地点、签证担保或其他约束是否让它真正可行；
- 哪些是已知的，哪些是推断的；
- 一次被拒意味着什么，以及它**不**意味着什么。

核心闭环：

**了解我（Understand Me）→ 精准扫描（Precision Scan）→ 投入决策（Pursuit）→ 定位（Position）→ 人工审核（Human Review）→ 申请材料包（Application Pack）→ 跟踪（Track）→ 学习（Learn）**

## 适合谁？

Roleward Alpha 最适合这样的求职者：

- 已经在求职中使用 AI 或 Codex；
- 职业经历不简单，无法靠关键词匹配概括；
- 正在转换方向、职能、行业、地域，或者同时在转换好几项；
- 想要少量真正值得投入的机会，而不是一长串列表；
- 在意定位的真实性，希望 AI 的产出建立在真实的职业证据之上；
- 愿意审核重要的假设，而不是把申请流程完全自动化。

它**不是**为海投、自动 LinkedIn 联络、编造简历匹配或保证面试预测而设计的。

## 能用它做什么？

| 我想要…… | Roleward 帮我…… |
| --- | --- |
| **建立我的职业上下文** | 把简历、职业笔记或已有的 AI 上下文，整理成结构化、可审核的职业档案 |
| **找到值得投入的机会** | 广泛搜索，然后只返回一份刻意精简的短名单；没有足够好的机会时返回零个 |
| **评估一个职位** | 从能力、筛选可读性、职业价值和受雇可行性出发，给出 `Pursue`（值得投入）、`Verify first`（先核实）或 `Pass`（放弃） |
| **想清楚我的定位** | 在改写对外材料之前，先产出一份定位简报（Positioning Brief） |
| **准备申请** | 定位审核通过后，定制简历、求职信、联系人短名单或联络草稿 |
| **从结果中学习** | 跟踪申请，保守地使用已确认的结果，不会把一次被拒变成永久规则 |

## 快速开始：Codex Alpha

### 1. 把仓库放到你的电脑上

克隆或下载本仓库，然后在 Codex 应用中把 `roleward-job-hunting` 文件夹作为本地项目打开。

如果你不想用终端，可以在已有的本地工作区里让 Codex 帮你克隆：

```text
帮我把 https://github.com/zhenglimindesign-ing/roleward-job-hunting 克隆到一个本地文件夹。
克隆后不要修改仓库内容。告诉我最终的文件夹路径。
```

然后在 Codex 中打开那个文件夹。

### 2. 从一句提示词开始

如果你已经有简历：

```text
阅读 SKILL.md，并使用 Roleward Job Hunting。

这是我的简历。帮我建立职业上下文和当前的求职方向。
能从材料中安全推断出的信息就不要再问我；把重要的事实、假设和缺失项列出来让我审核。
```

如果你想马上评估一个职位：

```text
阅读 SKILL.md，并使用 Roleward Job Hunting。

这个职位值得我投入吗？
<职位链接，或粘贴 JD>
```

这两种请求都会进入同一套底层工作流。

你可以直接用中文提问，Roleward 应该用你使用的语言回复；保存到本地状态的字段名和取值仍保持英文。

### 3. 先审核上下文，再信任后续判断

首次扫描前，Roleward 只需要足够的上下文来了解：

- 你的**职业锚点（Career Anchor）**：你实际做过什么；
- 你的**方向（Direction）**：你现在想往哪里走；
- 你的**地域（Geography）**：你想在哪里工作、能在哪里工作；
- 你的**工作许可状态（Authorization state）**：例如不需要签证担保、需要签证担保、视情况而定，或者不确定。

它应该给你一份**结构化上下文审核（Structured Context Review）**，而不是让你填一张长表单。

### 4. 试一个真实任务

```text
找几个这周真正值得我关注的职位。
只在我们已经确认的地域和约束范围内找。
```

或者：

```text
我想投这个职位。
在改写简历之前，先帮我想清楚应该怎样定位我的背景。
```

安装配置、本地状态和隐私，见[入门指南](docs/GETTING-STARTED.zh-CN.md)；更多工作流和示例提示词，见[使用指南](docs/USAGE.zh-CN.md)。

## 投入决策长什么样？

一个典型的职位评估结果会刻意把决策放在最前面：

```text
值得投入（PURSUE）

总体匹配度    80
能力匹配度    75
筛选可读性    65
职业价值      90

为什么可能值得你投入时间
你在企业级 B2B 产品和强监管系统方面的背景，能可信地衔接到这个职位。

主要顾虑
JD 要求正式的生产环境 AI 经验，而你目前的证据还不能充分证明这一点。

在流程中核实
团队对这项要求的执行有多严格。
```

具体数字是**方向性信号，不是概率**。推荐结论和理由，比 5–10 分的分差更重要。

## Roleward 不会做什么

Roleward 不应该：

- 自动投递申请；
- 自动发送 LinkedIn 消息或其他职业社交消息；
- 编造经历，或把独立项目包装成正式的生产环境经验；
- 为了多返回几个职位，悄悄放宽你的地域或其他硬性约束；
- 把未知的签证担保情况当成拒绝理由；
- 把一次被拒当作整个职位类别都不适合你的证据；
- 在当前 Alpha 中声称能给出经过校准的面试概率。

## 本地状态与隐私

Alpha 围绕本地结构化文件设计。

把本仓库作为专用工作区时：

- 默认的结构化状态：`state/roleward-state.json`；
- 简历、AI 上下文导出等私有源材料：`sources/`；
- 生成的申请材料：`application-files/`。

这些运行时目录下的真实用户文件会被 Git 忽略。**不要把你的简历、职业上下文、申请历史或本地状态提交到这个公开仓库。**

详见[入门指南](docs/GETTING-STARTED.zh-CN.md#本地状态与隐私)。

## 当前 Alpha 的边界

当前验证证据和限制，见 [Alpha 状态与后续检查（英文）](docs/ALPHA-STATUS.md)。

- 主要测试宿主：**Codex**。
- 结构化持久化和辅助脚本需要本地文件访问权限和 Python 3.11+。
- 当前的实时职位发现，依赖宿主具备网页/搜索能力。
- 手动触发的精准扫描即可满足 Alpha；生产级的定时扫描还不在本次公开 Alpha 的范围内。
- 此前的本机用户级 Codex 安装、发现及更新已通过验证，私人资料保持不变。本次整合包尚未替换该安装包，通用安装/更新流程仍待验收；专用仓库工作区仍是当前推荐方式。
- 分数只是辅助决策的次要信号，每次运行可能不同；评估 Roleward 主要看推荐质量、证据可信度和决策是否有用。
- 当前 Alpha 不需要 Roleward 生产后端。

## 反馈

遇到问题时，可以在 [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues) 反馈。说明你的请求、预期结果、实际结果和可获取的版本。分享前请去掉私人职业信息、简历和本地状态。

## 贡献者与开发者

面向用户的入口是 `SKILL.md`。配套实现位于：

- `references/`：各工作流的专项策略；
- `scripts/`：确定性的状态与工作流辅助脚本；
- `schemas/`：本地状态 schema；
- `fixtures/`：公开的合成/去标识化评估数据；
- `state/`、`sources/`、`application-files/`：被 Git 忽略的本地运行时目录。

启动检查：

```bash
python3 scripts/validate_skill.py
python3 scripts/smoke_context.py
python3 scripts/smoke_opportunity.py
python3 scripts/smoke_scan.py
python3 scripts/smoke_application.py
python3 scripts/smoke_learn.py
python3 scripts/smoke_eval.py
python3 scripts/smoke_pursuit_eval.py
python3 scripts/smoke_application_integrity.py
python3 scripts/smoke_scan_selection.py
python3 scripts/smoke_journey.py
python3 scripts/smoke_search_settings.py
python3 scripts/eval_runner.py
```

包校验脚本要求所选 Python 环境中已安装 PyYAML。
`eval_runner.py` 会区分三类内容：可执行的确定性 fixture、可移植 fixture 的结构检查，以及延后处理的语义用例。结构检查通过并不能证明模型的判断质量。可移植输入的准备方式和生成后的严格评分，见 `fixtures/README.md`（英文）。

内部产品与评估决策的权威记录位于私有的 Roleward 主仓库。本公开仓库是可分发的实现层。

GitHub PR 和 `main` 更新会在 Python 3.11、3.14 上自动运行同一组确定性包检查、工作流及样例检查。这些检查不执行模型判断质量评测。

## 许可证

待定。在正式添加许可证之前，本项目不授予任何开源许可。
