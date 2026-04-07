# GEO Audit Environment - Data Collection Guide for Hari

## Your Role

You are collecting and labeling 60 webpages that will train an AI to find GEO problems.

**This is the most important part of the project.** Without good data, the AI learns nothing.

---

## What is GEO?

```
SEO = Getting ranked in Google search results
GEO = Getting cited by AI assistants (ChatGPT, Perplexity, Claude)

EXAMPLE:
Someone asks ChatGPT: "How do I stake Ethereum?"
ChatGPT answers and says: "According to QuickNode..."

GEO = Making sure YOUR website is the one AI cites
```

---

## What You're Looking For

When you look at a webpage, ask yourself:

> "If an AI was trying to answer a question, would this page be a good source?"

**Good sources have:**
- Clear, direct answers
- Structured content (headers, lists)
- Schema markup (helps AI understand the page)
- Trust signals (author name, date)

**Bad sources have:**
- Vague introductions that don't answer questions
- Wall of text with no structure
- No schema markup
- No author or date

---

## The 60 Pages You Need

| Task | Difficulty | Pages | Description |
|------|------------|-------|-------------|
| Task 1 | Easy | 20 | Pages with OBVIOUS problems |
| Task 2 | Medium | 20 | Pages with SUBTLE problems |
| Task 3 | Hard | 20 | Pages for COMPETITIVE analysis |

---

## Issue Types Cheat Sheet

### CRITICAL Issues (Must Fix)

| Issue | What It Means | How To Spot It |
|-------|---------------|----------------|
| `missing_meta_description` | No meta description tag | View Source → search `<meta name="description"` → not found |
| `missing_title_tag` | No title tag | Look at browser tab - if blank or generic |
| `no_direct_answer` | Page doesn't answer the query upfront | Read first paragraph - is the answer there? |

### HIGH Issues (Should Fix)

| Issue | What It Means | How To Spot It |
|-------|---------------|----------------|
| `buried_answer` | Answer exists but hidden deep | Answer is in paragraph 5+ instead of paragraph 1 |
| `missing_faq_schema` | Has FAQ content but no markup | Page has Q&A but schema validator shows no FAQPage |
| `missing_howto_schema` | Tutorial without HowTo markup | Has steps 1, 2, 3 but no HowTo schema |
| `no_headers` | Wall of text, no H2/H3 | Page is just paragraphs with no section headings |

### MEDIUM Issues (Nice To Fix)

| Issue | What It Means | How To Spot It |
|-------|---------------|----------------|
| `weak_meta_description` | Meta exists but doesn't match query | Description says "Welcome to our site" instead of answering query |
| `weak_title_tag` | Title exists but doesn't include keywords | Title is generic like "Blog Post" |
| `thin_content` | Not enough depth | Under 500 words for an informational query |
| `missing_article_schema` | Blog post without Article schema | It's clearly an article but no Article schema |
| `no_author` | No author attribution | Can't find who wrote this |
| `no_date` | No publish/update date | No date visible anywhere |

### LOW Issues (Optional)

| Issue | What It Means | How To Spot It |
|-------|---------------|----------------|
| `no_sources` | Makes claims without citations | Says "studies show..." but no links |
| `poor_header_structure` | Headers exist but are messy | H3 before H2, or headers don't make sense |

---

## How To Analyze A Page

### Step 1: Pick a Page and Query

First, decide:
- What URL are you analyzing?
- What question SHOULD this page answer?

Example:
```
URL: https://quicknode.com/guides/ethereum/staking
Query: "how to stake ethereum"
```

### Step 2: Check Title Tag

**Where to look:** Browser tab, or View Source → search `<title>`

**Questions to ask:**
- Does the title exist?
- Does it include the query keywords?
- Is it descriptive?

**Examples:**
```
BAD:  "Staking Guide" (too generic)
BAD:  "QuickNode" (no keywords)
GOOD: "How to Stake Ethereum: Complete Guide | QuickNode"
```

### Step 3: Check Meta Description

**Where to look:** View Source → search `<meta name="description"`

**Questions to ask:**
- Does it exist?
- Does it describe what the page answers?
- Would an AI want to cite this?

**Examples:**
```
BAD:  (empty/missing)
BAD:  "Welcome to QuickNode, a blockchain infrastructure company."
GOOD: "Learn how to stake Ethereum in 5 steps. This guide covers validator setup, 32 ETH requirement, and expected rewards."
```

### Step 4: Check First Paragraph

**Where to look:** Read the first 100 words of the page

**Questions to ask:**
- Does it answer the query directly?
- Or does it start with fluff/company intro?

**Examples:**
```
BAD:  "QuickNode was founded in 2017 with a mission to make blockchain accessible..."
GOOD: "To stake Ethereum, you need to deposit 32 ETH into the deposit contract and run a validator node. Here's how to do it step by step..."
```

### Step 5: Check Headers

