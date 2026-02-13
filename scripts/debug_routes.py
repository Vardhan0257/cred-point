#!/usr/bin/env python3

with open('routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the double parenthesis
for i, line in enumerate(lines):
    if "activity=activity))" in line:
        print(f"Found at line {i+1}: {repr(line)}")
        if i < len(lines) - 1:
            print(f"Next line {i+2}: {repr(lines[i+1])}")
        if i < len(lines) - 2:
            print(f"Next line {i+3}: {repr(lines[i+2])}")
        break
else:
    print("Pattern not found")
    # Search for just the ending
    for i, line in enumerate(lines):
        if "form=form" in line and "activity" in line and "return render" in line:
            print(f"Found similar pattern at line {i+1}: {repr(line)}")
