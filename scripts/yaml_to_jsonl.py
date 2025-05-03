#!/usr/bin/env python3
import os
import yaml
import json
import sys
import re

def flatten(obj):
    """
    Recursively replace newlines in all string values with spaces
    and collapse multiple whitespace characters.
    """
    if isinstance(obj, dict):
        return {k: flatten(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [flatten(v) for v in obj]
    elif isinstance(obj, str):
        # Replace newlines and carriage returns with spaces, collapse whitespace
        return re.sub(r'\s+', ' ', obj.strip())
    else:
        return obj

def yaml_dir_to_jsonl(src_dir: str, dst_dir: str):
    """
    Crawl src_dir for all .yaml/.yml files, convert each to a .jsonl
    file in dst_dir, preserving base filenames. Injects 'type' and
    auto-generates 'index', and flattens multiline strings.
    """
    os.makedirs(dst_dir, exist_ok=True)
    for root, _, files in os.walk(src_dir):
        for fname in files:
            if not fname.lower().endswith(('.yaml', '.yml')):
                continue
            src_path = os.path.join(root, fname)
            rel_path  = os.path.relpath(src_path, src_dir)
            base_name = os.path.splitext(rel_path)[0]
            dst_path  = os.path.join(dst_dir, base_name + '.jsonl')
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            with open(src_path, 'r') as f:
                doc = yaml.safe_load(f)

            # Determine records and shared type
            if isinstance(doc, dict) and 'problems' in doc:
                records     = doc['problems']
                shared_type = doc.get('type')
            elif isinstance(doc, list):
                records     = doc
                shared_type = None
            else:
                print(f"Skipping {src_path}: no 'problems' or top-level list found.")
                continue

            # Write out JSONL
            with open(dst_path, 'w') as out:
                for idx, rec in enumerate(records):
                    if shared_type is not None:
                        rec.setdefault('type', shared_type)
                    rec['index'] = idx
                    rec = flatten(rec)
                    out.write(json.dumps(rec, ensure_ascii=False) + '\n')

            print(f"Wrote: {dst_path}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else 'data_src'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'data'
    yaml_dir_to_jsonl(src, dst)

