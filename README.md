# ultimate-ai-image-video-generator

A Codex skill for end-to-end image/video generation on CyberBara Public API v1.

## What it does

- List available image/video models
- Upload reference images
- Quote credits before submission
- Create image/video generation tasks
- Poll task status until final output URLs are ready

## Install this skill

Install with Codex skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo ZeroLu/ultimate-ai-image-video-generator \
  --path .
```

Or install via direct URL:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/ZeroLu/ultimate-ai-image-video-generator/tree/main
```

Then restart Codex.

## Usage

After installation, follow `SKILL.md` in this repository.

Direct CLI entrypoint in this skill:

```bash
python3 scripts/cyberbara_api.py --help
```

## API Key

Get your key at:

- https://cyberbara.com/settings/apikeys

Set it in terminal:

```bash
export CYBERBARA_API_KEY="<your_api_key>"
```

## License

No license file is included yet. Add one if you plan to accept external contributions.
