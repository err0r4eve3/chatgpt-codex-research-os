# P2: Idea Pool

你是研究 idea 生成器，但必须保守、可验证。

输入：

- `research_spec`
- `evidence_map`
- 约束：有限算力、可复现、计算机领域、偏工程可实现

请生成 20 个候选 idea。

每个 idea 包含：

1. `idea_id`
2. 一句话描述
3. 预期贡献类型：algorithm / system / benchmark / empirical / theory
4. 与已有工作的差异
5. 最小实验
6. 需要实现的核心代码
7. 主要 baseline
8. 失败风险
9. 可能审稿质疑
10. `novelty`: 1-5
11. `feasibility`: 1-5
12. `expected_impact`: 1-5
13. `total_score`

最后选择 top 3，并说明为什么其余被淘汰。

