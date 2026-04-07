# Real Medium Batch 01 — Reviewed Notes

This file reviews the automatically drafted rows in:

* `artifacts/real_medium_batch_01_draft.json`

The goal is to say:

* what looks good
* what should be corrected
* what should be replaced

## real_medium_001

URL:

* `https://ethereum.org/staking/solo/`

Verdict:

* keep

Corrections:

* `title_tag`: keep `Home stake your ETH | ethereum.org`
* `first_paragraph`: keep the extracted paragraph, not the hero bullets
* `has_author`: change to `false`
* `has_date`: keep `true`
* `has_sources`: keep `true`
* `source_count`: increase to about `6`

Reviewed issues:

* keep `missing_howto_schema`
* add `missing_faq_schema`
* add `no_author`

Notes:

* the page clearly contains step-like instructional content
* the page clearly contains an FAQ section
* visible author attribution is not obvious

## real_medium_002

URL:

* `https://ethereum.org/staking/pools/`

Verdict:

* keep

Corrections:

* `title_tag`: keep `Pooled staking | ethereum.org`
* `first_paragraph`: keep extracted paragraph
* `has_author`: change to `false`
* `has_date`: keep `true`
* `has_sources`: keep `true`
* `source_count`: keep around `4`

Reviewed issues:

* keep `missing_faq_schema`
* keep `weak_meta_description`
* add `no_author`

Notes:

* this is a good medium page because the content is decent but not perfect
* the meta description is probably serviceable but still a bit generic for the exact query

## real_medium_003

URL:

* `https://lido.fi/faq`

Verdict:

* replace candidate

Why:

* this page appears highly dynamic
* the draft parser missed most of the structure
* author/date/source detection is noisy here

Recommendation:

* do not trust the current draft row
* replace this candidate with a more stable page for the first batch

Suggested replacement:

* `https://ethereum.org/staking/pools/`
* or another stable educational article with a simpler DOM

## real_medium_004

URL:

* `https://www.blocknative.com/blog/ethereum-liquid-staking-guide`

Verdict:

* keep

Corrections:

* `title_tag`: keep
* `meta_description`: keep
* `h1`: keep
* `has_author`: keep `true`
* `has_date`: keep `true`
* `has_sources`: keep `true`
* `source_count`: keep high

Reviewed issues:

* remove `missing_article_schema` for now

Notes:

* this looks like a strong long-form article
* the draft issue is too speculative without a more careful schema check
* treat it as likely clean or nearly clean until manual review shows otherwise

## real_medium_005

URL:

* `https://ethereum.org/staking/`

Verdict:

* keep

Corrections:

* `title_tag`: keep
* `meta_description`: keep
* `h1`: keep
* `has_author`: change to `false`
* `has_date`: keep `true`
* `has_sources`: keep `true`
* `source_count`: keep around `4`

Reviewed issues:

* remove `no_direct_answer`
* remove `missing_howto_schema`
* add `no_author`

Notes:

* the opening line answers the topic well enough
* the page is broad and navigational, not a strict step-by-step how-to

## Summary

Recommended outcome for this batch:

* keep 4 pages
* replace 1 page (`real_medium_003`)

This is normal. The draft agent is useful, but dynamic pages still need human judgment.
