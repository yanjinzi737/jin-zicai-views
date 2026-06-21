# 离线脚本验证报告

验证日期：2026-06-21  
工作目录：`C:\Users\15996\jin-zicai-views`  
Python：`Python 3.14.0b1`

## 范围与约束

- 仅运行本地脚本，未启用网络请求。
- 未新增、搜索或修改任何来源。
- 未进入第三阶段。
- 验证前后来源状态保持为 `metadata_only=11`、`pending=1`、`verified=0`。

## 开始状态

执行 `git status --short`。仓库尚无首次提交，现有第一、二阶段文件均显示为未跟踪目录或文件：`AGENTS.md`、`PLAN.md`、`README.md`、`SKILL.md`、`agents/`、`docs/`、`references/`、`scripts/`。

## 实际命令与结果

| 命令 | 退出码 | 结果 |
|---|---:|---|
| `python --version` | 0 | `Python 3.14.0b1` |
| `python scripts\validate_corpus.py` | 0 | 12条记录；0条verified；Schema、ID、local_file、checksum、摘录长度及引用完整性通过 |
| `python scripts\build_corpus_index.py` | 0 | 重生成12条 `index.jsonl` 和 `index.csv` |
| `python scripts\build_corpus_index.py --check` | 0 | 12条记录已规范化，checksum无需刷新 |
| `python scripts\deduplicate_sources.py --strict` | 0 | 12条记录中无重复候选 |
| `python scripts\check_urls.py` | 0 | 12个唯一URL格式通过；仅格式检查，未发出在线请求 |
| `python scripts\check_markdown_links.py` | 0 | 0个本地Markdown链接需要检查；外部HTTP(S)链接按脚本设计跳过 |
| `python -m py_compile <scripts下每个.py>` | 0 | 全部6个Python文件编译通过 |
| JSONL/CSV UTF-8与状态一致性断言 | 0 | JSONL=12、CSV=12；CSV可用UTF-8-SIG读取；状态为11条metadata_only、1条pending |
| `git diff --check` | 0 | 未发现空白错误 |

## 警告与错误

`validate_corpus.py` 输出12条“证据未完全验证”警告：11条 `metadata_only`、1条 `pending`。这些是符合当前阶段事实的预期警告，不是校验失败。

本轮脚本没有产生Windows路径、UTF-8、参数或Python语法错误，因此没有为“让测试通过”而修改脚本逻辑。

## 实际变更

- 运行 `build_corpus_index.py`，由JSONL真源规范化并重生成 `references/corpus/index.csv`。
- 新增本报告。
- Python编译产生的临时 `scripts/__pycache__/` 已在确认路径位于项目目录后清理。

## 结论

当前离线语料工具链可在Windows PowerShell和Python 3.14.0b1下运行。Schema、source_id唯一性、引用完整性、重复来源、URL格式、Markdown本地链接、Python语法、JSONL/CSV编码与状态保持检查均通过。没有来源被升级为 `verified`。
