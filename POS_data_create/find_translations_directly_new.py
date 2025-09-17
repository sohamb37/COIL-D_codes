import os
import sys
import csv
from pathlib import Path
from collections import defaultdict

def load_all_gov_pairs_for_langpair(lp_root: Path):
    """
    Aggregate all <source>\t<target> pairs from all .txt files under:
      lp_root / "GOV" / ** / "translation_text" / "source_translated" / *.txt
    Returns:
      - mapping: dict {source: target}
      - stats: dict counts (files, lines, bad_lines)
    Last occurrence wins if duplicates. Skips lines without a tab.
    """
    gov_dir = lp_root / "EDU" # change accordingly for different domains
    mapping = {}
    stats = {"files": 0, "lines": 0, "bad_lines": 0}

    if not gov_dir.is_dir():
        return mapping, stats

    # Walk all subfolders under GOV
    for dirpath, dirnames, filenames in os.walk(gov_dir):
        # Only read files from directories named .../translation_text/source_translated
        p = Path(dirpath)
        if p.name != "source_reviewed": # chaging to source_reviewed from source_translated
            continue
        if p.parent.name != "translation_text":
            continue

        for fname in filenames:
            fp = p / fname
            if not fp.is_file() or fp.suffix.lower() != ".txt":
                continue
            stats["files"] += 1
            try:
                with fp.open("r", encoding="utf-8") as f:
                    for line in f:
                        stats["lines"] += 1
                        ln = line.rstrip("\n")
                        if "\t" not in ln:
                            stats["bad_lines"] += 1
                            continue
                        src, tgt = ln.split("\t", 1)
                        src = src.strip()
                        tgt = tgt.strip()
                        if not src:
                            continue
                        mapping[src] = tgt
            except Exception as e:
                print(f"Warning: Failed to read {fp}: {e}")

    return mapping, stats

def collect_all_langpairs(root: Path):
    """
    Discover language pair directories under root (name contains '-').
    Returns sorted list of LP names.
    """
    lps = []
    for d in os.listdir(root):
        if "-" in d and (root / d).is_dir():
            lps.append(d)
    return sorted(lps)


    # return ["HIN-MAI", "HIN-ODI", "HIN-SAT", "HIN-BAN"]
    # return ["HIN-DOI", "HIN-PAN", "HIN-MAI", "HIN-ODI", "HIN-SAT", "HIN-BAN"]
    # return ["HIN-DOI", "HIN-PAN", "HIN-MAI", "HIN-ODI", "HIN-SAT", "HIN-BAN", "HIN-GOM"]
    # return ["HIN-GOM", "HIN-SND", "HIN-URD", "HIN-DOI", "HIN-PAN", "HIN-MAI", "HIN-ODI", "HIN-SAT", "HIN-BAN", "HIN-ASM"]

# def intersect_sources_across_langpairs(per_lp_map: dict):
#     """
#     Given {lp: {src: tgt}}, return sorted list of sources present in ALL langpairs.
#     """
#     if not per_lp_map:
#         return []
#     sets = [set(m.keys()) for m in per_lp_map.values()]
#     universal = set.intersection(*sets) if sets else set()
#     return sorted(universal)

def relaxed_sources_across_langpairs(per_lp_map: dict, min_fraction: float = 0.6):
    """
    Given {lp: {src: tgt}}, return sorted list of sources that appear
    in at least `min_fraction` of language pairs.
    """
    if not per_lp_map:
        return []

    lp_count = len(per_lp_map)
    min_required = max(1, int(lp_count * min_fraction))

    # Count how many LPs contain each source
    freq = defaultdict(int)
    for lp, mapping in per_lp_map.items():
        for s in mapping.keys():
            freq[s] += 1

    # Retain sources that meet the threshold
    candidates = [s for s, c in freq.items() if c >= min_required]

    return sorted(candidates)



def write_universal_tsv(out_path: Path, langpairs: list, universal_sources: list, per_lp_map: dict):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        header = ["source_HIN"] + langpairs
        w.writerow(header)
        for s in universal_sources:
            row = [s]
            for lp in langpairs:
                row.append(per_lp_map[lp].get(s, ""))
            w.writerow(row)

def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: python select_gov_universal_agnostic.py <root_dir> <output_tsv> [--report]")
        print("  <root_dir>: path containing HIN-XXX directories")
        print("  <output_tsv>: path to final TSV with universal sentences across all LPs")
        print("  --report (optional): print per-LP stats and coverage diagnostics")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    out_tsv = Path(sys.argv[2]).resolve()
    report = len(sys.argv) == 4 and sys.argv[3] == "--report"

    if not root.is_dir():
        print(f"Error: root_dir not found: {root}")
        sys.exit(1)

    langpairs = collect_all_langpairs(root)
    if not langpairs:
        print("No language pair directories found.")
        sys.exit(0)

    per_lp_map = {}
    stats_all = {}
    for lp in langpairs:
        mapping, stats = load_all_gov_pairs_for_langpair(root / lp)
        if not mapping:
            print(f"[{lp}] No GOV data found.")
        else:
            print(f"[{lp}] Loaded {len(mapping)} pairs from {stats['files']} file(s), {stats['bad_lines']} malformed line(s) skipped.")
        per_lp_map[lp] = mapping
        stats_all[lp] = stats

    # Require presence across ALL language pairs
    # If any LP has zero pairs, the intersection will be empty.
    universal_sources = relaxed_sources_across_langpairs(per_lp_map, min_fraction=0.6)

    if not universal_sources:
        print("No universal source sentences found across all language pairs' GOV data.")
        if report:
            # Simple coverage hints: show top-N frequent sources per LP or counts
            for lp in langpairs:
                print(f"  - {lp}: {len(per_lp_map[lp])} unique sources")
        sys.exit(0)

    write_universal_tsv(out_tsv, langpairs, universal_sources, per_lp_map)
    print(f"✓ Wrote universal TSV with {len(universal_sources)} rows: {out_tsv}")

    if report:
        print("\nDiagnostics:")
        for lp in langpairs:
            total = len(per_lp_map[lp])
            print(f"  - {lp}: {total} unique GOV sources; overlap with universal: {sum(1 for s in universal_sources if s in per_lp_map[lp])}")

if __name__ == "__main__":
    main()
