"""Generate launch materials: Product Hunt, HN, tweets, Reddit."""

from generator import ProjectInfo, generate_launch_kit


def format_launch_kit_text(kit: dict) -> str:
    """Format launch kit as readable text."""
    lines = []

    if "error" in kit:
        return f"Error generating launch kit: {kit['error']}\n\nRaw: {kit.get('raw', '')}"

    lines.append("=" * 60)
    lines.append("LAUNCH KIT")
    lines.append("=" * 60)

    # Product Hunt
    lines.append("\n--- Product Hunt ---")
    lines.append(f"Tagline: {kit.get('product_hunt_tagline', 'N/A')}")
    lines.append(f"\nDescription:\n{kit.get('product_hunt_description', 'N/A')}")

    # Hacker News
    lines.append("\n--- Hacker News ---")
    lines.append(f"Title: {kit.get('hn_title', 'N/A')}")
    lines.append(f"\nFirst Comment:\n{kit.get('hn_comment', 'N/A')}")

    # Tweets
    tweets = kit.get("tweets", [])
    if tweets:
        lines.append("\n--- Tweet Thread ---")
        for i, tweet in enumerate(tweets, 1):
            lines.append(f"\n[{i}/{len(tweets)}] {tweet}")
            lines.append(f"  ({len(tweet)} chars)")

    # Reddit
    lines.append("\n--- Reddit ---")
    lines.append(f"Title: {kit.get('reddit_title', 'N/A')}")
    lines.append(f"\nBody:\n{kit.get('reddit_body', 'N/A')}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def format_launch_kit_markdown(kit: dict) -> str:
    """Format launch kit as Markdown."""
    lines = []

    if "error" in kit:
        return f"> Error: {kit['error']}"

    lines.append("# Launch Kit\n")

    lines.append("## Product Hunt\n")
    lines.append(f"**Tagline:** {kit.get('product_hunt_tagline', 'N/A')}\n")
    lines.append(f"{kit.get('product_hunt_description', 'N/A')}\n")

    lines.append("## Hacker News\n")
    lines.append(f"**Title:** {kit.get('hn_title', 'N/A')}\n")
    lines.append(f"**First Comment:**\n\n{kit.get('hn_comment', 'N/A')}\n")

    tweets = kit.get("tweets", [])
    if tweets:
        lines.append("## Tweet Thread\n")
        for i, tweet in enumerate(tweets, 1):
            lines.append(f"**{i}/{len(tweets)}:** {tweet}\n")

    lines.append("## Reddit\n")
    lines.append(f"**Title:** {kit.get('reddit_title', 'N/A')}\n")
    lines.append(f"{kit.get('reddit_body', 'N/A')}\n")

    return "\n".join(lines)
