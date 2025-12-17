# Simple DBLP Fetcher

A simple Python script to fetch publications from DBLP and combine them into ONE BibTeX file.

## Features

✅ Reads authors from a file  
✅ Fetches all publications from DBLP  
✅ Combines into ONE BibTeX file  
✅ Filter by year range (optional)  
✅ Simple and easy to use

## Files Needed

```
simple_dblp_fetcher.py    ← The script
authors.txt               ← List your authors here
```

## Quick Start

### 1. Create authors.txt

```text
# List your authors (one per line)
# Format: Author Name, PID (optional)

Issa Khalil, 115/8715
Mohamed Nabeel
Ting Yu
```

### 2. Run the script

```bash
# Fetch all publications
python3 simple_dblp_fetcher.py

# Output: publications.bib
```

Done! You now have ONE file with ALL publications.

## Usage Examples

### Basic usage (all publications)

```bash
python3 simple_dblp_fetcher.py
```

### Filter by year range

```bash
# Publications from 2020 to 2024
python3 simple_dblp_fetcher.py --start 2020 --end 2024

# Publications from 2023 onwards
python3 simple_dblp_fetcher.py --start 2023

# Publications up to 2022
python3 simple_dblp_fetcher.py --end 2022
```

### Custom files

```bash
# Custom authors file and output
python3 simple_dblp_fetcher.py --authors team.txt --output my_pubs.bib
```

### Combined

```bash
python3 simple_dblp_fetcher.py --authors team.txt --output recent.bib --start 2023 --end 2024
```

## Command Line Options

```
--authors FILE    Authors file (default: authors.txt)
--output FILE     Output BibTeX file (default: publications.bib)
--start YEAR      Start year filter (e.g., 2020)
--end YEAR        End year filter (e.g., 2024)
```

## Example Output

```
============================================================
DBLP Publications Fetcher
============================================================

Authors to fetch: 3
Year filter: 2020 to 2024

[1/3] Processing: Issa Khalil
  Found: Issa Khalil (PID: 115/8715)
  Retrieved 150 publications
  Filtered: 45/150 publications in range

[2/3] Processing: Mohamed Nabeel
  Searching for: Mohamed Nabeel
  Found: Mohamed Nabeel (PID: 65/4357)
  Retrieved 85 publications
  Filtered: 30/85 publications in range

[3/3] Processing: Ting Yu
  Searching for: Ting Yu
  Found: Ting Yu (PID: y/TingYu-1)
  Retrieved 120 publications
  Filtered: 40/120 publications in range

Combining publications...

============================================================
SUMMARY
============================================================
Authors processed: 3/3
Total publications: 115
Year range: 2020 to 2024
Output file: publications.bib
============================================================

✓ Done! Publications saved to: publications.bib
```

## Output File Format

The script creates ONE BibTeX file with ALL authors:

```bibtex
% DBLP Publications - Combined BibTeX
% Generated: 2024-12-12 15:30:22
% Total Authors: 3
% Year Range: 2020-2024
%
% Authors included:
% - Issa Khalil: 45 publications
% - Mohamed Nabeel: 30 publications
% - Ting Yu: 40 publications
%
% Total Publications: 115
%
% ========================================

% ========================================
% Author: Issa Khalil
% DBLP: https://dblp.org/pid/115/8715
% ========================================

@inproceedings{DBLP:conf/sp/DenizN0K25,
  author    = {Fatih Deniz and Mohamed Nabeel and ...},
  title     = {MANTIS: Detection of...},
  booktitle = {SP},
  year      = {2025}
}

... (all Issa's publications)

% ========================================
% Author: Mohamed Nabeel
% DBLP: https://dblp.org/pid/65/4357
% ========================================

... (all Mohamed's publications)

% ========================================
% Author: Ting Yu
% DBLP: https://dblp.org/pid/y/TingYu-1
% ========================================

... (all Ting's publications)
```

## Requirements

```bash
pip install requests
```

Or:

```bash
pip install -r requirements.txt
```

## WordPress TeachPress Integration

Perfect for WordPress TeachPress plugin:

1. Upload `publications.bib` to your server or GitHub
2. In TeachPress settings, use the URL to the file
3. Publications appear on your website!

## Troubleshooting

### "Author not found"

- Check spelling in authors.txt
- Add DBLP PID manually: `Author Name, 123/4567`

### "No publications fetched"

- Check internet connection
- Try adding PID for each author
- Check DBLP website is accessible

### Year filtering not working

- Make sure BibTeX entries have `year = {YYYY}` field
- DBLP data should include years automatically

## Tips

### Find Author's PID

1. Go to https://dblp.org
2. Search for author name
3. URL will be: `https://dblp.org/pid/123/4567.html`
4. PID is: `123/4567`

### Multiple Authors with Same Name

Use PID to disambiguate:

```text
John Smith, 123/4567  ← The one from MIT
John Smith, 789/0123  ← The one from Stanford
```

### Large Number of Authors

The script processes authors sequentially with a small delay to be respectful to DBLP servers.

## Support

- Check the log output for errors
- Verify authors.txt format
- Test with one author first
- Use `--start` and `--end` to reduce results

---
