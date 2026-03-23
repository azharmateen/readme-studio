"""README generation engine using LLM."""

import os
import json
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


@dataclass
class ProjectInfo:
    """Input data for README generation."""
    name: str
    one_liner: str
    language: str
    tech_stack: str
    commands: str
    features: str
    install_steps: str
    license_type: str
    extra_notes: str


@dataclass
class GeneratedReadme:
    """Generated README content."""
    markdown: str
    sections: dict


README_PROMPT = """You are a developer advocate creating a polished README.md for a developer tool.

## Project Details
- **Name:** {name}
- **One-liner:** {one_liner}
- **Language:** {language}
- **Tech Stack:** {tech_stack}
- **Key Commands:** {commands}
- **Features:** {features}
- **Install Steps:** {install_steps}
- **License:** {license_type}
- **Additional Notes:** {extra_notes}

---

Generate a complete, polished README.md with these sections:
1. **Title** with a concise tagline
2. **Badges** (build, license, version - use shields.io placeholders)
3. **Features** - bullet list with brief descriptions
4. **Quick Start** - 3-5 steps to get running
5. **Installation** - detailed install instructions
6. **Usage** - code examples with syntax highlighting
7. **Configuration** - any config options
8. **Contributing** - brief contribution guide
9. **License** - license notice

Guidelines:
- Write in a friendly, professional tone
- Include realistic code examples
- Use proper markdown formatting
- Make install steps copy-pasteable
- Keep it concise but complete

Respond with ONLY the raw markdown content. No wrapping fences."""


LAUNCH_KIT_PROMPT = """You are a growth marketer creating launch materials for a developer tool.

## Tool Details
- **Name:** {name}
- **One-liner:** {one_liner}
- **Language:** {language}
- **Features:** {features}

---

Generate launch materials as a JSON object with these keys:

{{
  "product_hunt_tagline": "60-char max tagline for Product Hunt",
  "product_hunt_description": "2-3 sentence Product Hunt description",
  "hn_title": "Hacker News Show HN title (under 80 chars)",
  "hn_comment": "First comment for HN post (2-3 paragraphs, technical, authentic tone)",
  "tweets": [
    "Tweet 1: announcement (under 280 chars)",
    "Tweet 2: key feature highlight (under 280 chars)",
    "Tweet 3: technical insight (under 280 chars)",
    "Tweet 4: social proof / call to action (under 280 chars)"
  ],
  "reddit_title": "Reddit post title for r/programming",
  "reddit_body": "Reddit post body (3-4 paragraphs, honest tone, technical details)"
}}

Respond ONLY with the JSON object. No markdown fences."""


def generate_readme(project: ProjectInfo, model: str = "gpt-4o-mini") -> GeneratedReadme:
    """Generate a README using an LLM."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)

    prompt = README_PROMPT.format(
        name=project.name,
        one_liner=project.one_liner,
        language=project.language,
        tech_stack=project.tech_stack,
        commands=project.commands,
        features=project.features,
        install_steps=project.install_steps,
        license_type=project.license_type,
        extra_notes=project.extra_notes,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.7,
    )

    markdown = response.choices[0].message.content or ""

    # Parse sections from generated markdown
    sections = _parse_sections(markdown)

    return GeneratedReadme(markdown=markdown, sections=sections)


def generate_launch_kit(project: ProjectInfo, model: str = "gpt-4o-mini") -> dict:
    """Generate launch materials (PH, HN, tweets, Reddit)."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)

    prompt = LAUNCH_KIT_PROMPT.format(
        name=project.name,
        one_liner=project.one_liner,
        language=project.language,
        features=project.features,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.8,
    )

    content = response.choices[0].message.content or "{}"

    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    if content.endswith("```"):
        content = content[:-3]

    try:
        return json.loads(content.strip())
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse launch kit",
            "raw": content[:500],
        }


def _parse_sections(markdown: str) -> dict:
    """Parse markdown into sections by headers."""
    sections = {}
    current_section = "preamble"
    current_content = []

    for line in markdown.split("\n"):
        if line.startswith("# "):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line.lstrip("# ").strip()
            current_content = []
        elif line.startswith("## "):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line.lstrip("# ").strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def generate_readme_offline(project: ProjectInfo) -> GeneratedReadme:
    """Generate a basic README without an LLM (fallback)."""
    md = f"""# {project.name}

{project.one_liner}

## Features

{_bulletize(project.features)}

## Installation

```bash
{project.install_steps or f'# Install {project.name}'}
```

## Usage

```bash
{project.commands or f'# Run {project.name}'}
```

## Tech Stack

{project.tech_stack or project.language}

## License

{project.license_type or 'MIT'}
"""

    if project.extra_notes:
        md += f"\n## Notes\n\n{project.extra_notes}\n"

    return GeneratedReadme(markdown=md, sections=_parse_sections(md))


def _bulletize(text: str) -> str:
    """Convert newline-separated items to bullet list."""
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    return "\n".join(f"- {l.lstrip('- ')}" for l in lines)
