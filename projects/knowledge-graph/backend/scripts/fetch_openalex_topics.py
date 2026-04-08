"""Fetch all OpenAlex topics and merge them into openalex_taxonomy.json as depth=2.

OpenAlex hierarchy: Domain (4) -> Field (26) -> Subfield (252) -> Topic (~4516)
We already have Fields + Subfields in the JSON. This script adds the Topic layer.

Usage:
    cd backend
    python -m scripts.fetch_openalex_topics
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from app.config import settings

BASE_URL = "https://api.openalex.org"
PER_PAGE = 200
TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "openalex_taxonomy.json"


def _headers() -> dict[str, str]:
    h: dict[str, str] = {}
    if settings.openalex_email:
        h["User-Agent"] = f"mailto:{settings.openalex_email}"
    return h


def fetch_all_topics() -> list[dict]:
    """Paginate through /topics and return all topic records."""
    all_topics: list[dict] = []
    page = 1
    client = httpx.Client(base_url=BASE_URL, headers=_headers(), timeout=60)

    try:
        while True:
            print(f"  Fetching topics page {page}...", end=" ", flush=True)
            resp = client.get("/topics", params={"per_page": PER_PAGE, "page": page})
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                print("empty, done.")
                break

            all_topics.extend(results)
            total = data.get("meta", {}).get("count", 0)
            print(f"got {len(results)}, total so far {len(all_topics)}/{total}")

            if len(all_topics) >= total:
                break
            page += 1
            time.sleep(0.12)
    finally:
        client.close()

    return all_topics


def _short_id(full_url: str) -> str:
    return full_url.replace("https://openalex.org/", "")


def merge_topics_into_taxonomy(topics: list[dict]) -> None:
    """Load existing taxonomy JSON, attach topics as children of subfields, save."""
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        fields = json.load(f)

    sf_map: dict[str, dict] = {}
    for field in fields:
        for sf in field.get("children", []):
            sf_map[sf["openalex_id"]] = sf
            sf["children"] = []

    attached = 0
    orphans = 0
    for t in topics:
        sf_info = t.get("subfield", {})
        sf_oa_id = _short_id(sf_info.get("id", "")) if sf_info.get("id") else None

        if not sf_oa_id or sf_oa_id not in sf_map:
            orphans += 1
            continue

        sf_node = sf_map[sf_oa_id]
        topic_entry = {
            "name_en": t["display_name"],
            "openalex_id": _short_id(t["id"]),
            "works_count": t.get("works_count", 0),
        }
        sf_node["children"].append(topic_entry)
        attached += 1

    for sf in sf_map.values():
        if "children" in sf:
            sf["children"].sort(key=lambda x: x.get("works_count", 0), reverse=True)

    with open(TAXONOMY_PATH, "w", encoding="utf-8") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)

    print(f"\n  Attached {attached} topics to subfields ({orphans} orphans skipped)")
    print(f"  Saved to {TAXONOMY_PATH}")


def main():
    print("=" * 60)
    print("  FETCH OPENALEX TOPICS")
    print("=" * 60)

    print("\n[1/2] Fetching all topics from OpenAlex API...")
    topics = fetch_all_topics()
    print(f"  Total topics fetched: {len(topics)}")

    print("\n[2/2] Merging into taxonomy JSON...")
    merge_topics_into_taxonomy(topics)

    print("\nDone.")


if __name__ == "__main__":
    main()
