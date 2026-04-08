# Decision Briefing System

## Overview

A structured system for creating concise decision-support briefs from multiple information sources (documents, agent recommendations, coordination results).

## Philosophy

**The reader should be able to understand and make a decision within 2 minutes.**

Key principle: BLUF-first (Bottom Line Up Front). The most important information comes first, details follow only if needed.

## Directory Structure

```
data/briefing/
├── input/              # Source materials (documents, screenshots, logs)
├── briefs/             # Generated briefs (markdown files)
└── templates/          # Brief templates (different formats for different contexts)
```

## Workflow

### Input Stage
Creator sends files through:
- Direct file upload to `data/briefing/input/`
- Shared document links (I'll fetch via wget/curl)
- Text/paste directly in chat

### Processing Stage
I create a brief with:
1. **Executive Summary** (1-2 sentences, <50 words)
2. **Context** (what is this about?)
3. **Key Findings** (3-5 bullet points max)
4. **Options Table** (risks, benefits, confidence)
5. **Recommendation** (what should we do?)
6. **Next Steps** (concrete actions)

### Output Stage
Brief delivered in:
- Markdown format in `data/briefing/briefs/`
- Git commit with detailed message
- Push to GitHub

## Standard Brief Template

```markdown
# Executive Summary
[Sentence 1: What is this about and what's the main decision?]
[Sentence 2: What do we recommend?]

# Context
[Background information: who, what, when, where, why]

# Key Findings
- 🟢 [Positive finding]
- 🟡 [Neutral/Uncertain finding]
- 🔴 [Critical issue finding]

# Options

| Option | Risk | Benefit | Confidence |
|--------|------|----------|-------------|
| Option A | 🟢 Low | Benefit 1 | High |
| Option B | 🟡 Medium | Benefit 2 | Medium |
| Option C | 🔴 High | Benefit 3 | Low |

# Recommendation
**[Recommended option]** - Brief rationale

# Next Steps
1. [Concrete step 1]
2. [Concrete step 2]
3. [Concrete step 3 (if applicable)]
```

## Style Guidelines

### Length
- Total length: ≤ 2 pages when printed
- Executive summary: < 50 words
- Each section: concise, no fluff

### Clarity
- Use simple language (boardroom vocabulary)
- Be specific: "Q3 revenue 15% above target" not "revenue improved"
- Numbers: always include units, context, and comparison

### Risk Emoji System
- 🟢 Green: Low risk / Good news
- 🟡 Yellow: Medium risk / Uncertain / Requires monitoring
- 🔴 Red: High risk / Critical / Immediate attention needed

### What NOT to Include
- Prose without conclusions
- Background without impact
- Technical details without business relevance
- Vague statements ("needs further research")

## Git Integration

Every brief gets a dedicated commit:

```
feat: brief - "Brief Title"

Summary: [Brief summary]

Input files: [list]

- Input: x.pdf, y.txt
- Context: T_zzz recommendation from Agent A
- Coordination: Approved by [person] on [date]
```

## Calibration Period

First 3-5 briefs are for calibration. During this period:

1. **I'll ask questions** to understand your preferences
2. **Format evolution** - templates may change based on feedback
3. **Length tuning** - adjusting based on what works for you

After calibration, I'll lock in a template that matches your style - but always open to refinement.

## Anti-Patterns

### ❌ Instead of this:
```markdown
## Context
Here's a lot of background about the project history,
the team structure, the technology stack, and why
we're considering this decision... (3 paragraphs)
```

### ✅ Do this:
```markdown
## Context
We need to choose an ORM for the new microservice. Current stack:
- Python 3.11, FastAPI
- Postgres DB
- Team: 2 backend devs
```

### ❌ Instead of this:
```markdown
## Findings
Option A looks interesting because it has good features.
Option B also has some merit. We might want to consider more.
```

### ✅ Do this:
```markdown
## Findings
- 🟢 Option A: Performant, team familiar (used in 2 previous projects)
- 🟡 Option B: Good async support, but learning curve
- 🔴 Option C: No documentation, maintenance burden
```

## Status

- ✅ System structure created
- ✅ Standard template defined
- ✅ Git workflow configured
- ⚠️ **Awaiting first input file** from creator
- ⚠️ **No web search** (requires OPENAI_API_KEY)
- ⚠️ **VLM for PDF** not yet tested

## Next Steps for Evolution

1. Practice with first creator input (real brief)
2. Test VLM for document analysis (if keys become available)
3. Investigate document parsing (PDF → text) utilities
4. Create specialized templates (finance, tech, HR, etc.)
5. Develop prompt engineering best practices for accurate summarization

## Knowledge Base

See `memory/knowledge/decision-briefing.md` for:
- Recipes and patterns (what works)
- Gotchas and anti-patterns (what to avoid)
- Template evolution history