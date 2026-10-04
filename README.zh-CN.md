# Roleward Job Hunting

[English](README.md) | **简体中文**

**判断哪些机会值得投入，再诚实地呈现你的职业背景。**

[Roleward](https://roleward.liminzheng.com/) 是一个 AI 职业工作台。
**Roleward Job Hunting** 是其中开源、优先支持 Codex 的求职 Skill。
它同时考虑你已有的真实职业证据，以及你接下来希望走的方向，帮助你把有限的求职精力投入少量值得追求的机会。
目标是帮助你**投得更好，而不是更多**。

> **Alpha · 优先支持 Codex。** 当前使用方式是把本仓库作为专用的本地 Codex 求职工作区。
> 可复用的全局安装和自动更新尚不属于受支持的 Alpha 路径。
> 验证范围见 [Alpha 状态](docs/ALPHA-STATUS.md)。

## 为什么使用它？

关键词匹配无法决定一个岗位是否值得投入。Roleward 分开看五个问题：

- **能力匹配：** 你的证据实际证明了什么？
- **招聘可读性：** 招聘者能否理解一个可信的录用理由？
- **职业价值：** 岗位能否推进你当前的方向？
- **可就业性：** 地点、签证或其他结构性约束是否使机会可行？
- **证据置信度：** 什么已知、什么是推断、什么仍不确定？

主要结论是 **值得追求 / 先核实 / 放弃**。分数只是辅助判断，不是面试概率。
在写申请材料前，Roleward 先帮助你决定如何诚实地呈现背景。

## 适合谁？

适合已经使用 Codex、职业经历需要认真理解、正在考虑转型或新市场，并希望少看一些但更值得投入的岗位的人。
你需要愿意纠正重要假设并审核定位。它不面向批量投递、虚构简历匹配或保证录用结果。

## 工作流程

**理解背景 → 精准搜索或直接提供岗位 → 判断是否追求 → 定位审核 → 按需准备材料 → 记录与学习**

可以从简历、职业笔记或 Job/JD 开始。Roleward 先使用已有信息，再询问缺失事实。
搜索返回少量候选；**零结果也有效**。决定追求后，先审核 Positioning Brief，再按需准备简历、求职信或联系草稿。
明确报告的投递与结果可以用于后续工作。

## 在 Codex 开始

1. 克隆或下载[本仓库](https://github.com/zhenglimindesign-ing/roleward-job-hunting)。
2. 把得到的 `roleward-job-hunting` 文件夹作为本地项目在 Codex 打开。
3. 附上简历或粘贴 Job/JD，然后说：

```text
读取 SKILL.md，使用 Roleward Job Hunting。
根据我附上的材料，帮我开始。
先用已有信息，再只问影响下一步的问题。
```

直接评估岗位时，可以把后两行替换成：

```text
这个岗位值得我追求吗？
<岗位链接或完整 JD>
```

你可以使用任何语言，Roleward 应使用你的语言回复；本地结构化字段名保持英文。
首次搜索需要真实背景、当前方向、地点范围和工作授权状态；“不确定”是有效答案。
设置与隐私见[开始使用](docs/GETTING-STARTED.zh-CN.md)，日常请求见[使用指南](docs/USAGE.zh-CN.md)。

## 人工审核与控制权

**人工审核是产品原则。** 重要个人事实由你纠正，职业定位由你选择。
定位审核是申请准备唯一必需的审核关口。Roleward 保持独立项目与正式生产经验的区别，保留基础简历中的重要证据，
并在本地运行环境支持时，用一个固定模板交付可编辑 DOCX 和 PDF。提交前的最终审核仍由你负责。

Roleward 不提交申请，也不发送职业联系消息。生产级定时搜索、面试辅导、薪资谈判和人脉 CRM 不属于本次 Alpha。

## 本地文件与连续使用

专用工作区把私有输入放在 `sources/`，结构化记录放在 `state/roleward-state.json`，准备好的材料放在 `application-files/`。
这些区域已被 Git 忽略，请勿发布。新对话可以读取同一份状态继续工作。
本地文件不是云备份；Skill 不与 Roleward Web、招聘网站或收件箱同步。

## 哪些仍处于 Alpha？

Pursuit 建议稳定性仍处于 HOLD。实时搜索精度和独立新用户的实用性尚未建立。
简历质量标准仍是提案，需要人工验收。Codex 是唯一受支持的 Alpha 环境；其他宿主和通用安装/更新路径尚未验证。
文档生成需要可选的[本地简历运行环境](docs/RESUME-RUNTIME.md)。技术检查不代表建议或生成内容质量已通过。

详见 [Alpha 状态](docs/ALPHA-STATUS.md)。可通过 [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues) 提交脱敏反馈。

## 面向贡献者与开发者

包验证需要 Python 3.11+ 和 PyYAML 6.0.3。可选文档检查还需要 `requirements-resume.txt`。

```sh
python -B scripts/validate_skill.py
python -B scripts/eval_runner.py
python -B scripts/smoke_journey.py
python -B scripts/smoke_resume.py
```

`.github/workflows/skill-checks.yml` 列出完整回归。合成用例不证明模型质量或真实投递结果。

## 许可证

[MIT](LICENSE)。附带的 Noto Sans 字体保留 [SIL OFL 条款](assets/fonts/OFL.txt)。
