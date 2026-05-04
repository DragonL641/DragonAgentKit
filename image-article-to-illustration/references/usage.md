# Usage

## Command Syntax

```bash
# Auto-select type and style based on content
/image-article-to-illustration path/to/article.md

# Specify type
/image-article-to-illustration path/to/article.md --type infographic

# Specify style
/image-article-to-illustration path/to/article.md --style blueprint

# Combine type and style
/image-article-to-illustration path/to/article.md --type flowchart --style notion

# Specify density
/image-article-to-illustration path/to/article.md --density rich

# Direct content input (paste mode)
/image-article-to-illustration
[paste content]
```

## Options

| Option | Description |
|--------|-------------|
| `--type <name>` | Illustration type (see Type Gallery in SKILL.md) |
| `--style <name>` | Visual style (see references/styles.md) |
| `--density <level>` | Image count: minimal / balanced / rich |

## Input Modes

| Mode | Trigger | Output Directory |
|------|---------|------------------|
| File path | `path/to/article.md` | Use `default_output_dir` preference, or ask if not set |
| Paste content | No path argument | `illustrations/{topic-slug}/` |

## Output Directory Options

| Value | Path |
|-------|------|
| `same-dir` | `{article-dir}/` |
| `illustrations-subdir` | `{article-dir}/illustrations/` |
| `independent` | `illustrations/{topic-slug}/` |

Configure in preferences: `default_output_dir: illustrations-subdir`

## Examples

**Technical article with data**:
```bash
/image-article-to-illustration api-design.md --type infographic --style blueprint
```

**Personal story**:
```bash
/image-article-to-illustration journey.md --type scene --style warm
```

**Tutorial with steps**:
```bash
/image-article-to-illustration how-to-deploy.md --type flowchart --density rich
```
