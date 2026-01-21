# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python-based tool for fetching academic publications from DBLP (Digital Bibliography & Library Project) and combining them into a single BibTeX file. The tool is designed for research groups to aggregate publications from multiple authors into one consolidated bibliography.

## Core Architecture

### Single-File Script Design
The entire application is contained in `simple_dblp_fetcher.py` - a standalone Python script with no external configuration files or complex dependencies. The design prioritizes simplicity and ease of use.

### Key Components

1. **Author Loading** (`load_authors`)
   - Reads `authors.txt` which contains author names and optional DBLP PIDs
   - Format: `Author Name, PID` (one per line, comments allowed with `#`)
   - PIDs are used to disambiguate authors and avoid search API calls

2. **DBLP Integration**
   - **Search API** (`search_author`): Finds author PIDs when not provided
   - **BibTeX Endpoint** (`fetch_bibtex`): Downloads complete publication list for a PID
   - Base URL pattern: `https://dblp.org/pid/{PID}.bib`

3. **Rate Limiting & Retry Logic**
   - 3-second delay between author requests (see line 388)
   - Retry mechanism with exponential backoff for HTTP 429 errors (lines 134-143)
   - Max 3 retries with increasing wait times (5, 10, 15 seconds)

4. **Year Filtering** (`filter_bibtex_by_year`)
   - Optional filtering by start/end year
   - Parses year from BibTeX `year = {YYYY}` field
   - Applied per-author before combining

5. **Deduplication** (`combine_bibtex`)
   - Removes duplicate publications using BibTeX keys (e.g., `DBLP:conf/sp/Paper2024`)
   - Common when multiple authors from the same group co-author papers
   - Tracks statistics: entries before/after deduplication

## Common Commands

### Basic Usage
```bash
# Fetch all publications for authors in authors.txt
python3 simple_dblp_fetcher.py

# Output: publications.bib
```

### With Year Filtering
```bash
# Publications from 2020-2024
python3 simple_dblp_fetcher.py --start 2020 --end 2024

# Publications from 2023 onwards
python3 simple_dblp_fetcher.py --start 2023

# Publications up to 2022
python3 simple_dblp_fetcher.py --end 2022
```

### Custom Input/Output
```bash
# Custom authors file and output file
python3 simple_dblp_fetcher.py --authors team.txt --output my_pubs.bib
```

### Dependencies
```bash
# Only requires the requests library
pip install requests
```

## File Structure

- `simple_dblp_fetcher.py` - Main script with all functionality
- `authors.txt` - Input file listing authors to fetch (one per line)
- `publications.bib` - Output file containing combined BibTeX entries
- `Readme.md` - User documentation

## Development Workflow

### Making Changes to the Script

1. The script is designed to be self-contained - avoid adding external dependencies unless absolutely necessary
2. When modifying API calls, respect DBLP's rate limits (currently 3-second delay between requests)
3. Maintain backward compatibility with the `authors.txt` format

### Testing Changes

Since there are no automated tests, manual testing workflow:
```bash
# Test with a small authors.txt (1-2 authors)
python3 simple_dblp_fetcher.py --authors test_authors.txt --output test.bib

# Verify output:
# - Check console output for errors
# - Inspect test.bib for valid BibTeX format
# - Confirm publication counts match expectations
```

### Common Modification Points

- **Rate limiting**: Adjust `time.sleep(3)` at line 388 and retry logic at lines 134-143
- **API endpoints**: DBLP URLs at lines 80 and 120
- **Output format**: Header generation in `combine_bibtex` (lines 256-286)
- **Error handling**: Each function has try/except blocks with logging

## Important Implementation Details

### Author PID Format
- PIDs in `authors.txt` use forward slash format: `123/4567`
- This maps to DBLP URL: `https://dblp.org/pid/123/4567`
- PIDs can be found by searching author name on dblp.org

### BibTeX Deduplication Logic
- Uses BibTeX keys (citation identifiers) to detect duplicates
- Key extraction at line 242: parses first line of entry for `{KEY,`
- Maintains insertion order, keeping first occurrence of each unique key

### Year Filtering Implementation
- Parses BibTeX entries by splitting on `@` character (line 170)
- Searches each entry for `year = {YYYY}` pattern (lines 176-182)
- Entries without parseable years are excluded from filtered results

## Automation

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/update-publications.yml`) that automatically updates `publications.bib`:

- **Schedule**: Runs monthly on the 1st at 00:00 UTC
- **Manual trigger**: Can be triggered manually from GitHub Actions tab
- **Behavior**: Fetches publications from 2020 to current year, commits and pushes changes if publications.bib is updated

The workflow uses `github-actions[bot]` as the committer, so no personal credentials are needed.

### Manual Trigger

To manually trigger the workflow:
1. Go to GitHub repository → Actions tab
2. Select "Update Publications" workflow
3. Click "Run workflow" button

### Modifying the Automation

To change the schedule or year range, edit `.github/workflows/update-publications.yml`:
- **Schedule**: Modify the `cron` expression (line 5)
- **Year range**: Change `--start 2020 --end $CURRENT_YEAR` in the workflow

## Use Case: WordPress TeachPress Integration

This tool is designed to generate BibTeX files for the WordPress TeachPress plugin:
1. Run script to generate `publications.bib`
2. Upload to server or GitHub
3. Configure TeachPress to import from URL
4. Publications automatically appear on WordPress site

When modifying the output format, maintain compatibility with TeachPress's BibTeX parser.