**Where to look:** Scan the page for H2/H3 headings

**Questions to ask:**
- Are there clear section headers?
- Do they help someone find information?
- Or is it a wall of text?

**Examples:**
```
BAD:  No headers, just paragraphs
BAD:  Headers like "Section 1", "Section 2"
GOOD: "H2: Requirements", "H2: Step-by-Step Guide", "H2: Expected Rewards"
```

### Step 6: Check Schema Markup

**Where to look:** https://validator.schema.org/ - paste the URL

**Questions to ask:**
- Does the page have any schema?
- Is it missing schema it SHOULD have?

**Schema types to look for:**
```
FAQ page → Should have FAQPage schema
Tutorial → Should have HowTo schema
Blog post → Should have Article schema
Product → Should have Product schema
```

### Step 7: Check Word Count

**Where to look:** Copy text into wordcounter.net or estimate

**Questions to ask:**
- Is there enough depth?
- Under 300 words = definitely thin
- Under 500 words = probably thin for guides

### Step 8: Check Trust Signals

**Where to look:** Look for author name, date, sources

**Questions to ask:**
- Who wrote this?
- When was it published/updated?
- Are claims backed by sources?

---

## Google Sheet Template

Create a Google Sheet with these columns:

| Column | What To Enter |
|--------|---------------|
| A: page_id | easy_001, easy_002, medium_001, etc. |
| B: url | Full URL of the page |
| C: target_query | The question this page should answer |
| D: difficulty | easy, medium, or hard |
| E: title_tag | Copy the title tag text |
| F: meta_description | Copy the meta description (or "MISSING") |
| G: h1 | Copy the H1 heading |
| H: first_paragraph | First 200 characters |
| I: word_count | Approximate word count |
| J: headers | List of H2s like "H2: About, H2: Steps" |
| K: schema_types | What schemas exist, or "NONE" |
| L: has_author | TRUE or FALSE |
| M: has_date | TRUE or FALSE |
| N: issue_1 | First issue type |
| O: issue_1_severity | critical/high/medium/low |
| P: issue_2 | Second issue type (if any) |
| Q: issue_2_severity | Severity |
| R: issue_3 | Third issue type (if any) |
| S: issue_3_severity | Severity |
| T: good_elements | What's good about this page |
| U: notes | Any other notes |

---

## Examples of Labeled Pages

### Example 1: Easy (Obvious Problems)

```
page_id: easy_001
url: https://random-crypto-blog.com/staking
target_query: how to stake ethereum
difficulty: easy

title_tag: Crypto Blog
meta_description: MISSING
h1: Welcome to Our Blog
first_paragraph: We are a team of crypto enthusiasts who love blockchain technology. In this post, we will discuss various topics...
word_count: 320
headers: NONE
schema_types: NONE
has_author: FALSE
has_date: FALSE

issue_1: missing_meta_description
issue_1_severity: critical

issue_2: no_direct_answer
issue_2_severity: critical

issue_3: no_headers
issue_3_severity: high

issue_4: thin_content
issue_4_severity: medium

issue_5: missing_howto_schema
issue_5_severity: high

good_elements: None really

notes: Classic bad page - no structure, no answer, no SEO basics
```

### Example 2: Medium (Subtle Problems)

```
page_id: medium_001
url: https://decent-exchange.com/guides/eth-staking
target_query: how to stake ethereum
difficulty: medium

title_tag: Ethereum Staking Guide | Decent Exchange
meta_description: Learn about Ethereum staking on Decent Exchange
h1: Ethereum Staking Guide
first_paragraph: Ethereum staking is a way to earn rewards on your ETH holdings. Staking involves locking up your ETH to help secure the network...
word_count: 1200
headers: H2: What is Staking, H2: Benefits, H2: How to Stake, H2: Risks
schema_types: Article
has_author: TRUE
has_date: FALSE

issue_1: weak_meta_description
issue_1_severity: medium
(meta exists but doesn't answer "how to" - just says "learn about")

issue_2: no_date
issue_2_severity: medium

issue_3: missing_howto_schema
issue_3_severity: high
(has step-by-step content but only Article schema, no HowTo)

good_elements: title_tag, headers, word_count, has_author

notes: Looks decent at first glance but missing key schema and weak meta
```

### Example 3: Hard (Competitive Analysis)

```
page_id: hard_001
url: https://our-client.com/ethereum-staking
target_query: how to stake ethereum
difficulty: hard
competitor_url: https://top-ranking-site.com/stake-eth

ANALYSIS OF OUR CLIENT:
title_tag: How to Stake Ethereum | Our Client
meta_description: Step-by-step guide to staking Ethereum
h1: Ethereum Staking Tutorial
word_count: 1500
headers: H2: Overview, H2: Steps, H2: FAQ
schema_types: Article, HowTo
has_author: TRUE
has_date: TRUE

COMPETITOR HAS:
- FAQPage schema (we don't)
- Video embed with VideoObject schema
- 2500 words (more comprehensive)
- Updated more recently
- More internal links

issue_1: competitor_has_faq_schema
issue_1_severity: high
(competitor has FAQPage schema, we only have Article + HowTo)

issue_2: competitor_more_comprehensive
issue_2_severity: medium
(competitor has 2500 words vs our 1500)

issue_3: missing_video_schema
issue_3_severity: medium
(competitor has video content with schema)

good_elements: title_tag, meta_description, has_howto_schema, has_author, has_date

notes: Our page is good but competitor outranks because of richer schema and more depth
```

