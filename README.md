# README Studio

Web app that generates polished README.md files from project descriptions. Fill in a form with your tool's details and get a professional README with rendered preview, plus optional launch materials for Product Hunt, Hacker News, Twitter, and Reddit.

## Features

- **AI-Powered Generation** - Uses GPT to create comprehensive, well-structured READMEs
- **Live Preview** - See rendered markdown alongside raw source
- **Copy and Download** - One-click copy to clipboard or download as .md file
- **Launch Kit** - Generate Product Hunt tagline, HN post, tweet thread, and Reddit post
- **Offline Mode** - Generate basic READMEs without an API key using templates
- **JSON API** - Programmatic access via POST /api/generate
- **Tailwind UI** - Clean, responsive interface

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/readme-studio.git
cd readme-studio
pip install -r requirements.txt

# Set API key (optional - offline mode works without it)
export OPENAI_API_KEY=sk-xxx

# Run
python app.py
```

Open http://localhost:5000 in your browser.

## Usage

### Web Interface

1. Fill in your project details (name, one-liner, features, commands, etc.)
2. Optionally check "Generate Launch Kit" for marketing materials
3. Click "Generate README"
4. Switch between Preview and Raw Markdown tabs
5. Copy to clipboard or download the .md file

### API

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-tool",
    "one_liner": "A CLI that does amazing things",
    "language": "Python",
    "features": "Fast processing\nPlugin support\nDocker ready",
    "commands": "mytool init\nmytool build",
    "launch_kit": true
  }'
```

Response:
```json
{
  "name": "my-tool",
  "markdown": "# my-tool\n\n...",
  "sections": {"Features": "...", "Installation": "..."},
  "launch_kit": {
    "product_hunt_tagline": "...",
    "hn_title": "...",
    "tweets": ["...", "...", "..."],
    "reddit_title": "..."
  }
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (optional, enables AI generation) |
| `PORT` | 5000 | Server port |
| `FLASK_DEBUG` | 1 | Debug mode (set to 0 in production) |
| `SECRET_KEY` | auto | Flask secret key |

## License

MIT
