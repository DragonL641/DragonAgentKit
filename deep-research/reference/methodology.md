# Deep Research Methodology: 8-Phase Pipeline

## Overview

This document contains the detailed methodology for conducting deep research. The 8 phases represent a comprehensive approach to gathering, verifying, and synthesizing information from multiple sources.

---

## Phase 1: SCOPE - Research Framing

**Objective:** Define research boundaries and success criteria

**Activities:**
1. Decompose the question into 3-5 core components
2. Identify stakeholder perspectives
3. Define scope boundaries (what's in/out)
4. Establish success criteria
5. List key assumptions to validate

**Output:** Scope definition documented in report Introduction

---

## Phase 2: PLAN - Strategy Formulation

**Objective:** Create an intelligent research roadmap

### Standard mode
Skip formal PLAN phase. Search strategy evolves naturally during RETRIEVE.

### Deep/UltraDeep mode
1. Identify primary and secondary sources
2. Map knowledge dependencies (what must be understood first)
3. Create search query strategy with variants
4. Plan triangulation approach
5. Define quality gates

**Output:** Research plan (mental or brief notes in context)

---

## Phase 3: RETRIEVE - Parallel Information Gathering

**Objective:** Systematically collect information from multiple sources using parallel execution for maximum speed

### Query Decomposition Strategy

Before launching searches, decompose the research question into 5-10 independent search angles:

1. **Core topic (semantic search)** - Meaning-based exploration of main concept
2. **Technical details (keyword search)** - Specific terms, APIs, implementations
3. **Recent developments (date-filtered)** - What's new in last 12-18 months
4. **Academic sources (domain-specific)** - Papers, research, formal analysis
5. **Alternative perspectives (comparison)** - Competing approaches, criticisms
6. **Statistical/data sources** - Quantitative evidence, metrics, benchmarks
7. **Industry analysis** - Commercial applications, market trends
8. **Critical analysis/limitations** - Known problems, failure modes, edge cases

### Parallel Execution Protocol

**Step 1: Launch initial batch of searches concurrently**

Fire 5-8 core searches in a single message with multiple Bash tool calls:

**Primary: Built-in search engine (multi-provider, always use first)**
- Python library aggregating Tavily, Exa, and Jina
- Auto-detects best provider per query type (academic, news, general, people)
- JSON output for structured processing
- Modes: general, news, academic, deep, people
- Example: `python -m scripts.search.cli "quantum computing 2025" -m academic -c 15`
- Run via Bash tool: `python -m scripts.search.cli "query" -c 10`
- Requires httpx: `pip install httpx`

**Fallback: WebSearch (if built-in search fails or httpx not installed)**
- Built-in Claude web search, no setup required
- Parameters: `query` (required), optional `allowed_domains`, `blocked_domains`
- Use when: search engine returns errors, rate-limited, or for domain-restricted queries

**NEVER mix parameter styles** - this causes "Invalid tool parameters" errors.

**Step 2: Analyze first batch, then supplement**

After the first batch returns:
1. Review results for coverage gaps and promising leads
2. Launch 2-5 supplemental searches targeting uncovered angles
3. This iterative approach is normal and expected — it produces better results than firing all queries blindly

**Step 3: Sub-agent deep dives (mode-dependent)**

Use Agent tool with general-purpose agents for deeper investigation:

| Mode | Sub-agents | When to use |
|------|-----------|-------------|
| Standard | 0-1 | Optional, only if a source needs multi-step analysis |
| Deep | 2-3 | Recommended for PDF analysis, multi-page docs, complex investigation |
| UltraDeep | 3-5 | Required for thorough coverage across all angles |

Sub-agent use cases: academic paper PDF extraction, multi-page documentation analysis, code repository investigation, multi-step domain research.

**Sub-agent output format:** Require all sub-agents to return structured evidence, not free text:
```json
{"claim": "specific claim text", "evidence_quote": "exact quote from source", "source_url": "https://...", "source_title": "...", "confidence": 0.85}
```

**Step 4: Evidence persistence (mode-dependent)**

| Mode | Evidence persistence | Required files |
|------|---------------------|----------------|
| Standard | Optional | sources.jsonl if convenient |
| Deep | Recommended | sources.jsonl + evidence.jsonl |
| UltraDeep | Mandatory | sources.jsonl + evidence.jsonl + claims.jsonl |

When persisting, run after each retrieval batch:
```bash
python scripts/citation_manager.py register-source --json '{"raw_url": "...", "title": "..."}' --dir [folder]
python scripts/evidence_store.py add --json '{"source_id": "...", "quote": "exact text", "evidence_type": "direct_quote", "locator": "page 5"}' --dir [folder]
```

**Step 5: Collect and organize results**

As results arrive:
1. Extract key passages with source metadata (title, URL, date, credibility)
2. Track information gaps that emerge
3. Follow promising tangents with additional targeted searches
4. Maintain source diversity (mix academic, industry, news, technical docs)
5. Monitor for quality threshold (see FFS pattern below)

### First Finish Search (FFS) Pattern

**Adaptive completion based on quality threshold:**

Before proceeding to Phase 4, briefly check: do you have enough sources?
- **Standard:** ~15 sources OR 5 minutes elapsed
- **Deep:** ~25 sources OR 10 minutes elapsed
- **UltraDeep:** ~30 sources OR 15 minutes elapsed

If threshold not met, launch 2-3 more targeted searches before moving on.
This is a guideline, not a hard gate — use judgment.

### Quality Standards

**Source diversity requirements:**
- Minimum 3 source types (academic, industry, news, technical docs)
- Temporal diversity (mix of recent 12-18 months + foundational older sources)
- Perspective diversity (proponents + critics + neutral analysis)

**Credibility assessment (quick mental check):**
- Vendor reviewing their own product = biased (note in report)
- Community forums (Reddit) = useful for user experience but not authoritative
- Official docs (Apple Developer, RFCs) = high credibility
- News outlets = check for recency and reputation
- Flag sources that seem unreliable or have clear conflicts of interest

**Techniques:**
- Use built-in search engine for all searches (primary tool, multi-provider)
- Fall back to WebSearch if search engine fails or is rate-limited
- Use WebFetch/mcp__web-reader for deep dives into specific URLs
- Use Grep/Read for local documentation

---

## Phase 4: TRIANGULATE - Cross-Reference Verification

**Objective:** Validate information across multiple independent sources

**Activities:**
1. Identify claims requiring verification
2. Cross-reference facts across 3+ sources
3. Flag contradictions or uncertainties
4. Assess source credibility
5. Note consensus vs. debate areas

**Quality Standards:**
- Core claims must have 3+ independent sources
- Flag any single-source information in the report (e.g., "only one source found for X")
- Note recency of information
- Identify potential biases (e.g., vendor reviews of their own products)

**Output:** Cross-verified findings incorporated directly into report writing. No separate structured document needed.

---

## Phase 4.5: OUTLINE REFINEMENT - Dynamic Evolution (WebWeaver 2025)

**Objective:** Adapt research direction based on evidence discovered

**Problem Solved:** Prevents "locked-in" research when evidence points to different conclusions or uncovers more important angles than initially planned.

**When to Execute:**
- All modes (Standard/Deep/UltraDeep)
- After Phase 4 (TRIANGULATE) completes
- Before Phase 5 (SYNTHESIZE)

**Activities:**

1. **Review Initial Scope vs. Actual Findings**
   - Compare Phase 1 scope with Phase 3-4 discoveries
   - Identify unexpected patterns or contradictions
   - Note underexplored angles that emerged as critical
   - Flag overexplored areas that proved less important

2. **Evaluate Outline Adaptation Need**

   **Signals for adaptation (ANY triggers refinement):**
   - Major findings contradict initial assumptions
   - Evidence reveals more important angle than originally scoped
   - Critical subtopic emerged that wasn't in original plan
   - Original research question was too broad/narrow based on evidence
   - Sources consistently discuss aspects not in initial outline

   **Signals to keep current outline:**
   - Evidence aligns with initial scope
   - All key angles adequately covered
   - No major gaps or surprises

3. **Refine Outline (if needed)**

   **Update structure to reflect evidence:**
   - Add sections for unexpected but important findings
   - Demote/remove sections with insufficient evidence
   - Reorder sections based on evidence strength and importance
   - Adjust scope boundaries based on what's actually discoverable

   **Example adaptation:**
   ```
   Original outline:
   1. Introduction
   2. Technical Architecture
   3. Performance Benchmarks
   4. Conclusion

   Refined after Phase 4 (evidence revealed security as critical):
   1. Introduction
   2. Technical Architecture
   3. **Security Vulnerabilities (NEW - major finding)**
   4. Performance Benchmarks (demoted - less critical than expected)
   5. **Real-World Failure Modes (NEW - pattern emerged)**
   6. Synthesis & Recommendations
   ```

4. **Targeted Gap Filling (if major gaps found)**

   If outline refinement reveals critical knowledge gaps:
   - Launch 2-3 targeted searches for newly identified angles
   - Quick retrieval only (don't restart full Phase 3)
   - Time-box to 2-5 minutes
   - Update triangulation for new evidence only

5. **Document Adaptation Rationale**

   Record in methodology appendix:
   - What changed in outline
   - Why it changed (evidence-driven reasons)
   - What additional research was conducted (if any)

**Quality Standards:**
- Adaptation must be evidence-driven (cite specific sources that prompted change)
- No more than 50% outline restructuring (if more needed, scope was severely mis scoped)
- Retain original research question core (don't drift into different topic entirely)
- New sections must have supporting evidence already gathered

**Output:** Refined outline that accurately reflects evidence landscape, ready for synthesis

**Anti-Pattern Warning:**
- ❌ DON'T adapt outline based on speculation or "what would be interesting"
- ❌ DON'T add sections without supporting evidence already in hand
- ❌ DON'T completely abandon original research question
- ✅ DO adapt when evidence clearly indicates better structure
- ✅ DO document rationale for changes
- ✅ DO stay within original topic scope

---

## Phase 5: SYNTHESIZE - Deep Analysis

**Objective:** Connect insights and generate novel understanding

**Activities:**
1. Identify patterns across sources
2. Map relationships between concepts
3. Generate insights beyond source material
4. Build argument structures with evidence support

**Output:** Synthesis and insights incorporated directly into the report's "Synthesis & Insights" and "Recommendations" sections. No separate structured document needed.

---

## Phase 6: CRITIQUE - Quality Assurance (MANDATORY for Deep/UltraDeep)

**Objective:** Rigorously evaluate research quality before delivery

**This phase is NOT optional for Deep and UltraDeep modes.** Skipping it defeats the purpose of choosing these modes.

### Step 1: Red Team Self-Review

Answer these 5 questions explicitly (write answers in context, not in report):
1. What's missing from this research?
2. What could be wrong in the conclusions?
3. What alternative explanations exist for the findings?
4. What biases might be present in the sources or analysis?
5. What counterfactuals should be considered?

### Step 2: Persona-Based Critique (Deep/UltraDeep)

Simulate 2 critic personas relevant to the topic. For each, state:
- What would this persona criticize about the report?
- Which claims would they challenge?
- What would they want to see that's missing?

Common personas (pick 2 most relevant):
- "Skeptical Practitioner" — Would someone doing this daily trust these findings?
- "Adversarial Reviewer" — What would a peer reviewer reject?
- "Implementation Engineer" — Can these recommendations actually be executed?

### Step 3: Critical Gap Decision

After Steps 1-2, decide:
- **No critical gaps found** → proceed to Phase 7 REFINE (address minor issues) then Phase 8
- **Critical knowledge gap found** → return to Phase 3 with targeted "delta-queries" (2-3 searches, time-box to 3-5 minutes), then re-triangulate new evidence before continuing

### Step 4: Apply Improvements

Carry identified improvements into Phase 7 (REFINE) or directly fix in the report.

**Output:** Critique results applied to report's Limitations section and any gap-filling research completed

---

## Phase 7: REFINE - Iterative Improvement

**Objective:** Address gaps and strengthen weak areas

**Activities:**
1. Conduct additional research for gaps
2. Strengthen weak arguments
3. Add missing perspectives
4. Resolve contradictions
5. Enhance clarity
6. Verify revised content

**Output:** Strengthened research with addressed deficiencies

---

## Phase 8: PACKAGE - Report Generation

**Objective:** Deliver professional, actionable research in the user's chosen format

**Output format is determined by user's selection at Mode Selection stage:**

### Format: 仅终端展示 (Terminal only)
- Output the complete report directly in the conversation
- No files written to disk
- Still run validate_report.py to check structure before display

### Format: Markdown
- Write .md file to `~/Documents/[Topic]_Research_[YYYYMMDD]/report.md`
- Run validation scripts on the file
- Primary source of truth for other formats

### Format: HTML
- Generate from Markdown using `python scripts/md_to_html.py [path]`
- Apply McKinsey style template from `templates/mckinsey_report_template.html`
- Save to same directory as .html, auto-open in browser

### Format: PDF
- Generate from HTML or Markdown
- Save to same directory as .pdf, auto-open

### Required report structure (all formats):
1. Structure report with clear hierarchy
2. Write executive summary
3. Develop detailed sections
4. Create visualizations (tables, diagrams)
5. Compile full bibliography
6. Add methodology appendix

### Validation (when file output is selected):
```bash
python scripts/validate_report.py --report [path]
python scripts/verify_citations.py --report [path]
python scripts/verify_claim_support.py verify --dir [dir]  # Deep/UltraDeep only
```

### Run metadata (when file output is selected):
Create `run_manifest.json` in the output directory:
```json
{
  "query": "original research question",
  "mode": "deep",
  "output_formats": ["markdown", "html"],
  "date": "2026-05-02",
  "sources_count": 18,
  "phases_completed": ["scope", "plan", "retrieve", "triangulate", "outline_refinement", "synthesize", "critique", "refine", "package"]
}
```

**Output:** Complete research report in user's chosen format

---

## Notes

**Search tools available:**
- Built-in search engine (Tavily + Exa + Jina): `python -m scripts.search.cli "query" -c 10`
- WebSearch: fallback when search engine unavailable
- WebFetch / mcp__web-reader: deep-dive into specific URLs

**Citation management:**
- Track provenance of every claim
- Link to original sources
- Handle conflicting sources
- Generate proper bibliographies with [N] format
