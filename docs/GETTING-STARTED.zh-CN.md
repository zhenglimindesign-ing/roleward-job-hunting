# 开始使用

[English](GETTING-STARTED.md) | **简体中文**

在专用的本地 Codex 工作区使用 Roleward Job Hunting。带上简历、职业笔记或一个想评估的岗位即可；开始前不需要整理完整档案。

## 一次性设置

克隆或下载[仓库](https://github.com/zhenglimindesign-ing/roleward-job-hunting)，把 `roleward-job-hunting` 文件夹作为本地项目在 Codex 打开。
如需 Codex 帮你克隆，可以先在一个现有本地工作区说：

```text
把 https://github.com/zhenglimindesign-ing/roleward-job-hunting 克隆到本地文件夹。
保留任何已有文件，并告诉我最终路径。
```

打开该文件夹，附上材料，然后说：

```text
读取 SKILL.md，使用 Roleward Job Hunting。
根据这些材料和我接下来想做的方向，帮我开始。
```

直接提供 Job/JD 时，可以问是否值得追求。Roleward 应使用已有候选人背景，只询问会改变结论的缺失信息，并使用你的语言回复。

## 审核重要信息

首次广泛搜索前，需要职业背景、当前方向、地点范围和工作授权状态；“不确定”有效。
Roleward 应给出简洁的结构化背景审核，区分来源陈述、确认事实和推断。
在对话中纠正重要错误即可，不需要逐行确认或填写档案表单。

选择追求后，先审核 Positioning Brief，再请求申请材料。定制简历时，请附上或指出希望采用的基础简历。
它应继续作为基准，保留重要职业事实和证据。文件生成需要可选的[本地运行环境](RESUME-RUNTIME.md)，Codex 可以检查并准备；草稿不等于已交付 DOCX/PDF。

## 保存与继续

私有输入、历史和材料保存在工作区中已被 Git 忽略的区域：

| 位置 | 内容 |
| --- | --- |
| `sources/` | 简历和来源笔记 |
| `state/roleward-state.json` | 结构化背景、机会和历史 |
| `application-files/` | 准备好的材料和导出记录 |

不要提交这些文件。本地状态不是云备份，也不与 Roleward Web、招聘网站或收件箱同步。
无法持久保存时，Roleward 必须说明连续性仅限当前对话。

新对话中打开同一工作区，然后说：

```text
读取 SKILL.md，使用 Roleward Job Hunting。
从保存的背景和上次处理的机会继续。
```

Roleward 应先读取已有状态，不让你重建背景。找不到历史时，先检查工作区，再考虑初始化新状态。

## 要求与更新

需要 Codex 本地文件能力，以及 Python 3.11+ 运行持久化工具。实时搜索需要宿主的当前网页/搜索能力。
普通状态工具只用 Python 标准库；PyYAML 只用于贡献者包验证。简历渲染另有可选依赖。

受支持的 Alpha 路径是专用工作区。全局安装和自动更新尚不支持。
手动更新代码前，请 Codex 检查本地改动并备份私有运行区域；代码提交不备份被 Git 忽略的职业数据。
保留并协调已有改动，只更新代码，然后读取状态、检查历史仍然可用。

## 遇到问题

如果 Codex 只解释 Roleward，请它读取 SKILL.md 并实际使用流程。
没有网页访问时，提供 JD，不要期待已验证的新搜索。没有文档依赖时，可以请求草稿和未交付文件的明确说明。
把分数看作方向提示，而非概率。通过 [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues) 提交脱敏反馈。

继续阅读[使用指南](USAGE.zh-CN.md)和 [Alpha 状态](ALPHA-STATUS.md)。
