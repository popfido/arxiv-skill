# Paper Analysis Framework

Use this framework when the user asks for a deep analysis of one arXiv paper or a comparison across several papers.

## Workflow

1. Confirm the paper ID or search for it.
2. Cache the paper locally if the markdown file does not exist.
3. Read the cached markdown.
4. Search for adjacent or competing papers if context would improve the answer.
5. Produce the final analysis with the structure below.

## Output structure

1. Executive summary
2. Research context
3. Methodology analysis
4. Results analysis
5. Limitations and failure modes
6. Practical implications
7. Future directions

## Guidance

### Executive summary

- State the problem the paper addresses.
- State the core contribution.
- State the main methodological move.
- State the headline result.

### Research context

- Place the paper within its research area.
- Identify the prior baseline or competing approaches.
- Explain what gap the paper claims to close.

### Methodology analysis

- Break down the method step by step.
- Note assumptions, datasets, and modeling choices.
- Call out implementation details that would matter for replication.

### Results analysis

- Describe benchmarks, metrics, and comparison points.
- Assess whether the reported results actually support the paper's claims.
- Flag weak baselines, narrow evaluation, or missing ablations when relevant.

### Limitations and failure modes

- Identify explicit limitations from the paper.
- Add any important implicit limitations visible from the method or evaluation.

### Practical implications

- Explain where the paper could realistically be applied.
- Note missing code, data, or resource assumptions that affect adoption.

### Future directions

- Suggest plausible follow-up work.
- Connect the paper to adjacent lines of research when useful.
