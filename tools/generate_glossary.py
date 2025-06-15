#!/usr/bin/env python3
"""
Generate the main glossary.md file as a navigational index from individual letter files.

For each letter:
- Link to the letter file (e.g., [S](glossary/S.md))
- List all term headings in that file as links (e.g., [Self-Awareness](glossary/S.md#self-awareness)) separated by |
- Use --- as a separator between letters

Header and footer are preserved.
"""

import os
import re
from pathlib import Path

def slugify(text):
    """GitHub-style anchor slugification."""
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

def generate_glossary():
    """Generate the main glossary as a navigational index from individual letter files."""
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    glossary_dir = project_root / "docs" / "glossary"
    output_file = project_root / "docs" / "glossary.md"
    
    # Header
    header = """# Glossary

This glossary provides precise definitions of technical terms used throughout the Brain from Brane framework. Terms are organized alphabetically with cross-references to related concepts.

<!-- **Note: This is a generated file. To update, run `tools/generate_glossary.py`**. -->

---

"""    # Footer
    footer_file = glossary_dir / "_footer.md"
    if footer_file.exists():
        with open(footer_file, 'r', encoding='utf-8') as f:
            footer_content = f.read().strip()
        # Fix relative paths for the main glossary file (one level up from glossary/)
        footer_content = footer_content.replace(
            "../01-pattern-realism/1-pattern-realism.md",
            "01-pattern-realism/1-pattern-realism.md"
        )
        footer_content = footer_content.replace(
            "../../README.md",
            "../README.md"
        )
        footer = f"\n{footer_content}\n"
    else:
        footer = "\n*For additional conceptual clarifications, see the [Introduction](01-pattern-realism/1-pattern-realism.md) and [Framework Overview](../README.md).*\n"

    all_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    content_parts = [header]

    for letter in all_letters:
        letter_file = glossary_dir / f"{letter}.md"
        if not letter_file.exists():
            continue
        with open(letter_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Find all term headings (## ... or deeper)
        # Accept any markdown heading level of 2 or greater (##, ###, ####, ...)
        terms = []
        heading_pattern = re.compile(r'^#{2,}\s+(.+)')
        for line in lines:
            m = heading_pattern.match(line)
            if m:
                term = m.group(1).strip()
                anchor = slugify(term)
                terms.append((term, anchor))
        # Output section
        content_parts.append(f"## [{letter}](glossary/{letter}.md)\n\n")
        if terms:
            links = [f"[{term}](glossary/{letter}.md#{anchor})" for term, anchor in terms]
            content_parts.append(' | '.join(links) + "\n")
        else:
            content_parts.append("*No terms defined for this letter yet.*\n")
        content_parts.append("\n---\n\n")
    # Remove last separator
    if content_parts[-1].strip() == '---':
        content_parts = content_parts[:-1]
    content_parts.append(footer)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(content_parts))
    print(f"Glossary index generated at {output_file}")

if __name__ == "__main__":
    generate_glossary()
