#!/usr/bin/env python3
"""Patch generate_diagrams.py to fix fig_4_5 Mermaid syntax errors."""
import re

path = r'c:\Users\HP\Desktop\dhruv\Resume screener\scripts\generate_diagrams.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Unicode checkmark/cross break Mermaid parser
content = content.replace('\u2714 Accept Rewrite', 'ACCEPT REWRITE')
content = content.replace('\u2718 Reject LLM Output', 'REJECT LLM OUTPUT')

# Fix 2: %, $ symbols inside node labels cause Mermaid issues
content = content.replace(
    'Extract Numbers, %, $, Technical Tokens',
    'Extract Numbers, Percentages, Technical Tokens'
)

# Fix 3: "(0ms Sub-Millisecond Response)" is fine, but "(Yes (Zero Hallucination))" 
# parentheses inside edge labels can break parser
content = content.replace(
    '-->|Yes (Zero Hallucination)| STEP6_PASS',
    '-->|"Yes: Zero Hallucination"| STEP6_PASS'
)
content = content.replace(
    '-->|No (Invented Facts)| STEP6_FAIL',
    '-->|"No: Invented Facts"| STEP6_FAIL'
)

# Also fix Token & Metric in diamond label (& breaks Mermaid)
content = content.replace(
    'STEP5 --> VAL_CHECK{"Token & Metric<br/>Set Match?"}',
    'STEP5 --> VAL_CHECK{"Token and Metric<br/>Set Match?"}'
)

# Fix Candidate Bullet Point & Target Skill in node
content = content.replace(
    'IN_BULLET["Candidate Bullet Point & Target Skill"]',
    'IN_BULLET["Candidate Bullet Point and Target Skill"]'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully!")
print("Verifying key lines:")
for i, line in enumerate(content.split('\n'), 1):
    if 'STEP6_PASS' in line or 'STEP6_FAIL' in line or 'VAL_CHECK' in line or 'IN_BULLET' in line:
        print(f"  L{i}: {line.strip()}")
