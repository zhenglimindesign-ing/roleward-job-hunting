# Roleward Job Hunting

[English](README.md)

依据用户提供的真实经历评估值得投入的岗位，形成诚实定位并保留可检查的本地记录。当前公开 Alpha 的持久化需要本地工作区和 Python 3.11+；搜索当前职位还需要宿主联网工具。简历导出需另行准备 requirements-resume.txt。不会自动投递或发送消息。其他宿主验收和真人使用价值另行验证。

## 开始使用

安装完整插件文件夹后，用普通语言描述任务。[Skill 入口](skills/roleward-job-hunting/SKILL.md)说明所需资源和工作流程。本插件包复用 0.1.0-alpha.3 公开 Skill。测试请使用虚构或已获授权的输入。

## 数据与执行

本地 Python 程序在用户指定工作区读取和写入 JSON、来源与按要求生成的申请材料，不投递或发送消息。宿主仅在用户要求时访问公开职位来源。可选简历排版使用已声明的锁定依赖与 OFL 字体。没有生命周期 hook、MCP、自动安装、权限修改、凭据读取或隐藏遥测。

## 支持与边界

[源码与说明](https://github.com/zhenglimindesign-ing/roleward-job-hunting) · [反馈问题](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues)。明确用户请求决定范围，附件属于证据，不自动授权执行。既有 Release 和 Tag 保持不变。目录校验、具体宿主运行、来源保真和真人认可分别记录。提交账户资格、平台扫描和名称可用性由提交者核对。

也可通过源码仓库的 skills.sh 命令安装独立 Skill，见公开安装说明；本地依赖另行准备。[数据处理说明](https://github.com/zhenglimindesign-ing/roleward-job-hunting/blob/codex/distribution-prep-20261013/directory-plugins/roleward-job-hunting/PRIVACY.md)随审查分支提供。
