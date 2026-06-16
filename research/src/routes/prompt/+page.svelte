<script lang="ts">
  import { apiPromptBuilder, apiUrl } from "$lib/api";
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
      label: "Code review",
      patterns: ["Template Pattern", "Chain-of-Thought", "Fact Check List"],
      tags: [
        { name: "objective", value: "Review a software repository for correctness, security, maintainability, release readiness, and exact patch guidance." },
        { name: "audience", value: "Senior developer or technical founder who needs actionable implementation feedback." },
        { name: "output", value: "Structured review with blockers, warnings, file-level fixes, and a final patch checklist." },
        { name: "constraints", value: "Do not invent files or routes. Identify uncertainty. Prioritize production-breaking issues first." }
      ]
    },
    {
      label: "Research synthesis",
      patterns: ["Template Pattern", "Fact Check List", "Alternative Approaches"],
      tags: [
        { name: "objective", value: "Synthesize research material into a grounded, citation-aware technical brief." },
        { name: "audience", value: "Technical reader who needs concise but evidence-based explanation." },
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
    window.open(apiUrl(result.download_url), "_blank");
  }
</script>

<svelte:head>
  <title>Prompt Builder · Research Assistant</title>
</svelte:head>

<div class="min-h-screen bg-white px-6 py-6 text-black">
  <header class="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
    <div>
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Prompt Builder</p>
      <h1 class="text-2xl font-bold tracking-tight text-black">Build production prompts and evaluation artifacts</h1>
      <p class="mt-2 max-w-3xl text-sm leading-6 text-gray-600">
        Add the prompt goal, select the useful patterns, then generate a copy-ready prompt with a spec, rubric, test suite and failure notes.
      </p>
    </div>

    <button
      type="button"
      class="rounded-lg bg-[#D8C7A1] px-5 py-2 text-sm font-semibold text-black disabled:opacity-50"
      onclick={handleGenerate}
      disabled={isGenerating}
    >
      {isGenerating ? "Generating…" : "Generate prompt"}
    </button>
  </header>

  {#if errorMessage}
    <p class="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>
  {/if}

  <main class="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
    <section class="space-y-5">
      <section class="rounded-xl border border-[#E6DCCB] bg-[#F7F3EB] p-5">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-black">Presets</h2>
          <span class="text-xs text-gray-500">optional</span>
        </div>
        <div class="flex flex-wrap gap-2">
          {#each presets as preset, index}
            <button
              type="button"
              class="rounded-full border border-[#E6DCCB] bg-white px-3 py-2 text-xs font-medium text-black hover:bg-[#EEE5D5]"
              onclick={() => applyPreset(index)}
            >
              {preset.label}
            </button>
          {/each}
        </div>
      </section>

      <section class="rounded-xl border border-[#E6DCCB] bg-white p-5">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-black">Prompt patterns</h2>
          <span class="text-xs text-gray-500">{selectedPatternNames.length} selected</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          {#each ALL_PATTERNS as p}
            <button
              type="button"
              class:selected={isPatternSelected(p.name)}
              class="pattern-card rounded-lg border border-[#E6DCCB] bg-[#FAF8F3] px-3 py-2 text-left hover:bg-[#F1E8D7]"
              onclick={() => togglePattern(p.name)}
            >
              <span class="block text-xs font-semibold text-black">{p.short}</span>
              <span class="block text-[11px] text-gray-500">{p.group}</span>
            </button>
          {/each}
        </div>
      </section>

      <section class="rounded-xl border border-[#E6DCCB] bg-white p-5">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-black">Context fields</h2>
          <button
            type="button"
            class="rounded-full border border-[#E6DCCB] bg-[#F7F3EB] px-3 py-1.5 text-xs font-medium text-black"
            onclick={addTagRow}
          >
            Add field
          </button>
        </div>

        <div class="space-y-3">
          {#each tags as tag, i}
            <div class="grid gap-2 rounded-lg border border-[#EEE5D5] bg-[#FBFAF7] p-3">
              <div class="flex gap-2">
                <input
                  aria-label="Context field name"
                  class="w-36 rounded-lg border border-[#E6DCCB] bg-white px-3 py-2 text-sm outline-none focus:border-[#D8C7A1]"
                  type="text"
                  placeholder="field"
                  bind:value={tag.name}
                />
                <button
                  type="button"
                  class="ml-auto h-9 w-9 rounded-lg bg-[#F1E8D7] text-sm font-semibold text-[#7A4A22] disabled:opacity-40"
                  onclick={() => removeTagRow(i)}
                  disabled={tags.length === 1}
                  aria-label="Remove context field"
                >
                  ×
                </button>
              </div>
              <textarea
                aria-label="Context field value"
                class="min-h-20 resize-y rounded-lg border border-[#E6DCCB] bg-white px-3 py-2 text-sm leading-6 outline-none focus:border-[#D8C7A1]"
                rows="3"
                placeholder="Value, requirement, rule or example"
                bind:value={tag.value}
              ></textarea>
            </div>
          {/each}
        </div>
      </section>
    </section>

    <section class="min-h-[620px] rounded-xl border border-[#E6DCCB] bg-white p-5">
      {#if result}
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">Generated artifacts</p>
            <h2 class="text-lg font-semibold text-black">{result.accepted ? "Ready for review" : "Needs revision"}</h2>
          </div>
          <span class="rounded-full bg-[#F7F3EB] px-3 py-1.5 text-xs font-semibold text-black">
            {(result.score * 100).toFixed(0)}%
          </span>
        </div>

        <div class="mb-4 flex flex-wrap gap-2" role="tablist" aria-label="Prompt artifacts">
          <button class:active={activeArtifact === "prompt"} type="button" class="artifact-tab" onclick={() => (activeArtifact = "prompt")}>Prompt</button>
          <button class:active={activeArtifact === "spec"} type="button" class="artifact-tab" onclick={() => (activeArtifact = "spec")}>Spec</button>
          <button class:active={activeArtifact === "rubric"} type="button" class="artifact-tab" onclick={() => (activeArtifact = "rubric")}>Rubric</button>
          <button class:active={activeArtifact === "suite"} type="button" class="artifact-tab" onclick={() => (activeArtifact = "suite")}>Tests</button>
          <button class:active={activeArtifact === "failures"} type="button" class="artifact-tab" onclick={() => (activeArtifact = "failures")}>Failures</button>
        </div>

        <pre class="min-h-[360px] max-h-[58vh] overflow-auto whitespace-pre-wrap rounded-xl bg-[#111] p-4 text-xs leading-6 text-[#F7F3EB]">{artifactText(activeArtifact)}</pre>

        <div class="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-lg bg-[#D8C7A1] px-4 py-2 text-sm font-semibold text-black"
            onclick={() => copyArtifact(activeArtifact)}
          >
            {copied === activeArtifact ? "Copied" : "Copy current"}
          </button>
          <button
            type="button"
            class="rounded-lg border border-[#E6DCCB] bg-white px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
            onclick={downloadPrompt}
            disabled={!result.download_url}
          >
            Download spec
          </button>
        </div>

        {#if result.recommendations.length}
          <div class="mt-5 border-t border-[#E6DCCB] pt-4">
            <h3 class="mb-2 text-sm font-semibold text-black">Notes</h3>
            <div class="space-y-2">
              {#each result.recommendations as item}
                <p class="text-sm leading-6 text-gray-600">{item}</p>
              {/each}
            </div>
          </div>
        {/if}
      {:else}
        <div class="flex min-h-[520px] flex-col items-center justify-center text-center">
          <div class="mb-4 rounded-2xl border border-[#E6DCCB] bg-[#F7F3EB] p-5">
            <svg class="h-24 w-32" viewBox="0 0 240 160" aria-hidden="true">
              <rect x="34" y="30" width="172" height="100" rx="18" fill="white" stroke="#D8C7A1" />
              <path d="M66 64h78M66 84h108M66 104h82" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round" />
              <circle cx="174" cy="104" r="18" fill="#D8C7A1" stroke="#111" stroke-width="4" />
              <path d="M166 104l6 6 13-16" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-black">No prompt generated yet</h2>
          <p class="mt-2 max-w-md text-sm leading-6 text-gray-600">
            Use the fields on the left to generate a prompt, prompt spec, scoring rubric, test suite and failure analysis.
          </p>
        </div>
      {/if}
    </section>
  </main>
</div>

<style>
  .pattern-card.selected {
    background: #D8C7A1;
    border-color: #D8C7A1;
  }

  .artifact-tab {
    border: 1px solid #E6DCCB;
    background: #F7F3EB;
    color: #111;
    border-radius: 999px;
    padding: 0.45rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .artifact-tab.active {
    background: #111;
    border-color: #111;
    color: #F7F3EB;
  }
</style>
