# AGENTS.md

## 项目范围

建设金梓才公开观点的可溯源研究 Skill。当前只维护基础骨架、审计与计划；不要批量抓取材料或提前生成方法论结论。

## 工作规则

1. 修改前运行 `git status --short` 和 `git diff`，阅读现有文件，不覆盖用户改动。
2. 先检查 `PLAN.md` 当前阶段，超出阶段就停止并报告。
3. 优先使用基金公司、监管披露、定期报告和本人公开访谈等一手来源。
4. 不将搜索摘要、转载或模型记忆当作本人原话。
5. 每条引文和事实记录来源、日期、发布方与访问路径。
6. 不复制参考仓库的第三方语料或基金数据。复用其 MIT 内容须保留许可要求并记录来源。
7. 保持 `SKILL.md` 精简；详细资料放 `references/`，过程审计放 `docs/`。
8. 新脚本须可重复运行、限制输出规模并执行代表性测试。

## Skill 约束

- frontmatter 只保留 `name` 与 `description`。
- 名称和目录均为 `jin-zicai-views`。
- 无证据时必须回答资料不足。
- 投资内容须声明仅供研究与学习，不构成投资建议。

## 基础检查

```powershell
python C:\Users\15996\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\15996\jin-zicai-views
git diff --check
git status --short
```
