# Data Format Guide

This document shows the exact JSON format Hijak needs to convert Hari's Google Sheet into.

---

## JSON Structure

Each task file is an array of page objects:

```json
[
  {
    "page_id": "easy_001",
    "url": "https://example.com/page",
    "target_query": "how to do something",
    "title_tag": "Page Title | Site Name",
    "meta_description": "Description text or empty string",
    "h1": "Main Heading",
    "first_paragraph": "First 200 characters of content...",
    "word_count": 500,
    "headers": ["H2: Section 1", "H2: Section 2", "H3: Subsection"],
    "schema_types": ["Article", "FAQPage"],
    "has_author": true,
    "has_date": false,
    "issues": [
      {
        "type": "missing_meta_description",
        "severity": "critical"
      },
      {
        "type": "no_direct_answer",
        "severity": "critical"
      }
    ]
  }
]
```

---

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `page_id` | string | Unique ID like "easy_001", "medium_015" |
| `url` | string | Full URL of the page |
| `target_query` | string | The question this page should answer |
| `title_tag` | string | The `<title>` content, empty string if missing |
| `meta_description` | string | The meta description, empty string if missing |
| `h1` | string | The H1 heading text |
| `first_paragraph` | string | First 200 chars of main content |
| `word_count` | integer | Approximate word count |
| `headers` | array of strings | List of headers like ["H2: About", "H3: Details"] |
| `schema_types` | array of strings | Schema types found like ["Article", "FAQPage"] |
| `has_author` | boolean | true if author name visible |
| `has_date` | boolean | true if date visible |
| `issues` | array of objects | List of issues with type and severity |

---

## Issue Object Format

```json
{
  "type": "issue_type_here",
  "severity": "critical|high|medium|low"
}
```

### Valid Issue Types

```
missing_title_tag
weak_title_tag
missing_meta_description
weak_meta_description
no_direct_answer
buried_answer
missing_faq_schema
missing_howto_schema
missing_article_schema
no_headers
poor_header_structure
thin_content
no_author
no_date
no_sources
```

### Severity Levels

```
critical - Must fix, severely hurts GEO
high     - Should fix soon
medium   - Nice to fix
low      - Optional improvement
```

---

## Example: task1_easy.json

```json
[
  {
    "page_id": "easy_001",
    "url": "https://random-blog.com/crypto-staking",
    "target_query": "how to stake ethereum",
    "title_tag": "Blog Post",
    "meta_description": "",
    "h1": "Welcome",
    "first_paragraph": "We are a team of crypto enthusiasts who love talking about blockchain technology and its applications...",
    "word_count": 280,
    "headers": [],
    "schema_types": [],
    "has_author": false,
    "has_date": false,
    "issues": [
      {"type": "missing_meta_description", "severity": "critical"},
      {"type": "weak_title_tag", "severity": "medium"},
      {"type": "no_direct_answer", "severity": "critical"},
      {"type": "no_headers", "severity": "high"},
      {"type": "thin_content", "severity": "medium"},
      {"type": "no_author", "severity": "medium"},
      {"type": "no_date", "severity": "medium"}
    ]
  },
  {
    "page_id": "easy_002",
    "url": "https://old-exchange.com/eth",
    "target_query": "what is ethereum staking",
    "title_tag": "",
    "meta_description": "Welcome to our exchange",
    "h1": "Ethereum",
    "first_paragraph": "Ethereum is a blockchain. It was created by Vitalik Buterin. Many people use Ethereum for various purposes...",
    "word_count": 150,
    "headers": ["H2: About"],
    "schema_types": [],
    "has_author": false,
    "has_date": false,
    "issues": [
      {"type": "missing_title_tag", "severity": "critical"},
      {"type": "weak_meta_description", "severity": "medium"},
      {"type": "no_direct_answer", "severity": "critical"},
      {"type": "thin_content", "severity": "medium"},
      {"type": "missing_article_schema", "severity": "high"}
    ]
  }
]
```

---

## Example: task2_medium.json

```json
[
  {
    "page_id": "medium_001",
    "url": "https://decent-site.com/guides/staking",
    "target_query": "how to stake ethereum",
    "title_tag": "Ethereum Staking Guide | Decent Site",
    "meta_description": "Learn about Ethereum and staking on our platform",
    "h1": "Ethereum Staking Guide",
    "first_paragraph": "Ethereum staking is becoming increasingly popular among crypto investors looking for passive income opportunities...",
    "word_count": 1200,
    "headers": ["H2: What is Staking", "H2: Benefits", "H2: How to Stake", "H2: Risks"],
    "schema_types": ["Article"],
    "has_author": true,
    "has_date": false,
    "issues": [
      {"type": "weak_meta_description", "severity": "medium"},
      {"type": "no_date", "severity": "medium"},
      {"type": "missing_howto_schema", "severity": "high"}
    ]
  },
  {
    "page_id": "medium_002",
    "url": "https://crypto-news.com/eth-staking-explained",
    "target_query": "ethereum staking rewards",
    "title_tag": "ETH Staking Explained: Rewards and Risks",
    "meta_description": "Everything you need to know about Ethereum staking rewards, including current APY rates and validator requirements.",
    "h1": "ETH Staking Explained",
    "first_paragraph": "Welcome to Crypto News! Today we're going to dive deep into the world of Ethereum staking. But first, let me tell you about our sponsor...",
    "word_count": 2000,
    "headers": ["H2: Introduction", "H2: What is Staking", "H2: Current Rewards", "H2: How to Start", "H2: FAQ"],
    "schema_types": ["Article", "FAQPage"],
    "has_author": true,
    "has_date": true,
    "issues": [
      {"type": "buried_answer", "severity": "high"},
      {"type": "missing_howto_schema", "severity": "high"}
    ]
  }
]
```

