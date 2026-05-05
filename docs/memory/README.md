# Memory — PaperNormAI
*每日工作存档。按日期堆积，不覆盖旧记录。*

---

## 最近存档

| 日期 | 存档文件 |
|------|---------|
| 2026-05-05 | docs/memory/2026-05-05.md |
| 2026-05-03 | docs/memory/2026-05-03.md |

---

## 存档模板（每次 /checkpoint 调用）

```markdown
# [YYYY-MM-DD] 工作存档

**存档时间:** HH:MM

---

## 今日完成

- [任务1]
- [任务2]

## 进行中

- **[模块/任务]** — 进度：[描述]
  - 下一步：[具体动作]

## 今日决策

- [决策1 — 为什么选A不选B]
- [决策2]

## 卡点与问题

- **[问题]** — 状态：[已解决/待解决/升级给谁]
  - 尝试过的方案：[方案]
  - 结论：[为什么行不通/还有什么可选]

## 备注

- [任何值得记下的上下文]

---

*本次存档由 [Arch/Bob/Richard] 手动触发*
```

---

## 存档文件命名

- 每日一个文件：`docs/memory/YYYY-MM-DD.md`
- 例：`docs/memory/2026-05-02.md`
- 同一工作段有多次存档时，用时间戳区分（如 `2026-05-02-1.md`）

---

## 使用方式

**存入**（任意时刻）：
```
/checkpoint
```

**取出**（新 session 开头）：
```
/recap
```

---

## 与其他文件的关系

```
SESSION-CHECKPOINT.md  ← 单次会话存档（handoff/）
BUILD-LOG.md           ← 步骤维度的构建历史（handoff/）
progress.md            ← 当前快照（docs/）
memory/                ← 每日存档（docs/memory/）
postmortem/            ← 踩坑复盘（docs/postmortem/）
```

---

## 清理规则

- 超过 90 天的存档可以归档到 `docs/memory/archive/`
- 归档前在 `docs/memory/README.md` 注明归档去向

---
*最近更新: YYYY-MM-DD*