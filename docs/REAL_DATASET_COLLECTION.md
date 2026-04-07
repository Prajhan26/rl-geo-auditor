# Real Dataset Collection Guide

This project currently has a **60-page synthetic benchmark** in `data/`.
That is useful for environment development and evaluation, but it is not the
same thing as a real-webpage benchmark.

Use this guide to build the next version:

* 20 real easy pages
* 20 real medium pages
* 20 real hard pages

## What "real pages" means

A real page is:

* publicly accessible on the web
* relevant to the topic area
* manually reviewed and labeled

A real page is not:

* an `example.com` placeholder
* invented text written only for the JSON file

## Difficulty Definition

### Easy

Use pages with obvious issues such as:

* missing meta description
* very thin content
* no headers
* very weak title
* obvious missing schema

### Medium

Use pages with mixed quality and subtler issues such as:

* buried answer
* missing FAQ or HowTo schema
* no date
* weak meta description
* missing sources on pages that should cite

### Hard

Use pages with stronger content and competitive structure where issues are more nuanced:

* comparison pages
* strategy pages
* institutional or advanced operator pages
* pages that are nearly correct except for one or two important omissions
* some clean pages with no issues at all

## Recommended Workflow

1. Collect candidate URLs in a spreadsheet or notes doc.
2. Open each page manually.
3. Record the page fields into JSON:
   * `url`
   * `target_query`
   * `title_tag`
   * `meta_description`
   * `h1`
   * `first_paragraph`
   * `word_count`
   * `headers`
   * `schema_types`
   * `has_author`
   * `has_date`
   * `has_sources`
   * `source_count`
4. Label issues conservatively.
5. Add the page to the correct difficulty file.

## Labeling Rule Of Thumb

Flag an issue only when you could explain it clearly to another person.

Examples:

* `missing_meta_description`: the page has no meta description
* `weak_title_tag`: title is generic or poorly aligned to the target query
* `no_direct_answer`: opening paragraph does not answer the query directly
* `buried_answer`: answer exists, but only after fluff or delay
* `missing_faq_schema`: FAQ-style content exists but `FAQPage` schema is absent
* `missing_howto_schema`: step-by-step instructional page lacks `HowTo` schema
* `missing_article_schema`: article-like page lacks `Article` schema
* `no_author`: no author attribution visible
* `no_date`: no publish/update date visible
* `no_sources`: not enough supporting citations for the page type

## Starter Pool Of Real Candidates

These are candidate pages to review and label manually. They are not yet added
to `data/`.

### Easy candidates

These are likely to produce obvious labels if you choose lower-quality blog or
affiliate-style pages in staking search results:

* Search query: `ethereum staking basics`
* Search query: `what is solo staking`
* Search query: `ethereum validator faq`
* Search query: `staking rewards explained`
* Search query: `liquid staking faq`

Use obvious low-quality pages from search results and label them manually.

### Medium candidates

1. Ethereum staking overview:
   https://ethereum.org/staking/
2. Home staking:
   https://ethereum.org/staking/solo/
3. Pooled staking:
   https://ethereum.org/staking/pools/
4. Lido staking app:
   https://stake.lido.fi/
5. Lido FAQ:
   https://lido.fi/faq
6. Blocknative liquid staking guide:
   https://www.blocknative.com/blog/ethereum-liquid-staking-guide

### Hard candidates

Use stronger comparison and advanced-operating pages:

1. Ethereum staking overview:
   https://ethereum.org/staking/
2. Home staking:
   https://ethereum.org/staking/solo/
3. Blocknative liquid staking guide:
   https://www.blocknative.com/blog/ethereum-liquid-staking-guide
4. Lido FAQ:
   https://lido.fi/faq
5. Lido staking app:
   https://stake.lido.fi/

Also search for:

* `best ethereum staking platform`
* `lido vs rocket pool`
* `ethereum staking taxes`
* `validator client comparison`
* `institutional staking custody`

These are usually better hard-set candidates because they have stronger content
and more nuanced omissions.

## Suggested Next Step

Build the real dataset in layers:

1. collect 5 real pages per difficulty first
2. label them carefully
3. test the environment again
4. then scale from 15 real pages to 60 real pages

This reduces labeling mistakes and keeps the benchmark coherent.
