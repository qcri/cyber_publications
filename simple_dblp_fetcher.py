#!/usr/bin/env python3
"""
Simple DBLP Publications Fetcher
=================================
Fetches publications from DBLP for multiple authors and combines them into ONE BibTeX file.

Usage:
    python3 simple_dblp_fetcher.py
    python3 simple_dblp_fetcher.py --start 2020 --end 2024
    python3 simple_dblp_fetcher.py --authors team.txt --output publications.bib
"""

import requests
import argparse
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_authors(filename="authors.txt"):
    """
    Load authors from file.

    File format:
        Author Name, PID (optional)
        # Comments start with #

    Returns:
        List of dictionaries with 'name' and optional 'pid'
    """
    authors = []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse line
                parts = [p.strip() for p in line.split(",")]

                if not parts[0]:
                    continue

                author = {"name": parts[0]}

                # Add PID if provided
                if len(parts) > 1 and parts[1]:
                    author["pid"] = parts[1]

                authors.append(author)

        logger.info(f"Loaded {len(authors)} authors from {filename}")
        return authors

    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return []


def search_author(author_name):
    """
    Search for author on DBLP and return PID.

    Returns:
        Dictionary with author info or None
    """
    logger.info(f"Searching for: {author_name}")

    url = "https://dblp.org/search/author/api"
    params = {"q": author_name, "format": "json", "h": 1}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        hits = data.get("result", {}).get("hits", {}).get("hit", [])

        if not hits:
            logger.warning(f"  Not found: {author_name}")
            return None

        author_info = hits[0]["info"]
        pid = author_info["url"].split("/")[-1]

        logger.info(f"  Found: {author_info.get('author')} (PID: {pid})")

        return {"name": author_info.get("author", author_name), "pid": pid}

    except Exception as e:
        logger.error(f"  Error searching: {e}")
        return None


