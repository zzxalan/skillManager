---
name: prompt-optimizer
description: Optimize incomplete, ambiguous, or rough user prompts into complete context-aware prompts using project files, repository conventions, and available documentation. Use when asked to 优化提示词, 补全提示词, 改写 prompt, prompt engineering, refine requirements, turn rough ideas into actionable AI tasks, or prepare prompts for Codex, ChatGPT, Claude, or other agents.
---

# Prompt Optimizer

## Goal

把用户不完整、含糊或只有初步想法的提示词，改写成可执行、上下文充分、边界清晰、可验证的高质量提示词。优先结合当前项目实际情况，不凭空替用户决定业务目标。

## Workflow

1. 保留用户原始意图，先判断用户是只想优化提示词，还是希望优化后继续执行任务。
2. 确认目标执行对象。若用户未说明，默认面向当前对话中的 AI coding agent；如果用户提到 ChatGPT、Claude、Codex、图片模型或其他工具，按对应对象调整措辞。
3. 收集项目上下文：
   - 优先读取当前仓库的 `AGENTS.md`、`README.md`、`package.json`、配置文件、目录结构和与任务相关的源码。
   - 使用 `rg` 或 `rg --files` 快速定位相关模块、测试、脚本和文档。
   - 只读取和提示词目标相关的上下文，避免把无关细节塞进最终提示词。
4. 识别缺口：目标、背景、输入、约束、范围、期望输出、验收标准、验证方式、权限边界、风险处理。
5. 根据缺口补全提示词：
   - 能从项目上下文确定的信息直接补充。
   - 无法确定但不阻塞执行的信息，用明确假设表达。
   - 会影响方向或有较高风险的信息，放到“仍需确认”。
6. 输出优化结果，不直接执行被优化后的任务，除非用户明确要求“优化并执行”。

## Reference

Read `references/quality-rubric.md` when the prompt is complex, cross-functional, high-risk, or needs a reusable structure.

## Output Format

默认用中文输出：

```text
优化后的提示词：
<用代码块给出可直接复制给 AI 的完整提示词>

补全依据：
- <说明从哪些项目文件、用户输入或合理假设补全>

仍需确认：
- <只列会影响执行方向的重要问题；没有则写“无”>
```

如果用户要求英文提示词，只把“优化后的提示词”写成英文，解释部分仍按用户当前语言回复。

## Quality Rules

- 写成任务提示，不写成抽象建议。
- 包含清晰的目标、范围、上下文、约束、输出格式和验收标准。
- 对 coding agent 的提示词必须包含代码风格、文件范围、测试或验证命令，以及不要改动无关文件的要求。
- 对需要联网、最新信息、法律、医疗、金融、安全或生产系统的任务，显式要求核验来源、标注日期或请求确认。
- 不要伪造项目事实、业务规则、接口字段、命令或文件路径。
- 不要过度限制模型的实现细节；只固定必要边界和质量标准。
- 如果原提示词明显可以直接执行但缺上下文，只做最小补全，避免把简单任务包装成复杂流程。
