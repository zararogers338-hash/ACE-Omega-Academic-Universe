# Methodology / 方法论

## English

ACE-Omega treats an academic corpus as a spatial system. Each paper is mapped to a celestial body. The mapping is metaphorical but computationally traceable:

- citation count influences mass and radius;
- publication year influences the time axis;
- discipline or module influences cluster position;
- extremely influential papers become black holes;
- top high-impact papers can become Dyson spheres;
- nearby works in the same module can be connected with faint lines;
- timeline replay shows field evolution.

The system does not claim that citation count equals truth. It uses citation count as a visible proxy for influence, gravity and attention.

## 中文

ACE-Omega 把学术文献集合看作一个空间系统。每篇论文被映射为一个天体。这个映射是隐喻性的，但它不是随意画图，而是有明确计算路径：

- 引用量影响质量与半径；
- 发表年份影响时间轴位置；
- 学科或模块影响星团位置；
- 极高影响力论文会被标记为黑洞；
- 高排名且高引用论文可能成为戴森球；
- 同模块、距离较近的论文会被连接；
- 时间线回放展示领域演化。

系统并不宣称“引用量等于真理”。引用量只是一个可视化代理，用来表示影响力、注意力和学术引力。

## Main formulas / 主要公式

```text
mass   = 1.0 + log10(2 + cited_by_count) * 2.5
radius = 3.0 + log10(2 + cited_by_count) * 2.5
x      = normalized_year_axis + Gaussian jitter
y      = log10(1 + cited_by_count) * 15 + Gaussian jitter
z      = module_offset + Gaussian jitter
```

Black hole rules:

```text
is_blackhole = cited_by_count > mean_cited * 50
or paper is in the top 0.1% by citation rank
```

Dyson sphere rule:

```text
is_dyson = paper is in the top 1% and cited_by_count > mean_cited * 10
```

See `docs/ACE_Omega_Manual.pdf` for the original technical manual.