def fetch_bibtex(pid, author_name, max_retries=3):
    """
    Fetch BibTeX for an author with retry logic.

    Args:
        pid: DBLP Person ID
        author_name: Author's name
        max_retries: Maximum number of retry attempts

    Returns:
        BibTeX string or None
    """
    logger.info(f"Fetching publications for: {author_name}")

    url = f"https://dblp.org/pid/{pid}.bib"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            bibtex = response.text
            count = bibtex.count("@")

            logger.info(f"  Retrieved {count} publications")
            return bibtex

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    logger.warning(
                        f"  Rate limited. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"  Error fetching: {e}")
                    return None
            else:
                logger.error(f"  Error fetching: {e}")
                return None
        except Exception as e:
            logger.error(f"  Error fetching: {e}")
            return None

    return None


def filter_bibtex_by_year(bibtex, start_year=None, end_year=None):
    """
    Filter BibTeX entries by year range.

    Args:
        bibtex: BibTeX content
        start_year: Start year (inclusive)
        end_year: End year (inclusive)

    Returns:
        Filtered BibTeX string
    """
    if start_year is None and end_year is None:
        return bibtex

    filtered_entries = []
    entries = bibtex.split("@")[1:]  # Split into entries

    for entry in entries:
        # Extract year from entry
        year = None
        for line in entry.split("\n"):
            if "year" in line.lower() and "=" in line:
                try:
                    year_str = line.split("=")[1].strip().strip(",{}").strip()
                    year = int(year_str)
                    break
                except:
                    continue

        # Check if year is in range
        if year:
            include = True
            if start_year and year < start_year:
                include = False
            if end_year and year > end_year:
                include = False

            if include:
                filtered_entries.append("@" + entry)

    return "\n".join(filtered_entries)


def extract_bibtex_key(entry):
    """
    Extract the BibTeX key from an entry.

    Example: @inproceedings{DBLP:conf/sp/Paper2024, ...
             Returns: DBLP:conf/sp/Paper2024
    """
    try:
        # Find the first line with @ and {
        first_line = entry.split("\n")[0]
        if "{" in first_line:
            key = first_line.split("{")[1].split(",")[0].strip()
            return key
    except:
        pass
    return None


def combine_bibtex(author_data_list, start_year=None, end_year=None):
    """
    Combine BibTeX from multiple authors into one file.
    Removes duplicate entries (same paper by multiple authors).

    Args:
        author_data_list: List of dicts with 'name', 'pid', 'bibtex'
        start_year: Optional start year filter
        end_year: Optional end year filter

    Returns:
        Combined BibTeX string
    """
    # Track seen entries by their BibTeX key to avoid duplicates
    seen_keys = set()
    unique_entries = []

    # Collect all unique entries
    for item in author_data_list:
        entries = item["bibtex"].split("@")[1:]  # Split into individual entries

        for entry in entries:
            if not entry.strip():
                continue

            # Extract the BibTeX key
            key = extract_bibtex_key("@" + entry)

            # Only add if we haven't seen this key before
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_entries.append("@" + entry)

    # Count publications per author (before de-duplication)
    author_counts = {}
    for item in author_data_list:
        count = item["bibtex"].count("@")
        author_counts[item["name"]] = count

    # Header
    combined = f"% DBLP Publications - Combined BibTeX\n"
    combined += f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    combined += f"% Total Authors: {len(author_data_list)}\n"

    if start_year or end_year:
        combined += f"% Year Range: "
        if start_year and end_year:
            combined += f"{start_year}-{end_year}\n"
        elif start_year:
            combined += f"{start_year}+\n"
        elif end_year:
            combined += f"up to {end_year}\n"

    combined += "%\n"
    combined += "% Authors included:\n"

    # List authors with their individual counts
    total_before_dedup = 0
    for item in author_data_list:
        count = author_counts[item["name"]]
        total_before_dedup += count
        combined += f"% - {item['name']}: {count} publications\n"

    combined += f"%\n"
    combined += f"% Total entries (before de-duplication): {total_before_dedup}\n"
    combined += f"% Unique publications (after de-duplication): {len(unique_entries)}\n"
    combined += f"% Duplicates removed: {total_before_dedup - len(unique_entries)}\n"
    combined += "%\n"
    combined += "% NOTE: Duplicates occur when multiple authors from this group\n"
    combined += "%       co-author papers together.\n"
    combined += "%\n% ========================================\n\n"

    # Add all unique entries
    combined += "\n".join(unique_entries)
    combined += "\n"

    return combined


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fetch DBLP publications and combine into one BibTeX file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --start 2020 --end 2024
  %(prog)s --authors team.txt --output my_publications.bib
  %(prog)s --start 2023 --output recent_pubs.bib
        """,
    )

    parser.add_argument(
        "--authors", default="authors.txt", help="Authors file (default: authors.txt)"
    )

    parser.add_argument(
        "--output",
        default="publications.bib",
        help="Output BibTeX file (default: publications.bib)",
    )

    parser.add_argument("--start", type=int, help="Start year (e.g., 2020)")

    parser.add_argument("--end", type=int, help="End year (e.g., 2024)")

    args = parser.parse_args()

    # Validate year range
    if args.start and args.end and args.start > args.end:
        logger.error("Start year cannot be greater than end year!")
        return 1

    print("\n" + "=" * 60)
    print("DBLP Publications Fetcher")
    print("=" * 60 + "\n")

    # Load authors
    authors = load_authors(args.authors)

    if not authors:
        logger.error("No authors found!")
        return 1

    print(f"Authors to fetch: {len(authors)}")
    if args.start or args.end:
        year_range = f"{args.start or 'start'} to {args.end or 'now'}"
        print(f"Year filter: {year_range}")
    print()

    # Fetch publications for each author
    author_data_list = []

    for idx, author in enumerate(authors, 1):
        print(f"[{idx}/{len(authors)}] Processing: {author['name']}")

        # Get PID if not provided
        if "pid" not in author:
            author_info = search_author(author["name"])
            if not author_info:
                print(f"  Skipped (not found)\n")
                continue
            pid = author_info["pid"]
            author_name = author_info["name"]
        else:
            pid = author["pid"]
            author_name = author["name"]

        # Fetch BibTeX
        bibtex = fetch_bibtex(pid, author_name)

        if not bibtex:
            print(f"  Skipped (fetch failed)\n")
            continue

        # Filter by year if specified
        if args.start or args.end:
            original_count = bibtex.count("@")
            bibtex = filter_bibtex_by_year(bibtex, args.start, args.end)
            filtered_count = bibtex.count("@")
            print(
                f"  Filtered: {filtered_count}/{original_count} publications in range"
            )

        # Add to list
        author_data_list.append({"name": author_name, "pid": pid, "bibtex": bibtex})

        print()

        # Add delay to avoid rate limiting (except for last author)
        if idx < len(authors):
            time.sleep(3)  # Wait 3 seconds between requests

    # Check if we have any data
    if not author_data_list:
        logger.error("No publications fetched!")
        return 1

    # Combine all BibTeX
    print("Combining publications...")
    combined_bibtex = combine_bibtex(author_data_list, args.start, args.end)

    # Save to file
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(combined_bibtex)

    # Calculate statistics
    total_pubs = combined_bibtex.count("@")

    # Count publications before de-duplication
    total_before_dedup = sum(item["bibtex"].count("@") for item in author_data_list)
    duplicates_removed = total_before_dedup - total_pubs

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Authors processed: {len(author_data_list)}/{len(authors)}")
    print(f"Total entries collected: {total_before_dedup}")
    if duplicates_removed > 0:
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Unique publications: {total_pubs}")
    else:
        print(f"Total publications: {total_pubs}")
    if args.start or args.end:
        year_range = f"{args.start or 'start'} to {args.end or 'now'}"
        print(f"Year range: {year_range}")
    print(f"Output file: {args.output}")
    print("=" * 60 + "\n")

    if duplicates_removed > 0:
        print(
            f"ℹ️  Note: {duplicates_removed} duplicate(s) removed (co-authored papers)"
        )
    print(f"✓ Done! Publications saved to: {args.output}\n")

    return 0


if __name__ == "__main__":
    exit(main())
