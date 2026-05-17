---
name: first-time-setup
description: First-time setup flow for image-content-to-xhs preferences
---

# First-Time Setup

## Overview

When no preferences file is found, guide user through preference setup.

**⛔ BLOCKING OPERATION**: This setup MUST complete before ANY other workflow steps. Do NOT:
- Ask about content/article
- Ask about style or layout
- Ask about target audience
- Proceed to content analysis

ONLY ask the questions in this setup flow, save preferences, then continue.

## Setup Flow

```
No preferences found
        │
        ▼
┌─────────────────────┐
│ AskUserQuestion     │
│ (all questions)     │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Create preferences  │
└─────────────────────┘
        │
        ▼
    Continue to Step 1
```

## Questions

**Language**: Use user's input language or saved language preference.

Use single AskUserQuestion with multiple questions (AskUserQuestion auto-adds "Other" option):

### Question 1: Watermark

```
header: "Watermark"
question: "Watermark text for generated images? Type your watermark content (e.g., name, @handle)"
options:
  - label: "No watermark (Recommended)"
    description: "No watermark, can enable later in preferences"
```

Position defaults to bottom-right.

### Question 2: Preferred Style

```
header: "Style"
question: "Default visual style preference? Or type another style name or your custom style"
options:
  - label: "None (Recommended)"
    description: "Auto-select based on content analysis"
  - label: "cute"
    description: "Sweet, adorable - classic XHS aesthetic"
  - label: "notion"
    description: "Minimalist hand-drawn, intellectual"
```

### Question 3: Save Location

```
header: "Save"
question: "Where to save preferences?"
options:
  - label: "Project"
    description: ".dragonskills/ (this project only)"
  - label: "User"
    description: "~/.dragonskills/ (all projects)"
```

## Save Locations

| Choice | Path | Scope |
|--------|------|-------|
| Project | `.dragonskills/image-content-to-xhs/EXTEND.md` | Current project |
| User | `~/.dragonskills/image-content-to-xhs/EXTEND.md` | All projects |

## After Setup

1. Create directory if needed
2. Write preferences file with frontmatter
3. Confirm: "Preferences saved to [path]"
4. Continue to Step 1

## Preferences Template

```yaml
---
version: 1
watermark:
  enabled: [true/false]
  content: "[user input or empty]"
  position: bottom-right
  opacity: 0.7
preferred_style:
  name: [selected style or null]
  description: ""
preferred_layout: null
language: null
custom_styles: []
---
```

## Modifying Preferences Later

Users can edit preferences directly or run setup again:
- Delete preferences file to trigger setup
- Edit YAML frontmatter for quick changes
- Full schema: `config/preferences-schema.md`