---

## Example: task3_hard.json

For hard tasks, include competitive analysis notes:

```json
[
  {
    "page_id": "hard_001",
    "url": "https://our-client.com/staking-guide",
    "target_query": "best way to stake ethereum",
    "title_tag": "Ethereum Staking Guide | Our Client",
    "meta_description": "Learn how to stake Ethereum with our comprehensive guide.",
    "h1": "Complete Ethereum Staking Guide",
    "first_paragraph": "Staking Ethereum is one of the best ways to earn passive income in crypto. In this guide, we'll show you exactly how to stake your ETH...",
    "word_count": 1800,
    "headers": ["H2: Overview", "H2: Requirements", "H2: Step by Step", "H2: Rewards", "H2: FAQ"],
    "schema_types": ["Article", "HowTo"],
    "has_author": true,
    "has_date": true,
    "issues": [
      {"type": "missing_faq_schema", "severity": "high"},
      {"type": "competitor_more_comprehensive", "severity": "medium"}
    ],
    "competitor_notes": {
      "competitor_url": "https://top-site.com/ethereum-staking",
      "competitor_advantages": [
        "Has FAQPage schema (we only have Article + HowTo)",
        "2500 words vs our 1800",
        "Includes video with VideoObject schema",
        "More recent update date"
      ]
    }
  }
]
```

---

## Conversion Script

Hijak can use this Python script to convert Google Sheets export to JSON:

```python
import csv
import json
from pathlib import Path

def convert_sheet_to_json(csv_path: str, output_path: str):
    """Convert Google Sheets CSV export to JSON format."""
    
    pages = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Parse issues
            issues = []
            for i in range(1, 6):  # Up to 5 issues
                issue_type = row.get(f'issue_{i}', '').strip()
                severity = row.get(f'issue_{i}_severity', '').strip()
                
                if issue_type:
                    issues.append({
                        "type": issue_type,
                        "severity": severity or "medium"
                    })
            
            # Parse headers
            headers_str = row.get('headers', '')
            headers = [h.strip() for h in headers_str.split(',') if h.strip()]
            
            # Parse schema types
            schema_str = row.get('schema_types', '')
            if schema_str.upper() == 'NONE' or not schema_str:
                schema_types = []
            else:
                schema_types = [s.strip() for s in schema_str.split(',') if s.strip()]
            
            page = {
                "page_id": row.get('page_id', ''),
                "url": row.get('url', ''),
                "target_query": row.get('target_query', ''),
                "title_tag": row.get('title_tag', ''),
                "meta_description": row.get('meta_description', '') if row.get('meta_description', '').upper() != 'MISSING' else '',
                "h1": row.get('h1', ''),
                "first_paragraph": row.get('first_paragraph', ''),
                "word_count": int(row.get('word_count', 0) or 0),
                "headers": headers,
                "schema_types": schema_types,
                "has_author": row.get('has_author', '').upper() == 'TRUE',
                "has_date": row.get('has_date', '').upper() == 'TRUE',
                "issues": issues
            }
            
            pages.append(page)
    
    with open(output_path, 'w') as f:
        json.dump(pages, f, indent=2)
    
    print(f"Converted {len(pages)} pages to {output_path}")


# Usage:
# 1. Export Google Sheet as CSV
# 2. Run:
#    convert_sheet_to_json('easy_pages.csv', 'data/task1_easy.json')
#    convert_sheet_to_json('medium_pages.csv', 'data/task2_medium.json')
#    convert_sheet_to_json('hard_pages.csv', 'data/task3_hard.json')
```

---

## File Locations

Place the JSON files in:

```
geo-audit-env/
└── data/
    ├── task1_easy.json     # 20 easy pages
    ├── task2_medium.json   # 20 medium pages
    └── task3_hard.json     # 20 hard pages
```

---

## Validation

Before using the data, validate it:

```python
import json

def validate_data(filepath: str):
    """Validate data file."""
    with open(filepath) as f:
        pages = json.load(f)
    
    print(f"File: {filepath}")
    print(f"Pages: {len(pages)}")
    
    for page in pages:
        # Check required fields
        assert page.get('page_id'), f"Missing page_id"
        assert page.get('url'), f"Missing url for {page['page_id']}"
        assert page.get('target_query'), f"Missing target_query for {page['page_id']}"
        assert 'issues' in page, f"Missing issues for {page['page_id']}"
        
        # Check issues
        for issue in page['issues']:
            assert issue.get('type'), f"Issue missing type in {page['page_id']}"
            assert issue.get('severity') in ['critical', 'high', 'medium', 'low'], \
                f"Invalid severity in {page['page_id']}"
    
    print("✓ Validation passed!")

# Run on all files
validate_data('data/task1_easy.json')
validate_data('data/task2_medium.json')
validate_data('data/task3_hard.json')
```
