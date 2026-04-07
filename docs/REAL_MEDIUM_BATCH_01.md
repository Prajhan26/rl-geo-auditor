# Real Medium Pages — Batch 01

These are **real live candidate pages** for the first medium-difficulty review
batch.

Important:

* these are review candidates, not final labels
* live pages can change
* before moving any of these into `data/`, manually confirm:
  * visible page fields
  * likely issue labels
  * whether the page still fits medium difficulty

## 1. Ethereum.org — Home stake your ETH

* URL: https://ethereum.org/staking/solo/
* Suggested target query: `how to stake ethereum from home`
* Why it fits medium:
  * strong official page
  * instructional structure
  * likely useful for checking direct-answer behavior and schema expectations
* Review for:
  * `missing_howto_schema`
  * `missing_faq_schema`
  * `no_sources`
  * whether the opening paragraph is direct enough for the query

## 2. Ethereum.org — Pooled staking

* URL: https://ethereum.org/staking/pools/
* Suggested target query: `what is pooled ethereum staking`
* Why it fits medium:
  * clear educational content
  * structured sections
  * FAQ-style cues
* Review for:
  * `missing_faq_schema`
  * `no_sources`
  * `weak_meta_description`

## 3. Lido — FAQ

* URL: https://lido.fi/faq
* Suggested target query: `lido staking faq`
* Why it fits medium:
  * strong FAQ-style page
  * good candidate for FAQ structure and source/trust review
* Review for:
  * `missing_faq_schema`
  * `no_sources`
  * whether author/date/trust signals are visible enough

## 4. Blocknative — Ethereum Liquid Staking Guide

* URL: https://www.blocknative.com/blog/ethereum-liquid-staking-guide
* Suggested target query: `ethereum liquid staking guide`
* Why it fits medium:
  * long-form educational article
  * likely mixed-quality signals rather than obvious flaws
* Review for:
  * `weak_meta_description`
  * `buried_answer`
  * `missing_faq_schema`
  * `no_date`
  * `no_sources`

## 5. Ethereum.org — General staking overview

* URL: https://ethereum.org/staking/
* Suggested target query: `ethereum staking guide`
* Why it fits medium:
  * broad overview page
  * useful baseline official page for labeling discipline
* Review for:
  * direct answer vs overview wording
  * `missing_article_schema`
  * `missing_faq_schema`
  * whether it should be labeled clean

## Recommended Next Step

For each page above:

1. open the page manually
2. record the page fields into a draft JSON row
3. write the likely labels in a separate note
4. only then add it into `data/`

This keeps the real benchmark trustworthy.
