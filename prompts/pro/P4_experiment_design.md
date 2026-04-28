# P4: Experiment Design

你是实验设计负责人。

输入：

- `selected_idea`
- `evidence_map`
- baseline candidates
- 我的工程约束

请输出 `experiment_spec.yaml`，必须包含：

1. Hypotheses。
2. Datasets / benchmarks。
3. Baselines。
4. Metrics。
5. Ablations。
6. Stress tests。
7. Negative controls。
8. Run matrix。
9. Statistical analysis。
10. Failure logging policy。
11. Compute budget estimate。
12. Minimum acceptable result。
13. Kill criteria。
14. 哪些结果可以支持哪些 claim。
15. 哪些结果不能支持哪些 claim。

重点：不要设计无法执行的实验。

