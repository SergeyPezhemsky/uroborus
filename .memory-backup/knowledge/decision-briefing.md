# Decision Briefing / Executive Summary - Best Practices

## Purpose
Create concise summaries that support decision-making, not just information transfer.

**Core principle:** The reader should be able to understand the situation, options, and recommendation in < 5 minutes.

## Structure (Bluf - Bottom Line Up Front)

### 1. Executive Summary (1-2 sentences)
**The decision required and the recommended action.**

Example: "Approve vendor A for implementation of payment gateway at $15K/month. This reduces fraud costs by 30%."

### 2. Context/Background (2-3 bullets)
- What's the situation?
- Why now? (urgency/trigger)
- Constraints (budget, timeline, dependencies)

### 3. Problem/Objective (1 sentence)
What are we trying to solve or achieve?

### 4. Analysis/Key Findings (3-5 bullets)
- Relevant data/trends
- Risks and opportunities
- Dependencies on other decisions
- What alternatives were considered

### 5. Options (2-4 options)
For each option:
- Brief description (1 line)
- Pros (2-3 bullets max)
- Cons (2-3 bullets max)
- Cost/impact (1 line)

### 6. Recommendation (1-2 sentences)
The recommended path and why it's better than alternatives.

### 7. Next Steps (2-5 bullets)
- Who does what
- When
- What approvals needed
- Dependencies

## Formatting Rules

### Length
- **Total: 1-2 pages maximum**
- Each section: 30-100 words (except tables if needed)
- Executive summary: < 50 words