---

## Where To Find Pages

### For EASY (Obvious Issues)

Look for bad pages:
- Google page 4-5 results for your query
- Old blog posts from small sites
- Forums with user-generated content
- Sites with no SEO at all

**Tip:** Search for queries like:
- "how to [crypto topic]"
- "what is [blockchain term]"
- "best [web3 tool]"

Then scroll to page 3-5 of Google.

### For MEDIUM (Subtle Issues)

Look for decent pages with hidden problems:
- Google page 1-2 results
- Medium.com articles
- Company blogs that look okay
- Sites with some SEO but not great

**Tip:** These pages LOOK fine but:
- Meta description doesn't match query
- Missing specific schema types
- No date or outdated
- Answer buried after intro

### For HARD (Competitive)

Compare two competing pages:
- Pick a query
- Find #1 result and #5 result
- Analyze why #1 is better
- Document the differences

**Tip:** Use queries related to:
- Unhashed clients (QuickNode, Alto IRA, etc.)
- Popular crypto topics
- Web3 tools and services

---

## Tools You'll Need

### 1. Schema Validator
https://validator.schema.org/

Paste URL → See what schemas exist

### 2. View Page Source
Right-click → View Page Source

Search for:
- `<title>` 
- `<meta name="description"`
- `application/ld+json` (schema)

### 3. Word Counter
https://wordcounter.net/

Paste text → Get word count

### 4. Google Search
Find pages at different quality levels

---

## Timeline

```
HOURS 1-3: Task 1 (Easy)
├── Find 20 pages with obvious issues
├── Label each one
├── Add to Google Sheet

HOURS 3-6: Task 2 (Medium)  
├── Find 20 pages with subtle issues
├── Label each one
├── Add to Google Sheet

HOURS 6-10: Task 3 (Hard)
├── Find 10 page pairs (our page vs competitor)
├── Analyze differences
├── Document why competitor wins
├── Add to Google Sheet

HOURS 10-12: Review
├── Double-check all entries
├── Make sure no duplicates
├── Export and send to Hijak
```

---

## Checklist

```
TASK 1 (EASY):
☐ easy_001 labeled
☐ easy_002 labeled
☐ easy_003 labeled
☐ easy_004 labeled
☐ easy_005 labeled
☐ easy_006 labeled
☐ easy_007 labeled
☐ easy_008 labeled
☐ easy_009 labeled
☐ easy_010 labeled
☐ easy_011 labeled
☐ easy_012 labeled
☐ easy_013 labeled
☐ easy_014 labeled
☐ easy_015 labeled
☐ easy_016 labeled
☐ easy_017 labeled
☐ easy_018 labeled
☐ easy_019 labeled
☐ easy_020 labeled

TASK 2 (MEDIUM):
☐ medium_001 labeled
☐ medium_002 labeled
... (same pattern)
☐ medium_020 labeled

TASK 3 (HARD):
☐ hard_001 labeled
☐ hard_002 labeled
... (same pattern)
☐ hard_020 labeled

FINAL:
☐ All 60 pages in Google Sheet
☐ No empty cells
☐ Shared with Hijak
```

---

## Quick Reference Card

```
WHEN YOU SEE...                         FLAG AS...
──────────────────────────────────────────────────────────
No <meta name="description">        →   missing_meta_description (CRITICAL)
Meta doesn't match query            →   weak_meta_description (MEDIUM)
No <title> tag                      →   missing_title_tag (CRITICAL)
Title is generic                    →   weak_title_tag (MEDIUM)
Answer not in first 100 words       →   no_direct_answer (CRITICAL)
Answer buried in paragraph 5+       →   buried_answer (HIGH)
Has FAQ but no FAQPage schema       →   missing_faq_schema (HIGH)
Has steps but no HowTo schema       →   missing_howto_schema (HIGH)
No H2/H3 headers                    →   no_headers (HIGH)
Under 500 words                     →   thin_content (MEDIUM)
No author name                      →   no_author (MEDIUM)
No date                             →   no_date (MEDIUM)
Claims without sources              →   no_sources (LOW)
```

---

## Questions?

If you're unsure about something:
1. Take your best guess
2. Add a note in the "notes" column
3. Hijak will review and clarify

**Remember:** Your judgment as a human is the ground truth. The AI will learn from YOUR labels.

Good luck! 🚀
