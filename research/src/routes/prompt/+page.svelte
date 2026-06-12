<script lang="ts">
  import { apiPromptBuilder } from "$lib/api";
  import type { PromptBuilderRequest, PromptBuilderResponse, TagIn } from "$lib/types";

  type ArtifactKey = "prompt" | "spec" | "rubric" | "suite" | "failures";

  const ALL_PATTERNS: { name: string; short: string; group: string }[] = [
    { name: "Template Pattern", short: "Template", group: "Reusable" },
    { name: "Chain-of-Thought", short: "Reasoning", group: "Analysis" },
    { name: "Fact Check List", short: "Fact check", group: "Grounding" },
    { name: "Alternative Approaches", short: "Alternatives", group: "Design" },
    { name: "Ask for Input", short: "Clarify", group: "HITL" },
    { name: "Recipe Pattern", short: "Procedure", group: "Process" },
    { name: "Semantic Filter", short: "Filter", group: "Grounding" },
    { name: "ReAct", short: "Tool loop", group: "Agentic" },
    { name: "Menu Actions", short: "Choices", group: "UX" },
    { name: "Tail Generation", short: "Next step", group: "Iteration" },
    { name: "Meta Language Creation", short: "Schema", group: "Reusable" }
  ];

  const presets: { label: string; tags: TagIn[]; patterns: string[] }[] = [
    {
      label: "Production code review",
      patterns: ["Template Pattern", "Chain-of-Thought", "Fact Check List"],
      tags: [
        { name: "objective", value: "Review a software repository for correctness, security, maintainability, release readiness, and exact patch guidance." },
        { name: "audience", value: "Senior developer or technical founder who needs actionable implementation feedback." },
        { name: "output", value: "A structured review with blockers, warnings, file-level fixes, and a final patch checklist." },
        { name: "constraints", value: "Do not invent files or routes. Identify uncertainty. Prioritize production-breaking issues first." }
      ]
    },
    {
      label: "Research synthesis",
      patterns: ["Template Pattern", "Fact Check List", "Alternative Approaches"],
      tags: [
        { name: "objective", value: "Synthesize research material into a grounded, citation-aware technical brief." },
        { name: "audience", value: "Technical reader who needs a concise but evidence-based explanation." },
        { name: "output", value: "Executive summary, evidence map, uncertainty notes, and next research questions." },
        { name: "constraints", value: "Separate facts from inference. Do not overstate source support." }
      ]
    },
    {
      label: "Agent workflow",
      patterns: ["ReAct", "Ask for Input", "Recipe Pattern", "Semantic Filter"],
      tags: [
        { name: "objective", value: "Design a human-in-the-loop agent workflow with tool calls, approval gates, fallback paths, and exportable implementation artifacts." },
        { name: "audience", value: "Automation engineer implementing the workflow in code, n8n, Zapier/Make, or MCP." },
        { name: "output", value: "Workflow schema, node sequence, approval questions, tool contracts, and implementation README." },
        { name: "constraints", value: "Pause before external side effects. Keep secrets out of outputs. Include error branches." }
      ]
    }
  ];

  let tags: TagIn[] = [
    { name: "objective", value: "" },
    { name: "audience", value: "" },
    { name: "output", value: "" },
    { name: "constraints", value: "" }
  ];

  let selectedPatternNames: string[] = ["Template Pattern", "Chain-of-Thought"];
  let isGenerating = false;
  let errorMessage: string | null = null;
  let result: PromptBuilderResponse | null = null;
  let copied = "";
  let activeArtifact: ArtifactKey = "prompt";

  function isPatternSelected(name: string): boolean {
    return selectedPatternNames.includes(name);
  }

  function togglePattern(name: string) {
    selectedPatternNames = isPatternSelected(name)
      ? selectedPatternNames.filter((n) => n !== name)
      : [...selectedPatternNames, name];
  }

  function addTagRow() {
    tags = [...tags, { name: "", value: "" }];
  }

  function removeTagRow(index: number) {
    if (tags.length === 1) return;
    tags = tags.filter((_, i) => i !== index);
  }

  function applyPreset(index: number) {
    const preset = presets[index];
    tags = preset.tags.map((tag) => ({ ...tag }));
    selectedPatternNames = [...preset.patterns];
    result = null;
    activeArtifact = "prompt";
  }

  async function handleGenerate() {
    errorMessage = null;
    result = null;
    copied = "";

    const cleanedTags: TagIn[] = tags
      .map((t) => ({ name: t.name.trim(), value: t.value.trim() }))
      .filter((t) => t.name && t.value);

    if (cleanedTags.length === 0) {
      errorMessage = "Add at least one context field before generating.";
      return;
    }

    if (selectedPatternNames.length === 0) {
      errorMessage = "Select at least one prompt pattern.";
      return;
    }

    const payload: PromptBuilderRequest = {
      tags: cleanedTags,
      pattern_names: selectedPatternNames
    };

    isGenerating = true;
    try {
      result = await apiPromptBuilder(payload);
      activeArtifact = "prompt";
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Prompt generation failed.";
      console.error("Prompt builder error:", err);
      errorMessage = msg;
    } finally {
      isGenerating = false;
    }
  }

  function artifactText(key: ArtifactKey): string {
    if (!result) return "";
    if (key === "prompt") return result.prompt_text;
    if (key === "spec") return result.prompt_spec_md;
    if (key === "rubric") return result.scoring_rubric_yaml;
    if (key === "suite") return result.prompt_eval_suite_json;
    return result.failure_analysis_md;
  }

  async function copyArtifact(key: ArtifactKey) {
    const text = artifactText(key);
    if (!text) return;
    await navigator.clipboard.writeText(text);
    copied = key;
    setTimeout(() => (copied = ""), 1400);
  }

  function downloadPrompt() {
    if (!result?.download_url) return;
    const url = result.download_url.startsWith("/") ? result.download_url : `/${result.download_url}`;
    window.open(url, "_blank");
  }
