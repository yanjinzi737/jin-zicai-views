# 参考仓库审计

## 范围

- 仓库：[lyra81604/zhengxi-views](https://github.com/lyra81604/zhengxi-views)
- 日期：2026-06-21
- 默认分支 `main`；公开、未归档
- 只读取元数据、README、SKILL、LICENSE、requirements 与 gitignore，未批量抓取语料或基金数据。

GitHub 目录接口受限，最小浅克隆也连接重置。以下结构以 README 明示目录为主，并用直接读取文件交叉确认，不宣称是完整清单。

## 结构

```text
zhengxi-views/
├── SKILL.md
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── references/
│   ├── method.md
│   ├── scorecard.md
│   ├── corpus_index.json
│   ├── corpus/
│   ├── fund_data/
│   └── all_funds/
└── scripts/
    ├── search_corpus.py
    ├── build_index.py
    ├── fetch_fund_data.py
    ├── build_fund_list.py
    ├── fund_lookup.py
    ├── fetch_any_fund.py
    └── score_fund.py
```

这是“入口指令 + 渐进式资料 + 单一职责脚本”的结构：SKILL 定义触发与证据边界；corpus 保存原始材料并由索引检索；method/scorecard 保存二级知识；fund_data/all_funds 保存数据快照与市场索引；scripts 分离检索、索引、抓取和评分。gitignore 排除缓存与打包产物；requirements 仅列 requests、Beautiful Soup、lxml。

可借鉴：证据、方法与数据分层；脚本独立验证；区分原话和推演；运行缓存不入库。

需要调整：

- 参考 SKILL frontmatter 含 `metadata`，不符合当前仅允许 `name` 与 `description` 的规范。
- README 展示树未列 LICENSE、requirements、gitignore，不能视为完整树。
- “全部公开观点”“全市场”等完整性声明须独立验证。
- 人物、机构、产品、任职区间和数据源必须重新核验，不能只替换姓名。
- 应先建立来源白名单和权利规则，再收录大量语料与数据。

## LICENSE

参考仓库使用 MIT License，版权行为 `Copyright (c) 2026 iiamyyy66`。MIT 允许使用、复制、修改和分发其覆盖内容，但复制全部或实质部分时须保留版权及许可声明，并以“原样”提供、无担保。

仓库另行说明：MIT 覆盖 scripts 代码及 SKILL、README、method、scorecard 等文档；`references/corpus/` 与 `references/fund_data/` 的语料和基金数据版权归原始权利人，仓库不主张版权。

结论：

1. MIT 不是对第三方语料或基金数据的再授权。
2. 实质复用其 MIT 内容须保留版权与许可文本并记录改动。
3. 本阶段只借鉴抽象结构，不复制内容，故不引入其 LICENSE。
4. 本项目应在原创内容与第三方材料边界明确后单独选择许可证。

## 本阶段决定

采用精简骨架：根目录放 Skill、说明、计划与协作规则；`references/`、`scripts/` 留作扩展；`docs/` 保存审计。暂不创建 corpus、fund_data、all_funds 或抓取依赖。
