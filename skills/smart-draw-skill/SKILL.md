---
name: smart-draw
description: >-
  Use when the user wants to create any technical diagram - architecture,
  flowchart, sequence, ER, data flow, mind map, or any visual diagram.
  Trigger on: "画图" "帮我画" "生成图" "做个图" "架构图" "流程图" "可视化" "出图"
  "generate diagram" "draw diagram" "visualize" "architecture diagram"
  "create chart" or any request to visualize a system/flow/process.
---

# Smart Draw — AI-Powered Diagram Creation with Quality Review

Generate high-quality draw.io diagrams through a three-phase pipeline:
1. **Plan** — clarify intent, produce a Blueprint JSON, get user confirmation
2. **Generate** — call next-ai-draw-io MCP server with structured prompt
3. **Review & Fix** — layered quality review with automatic repair

**Prerequisites:** This skill requires the next-ai-draw-io MCP server. If the user triggers this skill but the MCP server is not configured, tell them:
> "Smart Draw requires the next-ai-draw-io MCP server. Run: `claude mcp add drawio -- npx @next-ai-drawio/mcp-server@latest`"

To verify MCP is available, try calling any drawio MCP tool. If it fails with "tool not found", the server is not configured.

---

## Phase 1: Structure Planning

When triggered, DO NOT immediately generate a diagram. Instead, follow this workflow:

### Step 1: Analyze User Intent

From the user's message, extract what you already know:
- **Diagram type**: architecture / flowchart / sequence / ER / data-flow / mind-map / comparison / state-machine / class-diagram
- **Components mentioned**: list of services, actors, databases, etc.
- **Relationships mentioned**: connections between components
- **Layout preference**: top-to-bottom (default), left-to-right, radial
- **Icon library**: AWS (aws4), Azure (azure2), GCP (gcp2), Kubernetes (kubernetes), or none
- **Reference material**: does the user mention an existing diagram, image, or XML?

### Step 2: Ask Clarifying Questions (Max 2 Rounds)

Based on what's missing, ask focused questions. Ask ONLY about missing information — do not re-ask what the user already provided.