</script>

<svelte:head>
  <title>Prompt Builder · Research Assistant</title>
</svelte:head>

<div class="prompt-shell">
  <header class="hero">
    <div>
      <p class="eyebrow">Prompt systems studio</p>
      <h1>Upgrade rough ideas into production prompts with evaluation artifacts.</h1>
      <p class="subhead">The rest of the research app stays unchanged. This workspace focuses only on prompt generation, specs, rubrics, regression tests, and failure analysis.</p>
    </div>
    <button type="button" class="primary" onclick={handleGenerate} disabled={isGenerating}>
      {isGenerating ? "Building…" : "Build prompt system"}
    </button>
  </header>

  {#if errorMessage}
    <p class="error-card">{errorMessage}</p>
  {/if}

  <main class="studio-grid">
    <section class="left-stack">
      <div class="panel">
        <div class="panel-head">
          <h2>Starting point</h2>
          <span>optional</span>
        </div>
        <div class="preset-row">
          {#each presets as preset, index}
            <button type="button" onclick={() => applyPreset(index)}>{preset.label}</button>
          {/each}
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <h2>Prompt patterns</h2>
          <span>{selectedPatternNames.length} selected</span>
        </div>
        <div class="pattern-grid">
          {#each ALL_PATTERNS as p}
            <button
              type="button"
              class:selected={isPatternSelected(p.name)}
              onclick={() => togglePattern(p.name)}
            >
              <strong>{p.short}</strong>
              <span>{p.group}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <h2>Context fields</h2>
          <button type="button" class="ghost" onclick={addTagRow}>Add field</button>
        </div>
        <div class="tag-list">
          {#each tags as tag, i}
            <div class="tag-row">
              <input aria-label="Context field name" type="text" placeholder="field" bind:value={tag.name} />
              <textarea aria-label="Context field value" rows="3" placeholder="Value / requirement / example" bind:value={tag.value}></textarea>
              <button type="button" class="remove" onclick={() => removeTagRow(i)}>×</button>
            </div>
          {/each}
        </div>
      </div>
    </section>

    <section class="output-panel">
      {#if result}
        <div class="result-top">
          <div>
            <p class="eyebrow">Generated system</p>
            <h2>{result.accepted ? "Production-ready draft" : "Needs revision"}</h2>
          </div>
          <div class="score-pill">{(result.score * 100).toFixed(0)}%</div>
        </div>

        <div class="artifact-tabs" role="tablist" aria-label="Prompt artifacts">
          <button class:active={activeArtifact === "prompt"} onclick={() => (activeArtifact = "prompt")}>Prompt</button>
          <button class:active={activeArtifact === "spec"} onclick={() => (activeArtifact = "spec")}>Spec</button>
          <button class:active={activeArtifact === "rubric"} onclick={() => (activeArtifact = "rubric")}>Rubric</button>
          <button class:active={activeArtifact === "suite"} onclick={() => (activeArtifact = "suite")}>Tests</button>
          <button class:active={activeArtifact === "failures"} onclick={() => (activeArtifact = "failures")}>Failures</button>
        </div>

        <pre>{artifactText(activeArtifact)}</pre>

        <div class="action-row">
          <button type="button" onclick={() => copyArtifact(activeArtifact)}>{copied === activeArtifact ? "Copied" : "Copy current artifact"}</button>
          <button type="button" onclick={downloadPrompt} disabled={!result.download_url}>Download spec</button>
        </div>

        {#if result.recommendations.length}
          <div class="notes">
            <h3>Production notes</h3>
            {#each result.recommendations as item}
              <p>{item}</p>
            {/each}
          </div>
        {/if}
      {:else}
        <div class="empty-state">
          <svg viewBox="0 0 420 260" aria-hidden="true">
            <rect x="44" y="38" width="332" height="184" rx="26" />
            <path d="M92 92h132M92 122h214M92 152h168" />
            <circle cx="310" cy="168" r="32" />
            <path d="M296 168l10 10 21-24" />
          </svg>
          <h2>Build a prompt, not just a prompt string.</h2>
          <p>Output will include the production prompt, PROMPT_SPEC.md, scoring rubric, regression suite, and failure analysis.</p>
        </div>
      {/if}
    </section>
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    background: #fbf7ef;
    color: #1f1a16;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }

  .prompt-shell {
    min-height: calc(100vh - 56px);
    padding: 30px;
    background:
      radial-gradient(circle at top left, rgba(219, 120, 83, .17), transparent 32%),
      linear-gradient(135deg, #fffaf2 0%, #f6efe3 48%, #fdfbf7 100%);
  }

  .hero {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: flex-start;
    margin-bottom: 20px;
  }

  .eyebrow {
    margin: 0 0 8px;
    font-size: 11px;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: #ad5938;
    font-weight: 700;
  }

  h1 {
    margin: 0;
    max-width: 900px;
    font-size: clamp(34px, 5vw, 64px);
    line-height: .92;
    letter-spacing: -.07em;
    font-weight: 760;
  }

  .subhead {
    max-width: 740px;
    color: #6c625a;
    font-size: 14px;
    line-height: 1.55;
  }

  button {
    border: 0;
    border-radius: 999px;
    padding: 9px 13px;
    cursor: pointer;
    font: inherit;
  }

  button:disabled {
    opacity: .5;
    cursor: not-allowed;
  }

  .primary {
    background: #1f1a16;
    color: #fffaf2;
    min-width: 170px;
  }

  .ghost {
    background: #fffaf2;
    border: 1px solid #ead8c4;
    color: #1f1a16;
    font-size: 12px;
  }

  .error-card {
    background: #fff1ec;
    border: 1px solid #efb8a4;
    color: #8e341f;
    border-radius: 18px;
    padding: 12px 14px;
  }

  .studio-grid {
    display: grid;
    grid-template-columns: minmax(340px, 420px) minmax(0, 1fr);
    gap: 18px;
    align-items: start;
  }

  .left-stack {
    display: grid;
    gap: 14px;
  }

  .panel, .output-panel {
    background: rgba(255, 252, 246, .86);
    border: 1px solid #ead8c4;
    box-shadow: 0 30px 80px rgba(72, 48, 24, .07);
    border-radius: 26px;
    padding: 18px;
  }

  .panel-head, .result-top, .action-row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
  }

  .panel-head h2, .result-top h2, .notes h3 {
    margin: 0;
    font-size: 16px;
    letter-spacing: -.025em;
  }

  .panel-head span {
    font-size: 12px;
    color: #8c7e72;
  }

  .preset-row, .pattern-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .preset-row button {
    background: #1f1a16;
    color: #fffaf2;
    font-size: 12px;
  }

  .pattern-grid button {
    min-width: 112px;
    text-align: left;
    background: #fffaf2;
    color: #1f1a16;
    border: 1px solid #ead8c4;
    border-radius: 16px;
    padding: 11px;
  }

  .pattern-grid button.selected {
    background: #bd6140;
    border-color: #bd6140;
    color: #fffaf2;
  }

  .pattern-grid strong, .pattern-grid span {
    display: block;
  }

  .pattern-grid strong {
    font-size: 12px;
  }

  .pattern-grid span {
    margin-top: 4px;
    font-size: 11px;
    opacity: .75;
  }

  .tag-list {
    display: grid;
    gap: 10px;
    max-height: 48vh;
    overflow: auto;
    padding-right: 3px;
  }

  .tag-row {
    display: grid;
    grid-template-columns: 100px 1fr 28px;
    gap: 8px;
    align-items: start;
  }

  input, textarea {
    width: 100%;
    box-sizing: border-box;
    border: 1px solid #ead8c4;
    background: #fffdf9;
    border-radius: 14px;
    padding: 10px 11px;
    font: inherit;
    font-size: 12px;
    color: #1f1a16;
  }

  textarea {
    resize: vertical;
    line-height: 1.45;
  }

  .remove {
    width: 28px;
    height: 28px;
    padding: 0;
    background: #f4e7d9;
    color: #7b3b27;
  }

  .output-panel {
    min-height: 620px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .score-pill {
    width: 64px;
    height: 64px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: #1f1a16;
    color: #fffaf2;
    font-weight: 760;
  }

  .artifact-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .artifact-tabs button {
    background: #fffaf2;
    border: 1px solid #ead8c4;
    color: #5c5148;
    font-size: 12px;
  }

  .artifact-tabs button.active {
    background: #1f1a16;
    color: #fffaf2;
    border-color: #1f1a16;
  }

  pre {
    flex: 1;
    min-height: 360px;
    max-height: 58vh;
    overflow: auto;
    margin: 0;
    white-space: pre-wrap;
    background: #181310;
    color: #fff8ec;
    border-radius: 20px;
    padding: 16px;
    font-size: 12px;
    line-height: 1.55;
  }

  .action-row button {
    background: #fffaf2;
    border: 1px solid #ead8c4;
    color: #1f1a16;
    font-size: 12px;
  }

  .notes {
    border-top: 1px solid #ead8c4;
    padding-top: 12px;
  }

  .notes p {
    margin: 7px 0 0;
    font-size: 12px;
    color: #6c625a;
    line-height: 1.45;
  }

  .empty-state {
    margin: auto;
    text-align: center;
    max-width: 560px;
  }

  .empty-state svg {
    width: min(420px, 95%);
  }

  .empty-state rect {
    fill: #fffaf2;
    stroke: #ead8c4;
  }

  .empty-state path {
    fill: none;
    stroke: #1f1a16;
    stroke-width: 5;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .empty-state circle {
    fill: #e8a07c;
    stroke: #1f1a16;
    stroke-width: 4;
  }

  .empty-state h2 {
    margin: 8px 0;
    font-size: 24px;
    letter-spacing: -.04em;
  }

  .empty-state p {
    color: #6c625a;
    line-height: 1.5;
  }

  @media (max-width: 1050px) {
    .hero, .studio-grid {
      display: grid;
      grid-template-columns: 1fr;
    }
  }
</style>
