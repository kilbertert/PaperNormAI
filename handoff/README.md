# 三人协作智能体框架
<p align="center">
  <img src="assets/banner.png" alt="三人协作团队" width="100%">
</p>

<p align="center">
  <a href="https://russellenvy.github.io/three-man-team/">russellenvy.github.io/three-man-team</a>
</p>

---

## AI 编码工具存在的痛点
AI 编码工具功能强大，但缺乏规范约束。
仅仅需要调用单个函数，却要读取整个代码库；
擅自添加无人需求的多余功能；
任务执行中途随意偏离原定目标；
每次会话都会消耗大量 Token，做许多无用功。

解决办法并非优化提示词，而是建立一套标准化协作流程。

**三人协作智能体框架**配置三名分工明确的智能体，拥有清晰的任务交接机制与行为规则，从根源规避成本最高的各类运行异常问题。
- 架构师：负责方案规划与项目部署
- 开发执行者：严格按照需求文档精准开发
- 审核员：不达标的工作成果一律不予通过

---

## 为何设定三名智能体
深度思维（DeepMind）多智能体研究表明：**3-5人规模、具备标准化成果交接机制**的协作团队，工作表现优于单人智能体及规模更大的协作群组。

三人配置并非随意设定：
既是实现有效审核的最少人数，也是避免协作沟通成本抵消工作收益的最大人数上限。

角色分工完全贴合真实软件开发交付流程：
- 统筹全局、负责系统整体架构与上线部署
- 高效编码、保证代码整洁规范的开发执行者
- 查漏补缺、发现开发疏漏问题的审核人员

---

## 快速上手
可选择两种安装方式：

---

### 单项目安装（推荐）
一个项目独立安装一套，直接克隆至项目目录。

**第一步：进入项目文件夹并克隆仓库**
```bash
git clone https://github.com/russelleNVy/three-man-team.git .claude/skills/three-man-team
```

**第二步：运行配置脚本并按照提示操作**
```bash
cd .claude/skills/three-man-team && ./setup
```

配置脚本会自动引导后续流程，输出可直接执行的命令以及接入 Claude 的提示词，按照终端提示操作即可。

---

### 全局安装（所有项目通用）
一次安装，任意项目均可直接使用。

**第一步：克隆至 Claude 全局技能目录**
```bash
git clone https://github.com/russelleNVy/three-man-team.git ~/.claude/skills/three-man-team
cd ~/.claude/skills/three-man-team && ./setup
```

执行完毕即完成一次性全局安装，配置脚本会校验环境完整性。

---

**在任意项目中启用本框架：**

**第二步：将智能体配置文件复制到项目目录，启动 Claude**
```bash
cp -r ~/.claude/skills/three-man-team/templates/project-folder/* /path/to/your/project/
cd /path/to/your/project
```

打开 Claude Code，粘贴以下指令：
```
你担任本项目的架构师智能体，请读取 new-setup.md 配置文件。
```

架构师智能体将自动完成后续全部操作：生成项目上下文文件、配置团队角色名称，并给出首次会话使用提示词。

---

## 工作流程
<p align="center">
  <img src="assets/workflow.png" alt="三人协作团队工作流程" width="100%">
</p>

所有开发任务均遵循统一流程：
架构师制定规划并编写需求文档 → 开发执行者阅读文档、输出实现方案并完成编码 → 移交审核员校验 → 审核通过则进入部署，不通过则退回重做 → 最终由架构师在项目负责人许可后完成上线部署。**全程严格按步骤执行，不可跳步**。

完整实战案例（从需求分析到项目部署）参考：
[`examples/sprint-walkthrough.md`](examples/sprint-walkthrough.md)

---

## 团队角色介绍
<p align="center">
  <img src="assets/role-cards-cropped.png" alt="架构师、开发员、审核员" width="100%">
</p>

三名智能体，三种独立职责，协同适配开发全流程。

默认角色：架构师、开发执行者、审核员。
支持自定义重命名，配置阶段告知新名称即可，架构师会自动适配修改。

---

## Token 消耗优化
框架内置五条核心规则，写入 CLAUDE.md，每次会话自动生效：
```
若内容来自已加载技能/记忆库 → 直接采信，跳过文件读取
若属于推测性内容 → 终止工具调用
多任务可并行执行 → 启用并行调用
输出内容超过20行且无需查阅 → 转交子智能体处理
准备重复复述用户指令 → 直接精简删除
```

可将 `token-optimizer` 技能全局安装至路径：
`~/.claude/skills/token-optimizer`
也可在项目 `.claude/skills/` 目录中本地引用。

在此规则基础上，如需压缩终端 Bash 输出内容，可搭配工具 [RTK](https://github.com/rtk-ai/rtk) 使用：
该工具可在内容传入 Claude 上下文前，压缩 `find`、`ls`、`grep` 等命令输出。
非必需依赖，但重度使用 Claude Code 命令行的用户强烈推荐安装。
**RTK（终端层压缩）+ 令牌优化器（行为层约束）** 组合可实现 Token 消耗大幅节省。

完整优化规范详见文档：`docs/token-optimization.md`

---

## 模板说明
- `templates/project-folder/` — **首选模板**
内置预设角色人设（架构师、鲍勃、理查德），开箱即用。可自定义角色定位描述，按需修改团队名称。
- `templates/generic/` — 空白通用模板
含 `[自定义项]` 占位符，适合从零搭建专属智能体人设，或全局统一配置多项目通用模板。

配置阶段可直接告知架构师新角色名称，自动完成全局重命名。

---

## 开源许可证
MIT 开源协议，永久免费使用。
