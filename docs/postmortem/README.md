# Postmortem — PaperNormAI
*踩坑复盘存档。每一次值得记录的失败都是团队学习的素材。*

---

## 最近复盘

| 日期 | 标题 | 类型 | 根因 |
|------|------|------|------|
| 2026-05-05 | Docling v2 API 理解错误导致静默失败 | bug | 外部库 API 未经验证，`elements` 属性不存在 |

---

## 存档索引

| 日期 | 存档文件 |
|------|---------|
| 2026-05-05 | `2026-05-05-docling-fake-implementation.md` |

---

## 复盘模板

```markdown
### [日期] — [问题简述]

**问题现象：**
[一句话描述]

**根因：**
- **表面原因：** [直接导致问题的代码/设计]
- **真正原因：** [背后的问题]

**教训：**
- [教训1]

**回写动作：**
- [ ] 更新 `.ai/skills/fix-development.md`（如果是可复用的修复模式）
- [ ] 更新 `.github/copilot-instructions.md`（如果是系统性约束）
- [ ] 更新 `docs/knowledge/PaperNormAI-knowledge/900-learning-log.md`
```

---
*最近更新: 2026-05-05*