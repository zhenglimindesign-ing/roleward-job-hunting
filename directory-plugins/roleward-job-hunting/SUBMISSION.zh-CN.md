# roleward-job-hunting 提交准备

[English](SUBMISSION.md)

这是 `codex/distribution-prep-20261013` 上的 0.1.0-alpha.3-distribution.2 审查候选包。现有 Release 和 Tag 未改动，发布前需维护者审查。生成式公开分发项目在下一次 Release 前应同步回 canonical 源码；本次不改写历史发布清单哈希。

## OpenAI

完整 ZIP 包含通用、Codex、Claude manifest、方形图标、三个启动提示、依赖与隐私说明。产品范围由 `skills/*/agents/openai.yaml` 声明。

本地流程限定为 CODEX。虚构 32 步 CLI 流程及现有简历导出检查通过；Claude 小任务保留证据限定。Pursuit 判断校准与真实用户价值仍为 NOT VERIFIED。本地执行的 partner 准入是外部送审前提，不是打包失败。

已登录平台要求先完成开发者身份验证。本人已提交个人验证，目前 identity in review；本次不声称完成上传、官方扫描或正式送审。通过后继续 https://platform.openai.com/plugins → 上传新插件 → skills-only ZIP，检查转换与自动扫描结果并修复阻断项。正式送审和具有约束力的声明需账号持有人授权。

## Claude

来源：`zhenglimindesign-ing/roleward-job-hunting`；路径：`directory-plugins/roleward-job-hunting`；分支：`codex/distribution-prep-20261013`。操作路径为 https://claude.ai/directory/manage → Submit new → Plugin bundle → Validate。GitHub 写权限已确认，最终任务交接记录平台校验及保存草稿是否实际成功。本地 Claude 安装／发现及已登录小任务通过；目录内原生运行仍为 NOT VERIFIED。

manifest 指向[分支隐私说明](https://github.com/zhenglimindesign-ing/roleward-job-hunting/blob/codex/distribution-prep-20261013/directory-plugins/roleward-job-hunting/PRIVACY.md)。政策咨询由另一路处理，本次不因政策推测删除核心功能，也不把校验通过当作政策批准。联系邮箱、年龄范围、具有约束力的合规确认与正式送审仍需账号持有人决定。本任务未获正式送审或公开发布授权。

## skills.sh

仓库发现、完整复制和新会话加载已在关闭遥测下通过；双语公开 README 已补充验证过的命令。默认分支安装仍使用当前公开源码，提议的文档和指令修复经维护者审查后才进入默认分支。关键词／搜索收录是独立事项且为 NOT VERIFIED；本次未添加排行榜功能或发送安装遥测。
