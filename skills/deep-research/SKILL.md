---
name: deep-research
description: Use when the user needs multi-source research with citation tracking, evidence persistence, and structured report generation. Triggers on "deep research", "comprehensive analysis", "research report", "compare X vs Y", "analyze trends", or "state of the art". Not for simple lookups, debugging, or questions answerable with 1-2 searches.
context: fork
---

# Deep Research

## Core Purpose

Deliver citation-tracked research reports through a structured pipeline. Depth and rigor scale by mode — from focused multi-source analysis to comprehensive verified research with evidence persistence and claim-level verification.

---

## Decision Tree

```
Request Analysis
+-- Simple lookup? --> STOP: Use WebSearch
+-- Debugging? --> STOP: Use standard tools
+-- Complex analysis needed? --> CONTINUE to Mode Selection
```

---

## Mode Selection (MANDATORY — must happen before any research work)

**Before executing any phase, call AskUserQuestion ONCE with exactly 2 questions.**

```
AskUserQuestion(questions=[
  {
    "question": "Choose a research depth level for this topic:",
    "header": "Depth",
    "multiSelect": false,
    "options": [
      {"label": "Standard Research (Recommended)", "description": "6 phases, 5-10 min. Cross-verification and synthesis. Most research questions."},
      {"label": "Deep Analysis", "description": "8 phases, 10-20 min. Rigorous verification with red-team critique."},
      {"label": "UltraDeep Review", "description": "8+ phases, 20-45 min. Academic-level thoroughness, maximum rigor."}
    ]
  },
  {
    "question": "Select output format(s):",
    "header": "Format",
    "multiSelect": true,
    "options": [
      {"label": "Terminal Only", "description": "Output in conversation, no files written"},
      {"label": "Markdown", "description": "Save .md to ~/Documents/[Topic]_Research_[YYYYMMDD]/"},
      {"label": "HTML", "description": "McKinsey-style .html, auto-open in browser"},
      {"label": "PDF", "description": "Professional print-quality .pdf, auto-open"}
    ]
  }
])
```

**Behavior:**
- Recommend **Standard** as default for Q1
- Q2 MUST have `multiSelect: true` — user can pick any combination
- If user selects only "Terminal Only": output report in conversation, no files written
- If user's message implies a depth level (e.g., "全面深入分析" → Deep, "论文级综述" → UltraDeep), pre-select it but still confirm
- After both answered, proceed with Phase 1

**Default assumptions:** Technical query = technical audience. Comparison = balanced perspective. Trend = recent 1-2 years.

---

## Workflow Overview

| Phase | Name | Std | Deep | Ultra |
|-------|------|-----|------|-------|
| 1 | SCOPE | Y | Y | Y |
| 2 | PLAN | - | Y | Y |
| 3 | RETRIEVE | Y | Y | Y |
| 4 | TRIANGULATE | Y | Y | Y |
| 4.5 | OUTLINE REFINEMENT | Y | Y | Y |
| 5 | SYNTHESIZE | Y | Y | Y |
| 6 | CRITIQUE | - | Y | Y |
| 7 | REFINE | - | Y | Y |
| 8 | PACKAGE | Y | Y | Y |

**Note:** Phases 3-5 are iterative — retrieve, analyze, supplement, triangulate. For Deep/UltraDeep, evidence is persisted to files between iterations.

---

## Execution

**On invocation, load relevant reference files:**

1. **Phase 1-7:** Load [methodology.md](./reference/methodology.md) for detailed phase instructions
2. **Phase 8 (Report):** Load [report-assembly.md](./reference/report-assembly.md) for progressive generation
3. **HTML/PDF output:** Load [html-generation.md](./reference/html-generation.md)
4. **Quality checks:** Load [quality-gates.md](./reference/quality-gates.md)
5. **Long reports (>18K words):** Load [continuation.md](./reference/continuation.md)

**Templates:**
- Report structure: [report_template.md](./templates/report_template.md)
- HTML styling: [mckinsey_report_template.html](./templates/mckinsey_report_template.html)

**Scripts:**
- `python scripts/validate_report.py --report [path]`
- `python scripts/verify_citations.py --report [path]`
- `python scripts/md_to_html.py [markdown_path]`
- `python scripts/citation_manager.py init-run --out-dir [dir] --query "[q]" --mode [mode]`
- `python scripts/extract_claims.py --report [path]`
- `python scripts/verify_claim_support.py verify --dir [dir]`

---

## Output Contract

**Required sections:**
- Executive Summary (200-400 words)
- Introduction (scope, methodology, assumptions)
- Main Analysis (standard: 4-6 findings, 600-1,500 words each; deep/ultradeep: 6-8 findings, 600-2,000 words each, cited)
- Synthesis & Insights (patterns, implications)
- Limitations & Caveats
- Recommendations
- Bibliography (COMPLETE - every citation, no placeholders)
- Methodology Appendix

**Output (based on user's format selection):**
- If "仅终端展示" selected: output full report in conversation, no files written
- If "Markdown" selected: save .md file to `~/Documents/[Topic]_Research_[YYYYMMDD]/`
- If "HTML" selected: generate McKinsey-style .html, auto-open in browser
- If "PDF" selected: generate professional .pdf, auto-open
- Users can combine multiple formats (e.g., Markdown + HTML)

**Evidence & metadata files** (when file output is selected, mode-dependent):
- `sources.jsonl` — stable source registry with canonical IDs
- `evidence.jsonl` — append-only evidence store with quotes and locators (Deep/UltraDeep recommended)
- `claims.jsonl` — atomic claim ledger with support status (UltraDeep required)
- `run_manifest.json` — query, mode, assumptions, output format

**Quality standards:**
- 10+ sources, 3+ per major claim
- All factual claims cited immediately [N]
- No placeholders, no fabricated citations
- Prose-first (>=80%), bullets sparingly
- Claim-support verification via `verify_claim_support.py` (Deep/UltraDeep when evidence files exist)

---

## When to Use / NOT Use

**Use:** Comprehensive analysis, technology comparisons, state-of-the-art reviews, multi-perspective investigation, market analysis.

**Do NOT use:** Simple lookups, debugging, 1-2 search answers.
