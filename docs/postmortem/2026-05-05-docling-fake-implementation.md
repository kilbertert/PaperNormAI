# Postmortem — Docling 集成虚假应用

**问题简述:** Docling v2 API 理解错误导致文档解析代码为空操作

---

## 问题发现

2026-05-05 在审查 Step 1 docling 集成代码时，Richard 发现代码存在严重问题：
Bob 编写的 `_convert_to_document_model` 方法依赖了一个不存在的 `elements` 属性，
导致实际解析时所有段落都无法被提取。

---

## 发现方式

- [x] 自测
- [ ] Code Review
- [ ] 用户反馈
- [ ] 生产事故
- [ ] 其他：**架构复盘时主动验证**

---

## 影响范围

- `backend/app/infrastructure/docling/parser.py` 的 `_convert_to_document_model` 方法
- 所有调用 `DoclingDocumentParser.parse()` 的代码收到空 DocumentModel

---

## 时间线

| 时间 | 事件 |
|------|------|
| 2026-05-03 | Bob 实现 Step 1 docling 集成 |
| 2026-05-03 | Richard Review 通过（未发现 API 错误） |
| 2026-05-05 | Arch 主动复盘，验证实际 docling v2 API |
| 2026-05-05 | 发现 `docling_doc.elements` 不存在，实际应使用 `docling_doc.texts` |
| 2026-05-05 | Arch 直接重写 parser.py，修复 API 错误 |

---

## 根因分析

**表面原因：**

Bob 的 `_convert_to_document_model` 使用了：
```python
if hasattr(docling_doc, "elements") and docling_doc.elements:
    for element in docling_doc.elements:  # 这个属性不存在
```

但 docling v2.x 的实际 API 是：
- `docling_doc.texts` — 包含 `TextItem` 和 `SectionHeaderItem` 的列表
- `docling_doc.groups` — 包含分组结构（如章节）

**真正原因：**

1. **没有验证假设** — Bob 假设了 docling 的 API 结构，但没有在实际环境中验证
2. **虚假代码路径** — `hasattr(docling_doc, "elements")` 始终返回 False，所以 `for element` 分支永远不执行
3. **代码"看起来正确"** — 没有抛出异常，但静默返回空结果，比明显错误更危险
4. **Review 未能发现** — Richard 的 review 关注架构和代码风格，没有实际运行验证 API 兼容性

---

## 教训

1. **对于外部库/包，必须在实际代码中验证 API**
   - 不能只读文档或看示例
   - 必须写一个实际运行的小脚本验证数据结构

2. **静默失败比明显错误更危险**
   - 返回空结果比抛出异常更难发现
   - 应该用 `assert` 或明确的检查来尽早暴露问题

3. **架构复盘是必要的质量关卡**
   - 这次问题是通过 Arch 主动验证才发现的
   - 应该在 Review 流程中增加"实际 API 验证"步骤

4. **对于复杂的外部依赖，应该有集成测试**
   - 单元测试只验证逻辑，不验证 API 兼容性
   - 应该有一个端到端测试实际调用 docling 并验证输出

---

## 需要写进 CLAUDE.md / 项目规范的建议

1. **外部库 API 验证规则**：新集成的外部库必须通过实际运行的小脚本验证 API，不能只依赖文档或示例代码

2. **静默失败的检查**：对于从外部来源（文件、网络、库）获取的数据，如果结果为空应该报警而非静默接受

3. **Review 检查清单增加**：
   - [ ] 代码中使用的 API 已在实际环境中验证？
   - [ ] 返回空集合/字典的情况有明确处理？

---

## 关联文档更新

- [x] 已更新：`backend/app/infrastructure/docling/parser.py` — 正确使用 `docling_doc.texts` 和 `docling_doc.groups`
- [ ] 已更新：`docs/postmortem/YYYY-MM-DD.md` — 本复盘文档
- [ ] 无需更新：其他代码未受影响

---

## 相关代码变更

**修复前（有问题的代码）：**
```python
def _convert_to_document_model(self, docling_doc: Document) -> DocumentModel:
    if hasattr(docling_doc, "elements") and docling_doc.elements:  # 永远 False
        for element in docling_doc.elements:  # 永远不会执行
            ...
```

**修复后（正确的代码）：**
```python
def _convert_to_document_model(self, docling_doc) -> DocumentModel:
    # 从 docling_doc.texts 提取文本段落
    for idx, item in enumerate(docling_doc.texts):
        if item.label.value == 'section_header':
            continue  # 跳过标题，标题放入 structure
        paragraph = Paragraph(...)
        paragraphs.append(paragraph)
```

---

*复盘时间: 2026-05-05 18:00 — by Arch*
*归档原因：外部库 API 理解错误，静默失败，代码看起来正确但实际不工作*