**Prioritized questions (ask only what's needed):**

1. If diagram type is unclear: "What type of diagram do you need? (architecture / flowchart / sequence / ER / data-flow / mind-map)"
2. If components are not listed: "What are the main components/services in this system?"
3. If cloud icons might be relevant: "Should I use cloud provider icons? (AWS / Azure / GCP / none)"
4. If the user might have a reference: "Do you have a reference diagram or existing XML you can share?"

**Rules:**
- Maximum 2 rounds of questions total
- If the user's original message is already detailed enough, skip directly to Step 3
- Never ask more than 2 questions per round
- Default layout: top-to-bottom
- Default style: clean, minimal

### Step 3: Produce Blueprint JSON

Based on collected information, generate a Blueprint JSON:

```json
{
  "diagram_type": "<type>",
  "title": "<human-readable title>",
  "layout": "top-to-bottom | left-to-right | radial",
  "icon_library": "<library-name or null>",
  "groups": [
    { "id": "g1", "label": "<group display name>", "node_ids": ["n1", "n2"] }
  ],
  "nodes": [
    { "id": "n1", "label": "<display name>", "shape": "<shape-type>" }
  ],
  "edges": [
    { "id": "e1", "from": "<source-node-id>", "to": "<target-node-id>", "label": "<edge label>", "type": "primary | control | data" }
  ]
}
```

**Shape reference:**
- Service/API: `rounded_rect`
- User/Actor: `circle`
- Database/Store: `cylinder`
- Gateway/Proxy: `hexagon`
- Decision point: `diamond`
- External system: `dashed_rect`
- Container/Group: `container`

### Step 4: Present Blueprint for User Confirmation

Show the Blueprint to the user in a readable format and ask:
> "Here's the planned structure for your diagram. Does this look right? You can add/remove/rename components before I generate it."

Wait for user confirmation before proceeding to Phase 2. If the user requests changes, update the Blueprint and re-confirm.

**If user says it looks good → proceed to Phase 2.**

---

## Phase 2: Structured Generation

Once the Blueprint is confirmed, convert it to a structured prompt and call the MCP server.

### Step 1: Load Icon Library (if needed)

If `icon_library` is set in the Blueprint, call the MCP tool first:
```
get_shape_library(library="<icon_library>")
```
This ensures correct icon syntax. NEVER guess icon shapes — always look them up.

### Step 2: Convert Blueprint to Generation Prompt

Build a natural language prompt from the Blueprint for the MCP display_diagram call:

```
Create a {diagram_type} diagram titled "{title}".
Layout: {layout} direction.
{groups.count} sections/layers:
{for each group: "- {group.label}: {comma-separated node labels}"}

Components:
{for each node: "- {node.label} as {node.shape}"}

Connections:
{for each edge: "- {source.label} → {target.label} ({edge.label})"}

Requirements:
- Use {icon_library} icon library for all cloud/infra components
- Keep all elements within 800×600 viewport
- Minimum 50px gap between elements
- Use orthogonal edge routing (edgeStyle=orthogonalEdgeStyle)
- All edges must specify exitX, exitY, entryX, entryY
- Route edges around intermediate nodes, never through them
```

### Step 3: Call MCP display_diagram

Use the MCP tool:
```
display_diagram(xml="<generated xml>")
```

### Step 4: Handle Truncation

If the MCP response indicates output was truncated, call:
```
append_diagram(xml="<continuation fragment>")
```
Continue until the full diagram is generated.

### Step 5: Proceed to Phase 3

After the diagram is generated (even if there are visible issues), proceed to Phase 3 for quality review. Do NOT attempt to fix issues manually before the review phase.

---

## Phase 3: Layered Review & Fix Loop

After diagram generation, run a two-layer quality review. Track the review iteration count.

**Initialize:** `review_iteration = 0`

### Layer 1: XML Text Review (Inline — No Subagent)

Perform these checks directly on the generated XML:

#### Critical Checks (must fix before proceeding)

1. **Tag closure**: Every `<mxCell ...>` must end with `/>` or have a closing `</mxCell>`
2. **ID uniqueness**: Extract all `id="..."` values — no duplicates allowed
3. **Reference integrity**: Every `source="X"` and `target="Y"` on edge cells must reference IDs that exist as vertex cells
4. **Blueprint node coverage**: Every node ID in the Blueprint must appear in the XML
5. **Blueprint edge coverage**: Every edge in the Blueprint must have a corresponding edge element

**If any critical check fails:**
- Call `edit_diagram` to fix the specific issue
- Re-run Layer 1 checks (this loop is unlimited — syntactic fixes are deterministic)
- Do NOT increment the review counter for Layer 1 fixes

**When all critical checks pass → proceed to Layer 2.**

#### Warning Checks (record for Layer 2)

1. **Coordinate overlap**: For each pair of vertex cells, check if bounding boxes overlap (min 20px gap)
2. **Viewport bounds**: All x,y coordinates should be within 0-800 x 0-600
3. **Edge routing**: Check if edge waypoints would visually cross through unrelated nodes

Record any warnings found. Pass them to the Layer 2 subagent as additional context.

### Layer 2: Visual Review (Subagent)

Increment: `review_iteration += 1`

If `review_iteration > 3`: skip review, show diagram with remaining warnings.

Otherwise, dispatch a review subagent:

```
Agent({
  subagent_type: "claude",
  description: "Review diagram quality",
  prompt: "<contents of references/review-prompt.md>\n\n## Input\n\n### Blueprint\n```json\n<blueprint_json>\n```\n\n### Generated XML\n```xml\n<current_xml>\n```\n\n### Warnings from Layer 1\n<list_of_warnings_or_none>"
})
```

**Read the references/review-prompt.md file** to get the subagent's instructions. Pass the Blueprint and current XML as input.

### Process Review Results

The subagent returns a JSON response:

**If `{ "status": "pass" }`:**
- Review complete. Show the final diagram to the user.
- Output: "Diagram generated and quality-checked. You can see it in your browser and make manual adjustments in draw.io."

**If `{ "status": "issues", "issues": [...] }`:**
- For each `critical` issue:
  1. Apply the `suggested_fix` via `edit_diagram`
  2. After all critical fixes applied, go back to Layer 1 (do NOT increment counter for Layer 1 re-checks)
- For `minor` issues:
  - Attempt to fix if the suggested_fix is specific enough
  - Skip if the fix is vague

**After fixes → re-run Layer 2 (which increments the counter again).**

### Loop Guard

If `review_iteration >= 3` and issues remain:
- Show the current diagram
- List remaining unfixed issues
- Tell user: "The diagram has some remaining issues: <list>. You can manually adjust these in draw.io."

### Success Output

When review passes, report to the user:
- Confirm the diagram type and title
- Note the number of review iterations performed
- Remind user they can manually adjust in draw.io or request further changes in chat
