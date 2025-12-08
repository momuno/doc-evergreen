#!/usr/bin/env python3
"""Test script for LLM relevance analyzer with debug logging.

This helps diagnose why LLM analysis appears to not be running.
"""

import logging
import sys
from pathlib import Path

# Setup verbose logging FIRST
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s [%(name)s] %(message)s',
    force=True,
)

# Set all doc_evergreen loggers to DEBUG
logging.getLogger('doc_evergreen').setLevel(logging.DEBUG)

# Reduce noise from libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('anthropic').setLevel(logging.WARNING)

print("=" * 80)
print("LLM RELEVANCE ANALYZER TEST")
print("=" * 80)
print()

# Now import after logging is configured
from doc_evergreen.generate.intent_context import IntentContext
from doc_evergreen.generate.repo_indexer import FileIndex
from doc_evergreen.generate.llm_relevance_analyzer import LLMRelevanceAnalyzer

# Load existing context
context_path = Path('.doc-evergreen/context.json')
index_path = Path('.doc-evergreen/file_index.json')

if not context_path.exists():
    print("❌ No context.json found. Run generate-outline first.")
    sys.exit(1)

if not index_path.exists():
    print("❌ No file_index.json found. Run generate-outline first.")
    sys.exit(1)

print("📂 Loading context and file index...")

# Load context from JSON
import json
context_data = json.loads(context_path.read_text())
from doc_evergreen.generate.doc_type import validate_doc_type
context = IntentContext(
    doc_type=validate_doc_type(context_data['doc_type']),
    purpose=context_data['purpose'],
    output_path=context_data['output_path'],
)

file_index = FileIndex.load(index_path)

print(f"   Doc type: {context.doc_type.value}")
print(f"   Purpose: {context.purpose[:80]}...")
print(f"   Total files: {len(file_index.files)}")
print()

# Test with just 3 files to keep it fast
print("🧪 Creating test file index (first 3 files only)...")
test_files = file_index.files[:3]
test_index = FileIndex(
    project_root=file_index.project_root,
    files=test_files,
)

for i, f in enumerate(test_index.files, 1):
    print(f"   {i}. {f.rel_path} ({f.file_type.value})")
print()

print("🤖 Creating LLMRelevanceAnalyzer...")
print("   (Watch for debug logging below)")
print()
print("-" * 80)

try:
    analyzer = LLMRelevanceAnalyzer(
        context=context,
        file_index=test_index,
        threshold=0,  # Accept all scores to see what we get
        batch_size=3,
    )
    
    print()
    print("-" * 80)
    print()
    print("🔍 Running LLM analysis on 3 files...")
    print("   (This should take 10-30 seconds if LLM is being called)")
    print()
    
    def progress(current, total, file_path):
        print(f"   📊 Progress: {current}/{total} - {file_path}")
    
    scores = analyzer.analyze(progress_callback=progress)
    
    print()
    print("=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print(f"Results: {len(scores)} files scored")
    print()
    
    for score in scores:
        print(f"📄 {score.file_path}")
        print(f"   Score: {score.score}")
        print(f"   Reasoning: {score.reasoning[:100]}...")
        print(f"   Key Material: {score.key_material[:100]}...")
        print()
    
    # Check if reasoning is generic (rule-based) or custom (LLM)
    if scores:
        first_reasoning = scores[0].reasoning
        if "Documentation file" in first_reasoning and "highly relevant" in first_reasoning:
            print("⚠️  WARNING: Reasoning looks GENERIC (rule-based)")
            print("   Expected: Custom LLM reasoning specific to your purpose")
            print("   Got: Generic rule-based reasoning")
            print()
            print("   This means LLMRelevanceAnalyzer is NOT actually being used!")
        else:
            print("✓ Reasoning looks CUSTOM (LLM-based)")
            print("  This is what we want!")
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ ERROR OCCURRED")
    print("=" * 80)
    print()
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