### Tone
- **Objective, slightly opinionated** (recommendations need conviction)
- No hedging ("maybe," "could be," "seems like")
- Use data where available (#s, dates, costs)

### Visuals
- Use tables for options comparison
- Simple diagrams if critical (but avoid if text works)
- Color coding: green = go, yellow = caution, red = stop

### Red Flags (always call out)
- Budget overruns
- Timeline delays
- Missing data (not "we don't know" but "data needed: X, Y")
- Political/stakeholder risks

## Anti-Patterns to Avoid

❌ Information dump without structure
❌ Skipping to recommendation without context
❌ Buried lead (recommendation at the end)
❌ Generic "options" without analysis
❌ No clear call to action
❌ Missing next steps ("we'll figure it out later")

## Rusty Observations (Personal)

**Hypothesis 1:** Decision-makers scan, don't read. The structure above assumes:
1. They read the executive summary first
2. If unclear, they jump to context
3. If skeptical, they check alternatives
4. If convinced, they jump to next steps

**Hypothesis 2 (to test):** Different orgs prefer different depths:
- Large corp: more risk quantification, sign-offs
- Startup/consumer: "just tell me what to do"
- Tech/eng: technical debt analysis
- Finance: NPV calculations (should I learn this?)

**Next research areas:**
- How do different industries differ?
- What's too long? What's too short?
- Examples of bad briefs to avoid repeating
- Decision frameworks beyond pros/cons (e.g., decision matrices)

--- 

*Created: 2026-04-07 (Evolution task: decision-briefing)*
## Context-Aware Variations (Research in Progress)

### Startup Style (Observed Pattern)
- **Total:** 10-15 bullets max, ~150-200 words
- **Focus:** "Just tell me what to do"
- Structure:
  1. Recommendation (1 sentence)
  2. Why now? (1 sentence)
  3. Top 3 risks (bullets)
  4. 3-5 next steps (who, what, when)

### Corporate Style (Observed Pattern)
- **Total:** 1-2 pages, structured sections
- **Focus:** Risk mitigation and审批 chain
- Structure (as in main section above)
- Additions:
  - Risk likelihood/impact matrix
  - Alternative analysis deeper
  - Required approvals section

### Tech/Eng Style (Observed Pattern)
- **Focus:** Technical debt vs. delivery
- Additions:
  - Tech debt impact if NOT doing
  - Impact of timeline/scope trade-offs
  - Dependencies on other technical decisions

### Finance Style (Observed Pattern)
- **Focus:** Return and payback period
- Additions:
  - NPV calculation (when multi-year decision)
  - Payback period
  - Sensitivity analysis (what if X changes)

## Visual Hierarchy Rules (Updated)

### Scanning-Friendly Formatting
- **Bold key numbers:** costs ($), dates, percentages, timelines
- **Symbols for quick signals:** 🟢 = go, 🟡 = caution, 🔴 = stop
- **Tables for options comparison:** (not just bullet lists)
  ```markdown
  | Option | Cost | Risk | Timeline | Key Pros |
  |--------|------|------|----------|----------|
  | A      | $50K | 🟡   | 2 mo     | Fast, proven |
  | B      | $80K | 🟢   | 4 mo     | Scalable |
  ```

### Length Guidelines
- **Total:** 1-2 pages max (main principle)
- **Executive summary:** < 50 words
- **Each section:** 30-100 words (except tables)
- **Options tbl:** Fit on 1 page (max 4 columns)

## Global Observations (Hypotheses to Test)

### Hypothesis 1: Scanning, Not Linear Reading
**Pattern:** Decision-makers jump between sections, not read sequentially
- Executive summary → likely first stop
- If unclear → jump to context
- If skeptical → check alternatives
- If convinced → jump to next steps

**Implication:** Use headings, bold, tables to make jumps efficient

### Hypothesis 2: Less Options = Better Decisions
**Pattern:** 3-4 options max. More = analysis paralysis.
- Present only viable options
- Explicitly call out "rejected options" and why (2-3 lines each)

### Hypothesis 3: Conviction > Balance
**Pattern:** Hedging reduces trust ("could be," "seems like")
- State recommendation clearly
- Use data to back it
- If uncertain: "30% chance of X, data needed: Y" (not "maybe")

### Hypothesis 4: Next Steps are Critical
**Pattern:** "We'll figure it out later" defeats purpose
- Always 2-5 concrete steps
- Include: who, what, when, dependencies
- If blocked by approval: "Approval needed from [role] by [date]"

## Anti-Patterns (Refined)

❌ Too long: >2 pages total = likely not read
❌ Too many options: >4 options = analysis paralysis
❌ Buried lead: recommendation hidden at end = violates BLUF
❌ No next steps: decision without action = half-complete
❌ Missing data as "we don't know": instead, "Data needed: X, Y"
❌ Generic options without analysis: equal pros/cons = signal: do more work

## Ouroboros Working Style (Personal Note)

**Approach when briefing:**
1. Be concise: aim ≤1 page unless creator asks for more detail
2. Be opinionated: pick a path, justify it, show alternatives rejected
3. Be concrete: numbers, dates, owners (no "someone will do it")
4. Use tables when comparing options (scanning > reading)
5. Highlight red flags explicitly (🔴) and yellow cautions (🟡)

**Trigger questions for style calibration:**
- Length preference? (short bullets vs full sections)
- Detail preference? (high-level summary vs data)
- Decision context? (startup vs corporate vs one-off)

---
## Tools and Templates (Evolution #2)

### Common Frameworks

**1. RAPID Decision Framework (Bain)**
- **R**ecommend — recommends course of action
- **A**gree — must agree to proceed (veto power)
- **P**erform — executes decision
- **I**nput — consulted, provides data
- **D**ecide — single decision-maker

Useful when: cross-functional decisions with multiple stakeholders.
Add to brief: "Roles" section mapping stakeholders to RAPID.

**2. Decision Matrix (vs. Pros/Cons)**
- Rows: criteria (cost, risk, timeline, strategic fit)
- Columns: options
- Cells: score (1-5) or qualitative (High/Med/Low)
- Totals row for quantitative comparison

Use when: >2 complex options with multiple trading factors.

**3. Pre-Mortem (Risk Analysis)**
- Instead of "what could go wrong?", ask: "it failed 6 months from now — why?"
- Brief addition: "If this fails, it's likely because of: X, Y, Z"

Use when: high-stakes decisions with significant unknowns.

### Template Checklist (Before Sending to Creator)

**Structural:**
- [ ] Executive summary first (BLUF)
- [ ] Context clear (what and why now)
- [ ] Options limited to 3-4 viable
- [ ] Recommendation stated clearly
- [ ] Next steps concrete (who, what, when)

**Formatting:**
- [ ] Bold key numbers ($, %, dates)
- [ ] Tables for option comparison (if >2 options)
- [ ] Color/emoji signals (🟢🟡🔴) for risks
- [ ] Total length ≤2 pages unless specifically requested

**Content quality:**
- [ ] Data-based (not "I think" but "data shows X")
- [ ] Risks called out explicitly
- [ ] Alternatives rejected explained briefly
- [ ] No unknowns presented as "we don't know" → "Data needed: X"

### Notes for Ouroboros Context (Remote vs. In-Person)

**Remote considerations:**
- Briefs are primary comms (no hallway follow-ups)
- Must be self-contained (explicit context for new stakeholders)
- Clearer call to action (no ambiguous nods)

**In-person considerations:**
- Briefs can be shorter (verbal fill-in possible)
- Less need for full context (shared understanding already exists)
- Focus on discussion triggers vs. full analysis

**When style unclear:**
Start with: "Here's a brief in ~200 words. Want more detail on any section?"
- If creator asks "what's the risk?" → dive deeper
- If creator says "sounds good" → keep it concise
- Track pattern over time → calibrate style

--- 
*Updated: 2026-04-07 (Evolution #2: Added frameworks and templates)*