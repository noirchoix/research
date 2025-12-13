<script lang="ts">
  import { apiPromptBuilder } from "$lib/api";
  import type { PromptBuilderRequest, PromptBuilderResponse, TagIn } from "$lib/types";

  const ALL_PATTERNS: { name: string; short: string }[] = [
    { name: "Alternative Approaches", short: "Alternatives" },
    { name: "Ask for Input", short: "Ask for input" },
    { name: "Fact Check List", short: "Fact check" },
    { name: "Menu Actions", short: "Menu actions" },
    { name: "Meta Language Creation", short: "Meta language" },
    { name: "Recipe Pattern", short: "Recipe" },
    { name: "Semantic Filter", short: "Semantic filter" },
    { name: "Tail Generation", short: "Tail" },
    { name: "Template Pattern", short: "Template" },
    { name: "Chain-of-Thought", short: "Chain-of-thought" },
    {name:"ReAct", short: "ReAct"}
  ];

  let tags: TagIn[] = [
    { name: "topic", value: "" },
    { name: "audience", value: "" }
  ];

  let selectedPatternNames: string[] = [];

  let isGenerating = false;
  let errorMessage: string | null = null;

  let result: PromptBuilderResponse | null = null;
  let promptText = "";

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

  async function handleGenerate() {
    errorMessage = null;
    result = null;
    promptText = "";

    const cleanedTags: TagIn[] = tags
      .map((t) => ({ name: t.name.trim(), value: t.value.trim() }))
      .filter((t) => t.name && t.value);

    if (cleanedTags.length === 0) {
      errorMessage = "Please provide at least one tag with a name and value.";
      return;
    }

    if (selectedPatternNames.length === 0) {
      errorMessage = "Please select at least one prompt pattern.";
      return;
    }

    const payload: PromptBuilderRequest = {
      tags: cleanedTags,
      pattern_names: selectedPatternNames
    };

    isGenerating = true;
    try {
      const res = await apiPromptBuilder(payload);
      result = res;
      promptText = res.prompt_text;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Prompt generation failed.";
      console.error("Prompt builder error:", err);
      errorMessage = msg;
    } finally {
      isGenerating = false;
    }
  }

  async function copyPrompt() {
    if (!promptText) return;
    await navigator.clipboard.writeText(promptText);
  }

  function downloadPrompt() {
    if (!result?.download_url) return;
    const url = result.download_url.startsWith("/") ? result.download_url : `/${result.download_url}`;
    window.open(url, "_blank");
  }
</script>

<div class="min-h-screen bg-white px-6 py-6 flex flex-col">
  <!-- Header -->
  <header class="flex items-center justify-between mb-8">
    <h1 class="text-2xl font-bold text-black">Prompt Builder</h1>
    <p class="text-xs text-gray-500 max-w-md text-right">
      Combine prompt patterns with your own tags to generate reusable, high-quality prompts
      for your research workflows.
    </p>
  </header>

  <!-- Main layout: left (tags + patterns), right (result) -->
  <main class="flex-1 grid gap-8 md:grid-cols-[1.1fr_1.6fr]">
    <!-- LEFT PANEL -->
    <div class="space-y-6">
      <!-- Pattern palette -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">
          Prompt patterns
        </h2>
        <p class="text-xs text-gray-600 mb-3">
          Select one or more patterns. These are mapped to pattern embeddings in your backend.
        </p>

        <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          {#each ALL_PATTERNS as p}
            <button
              type="button"
              class={`px-3 py-1 rounded-full text-xs border
                      ${isPatternSelected(p.name)
                          ? "bg-[#D8C7A1] border-[#C0AE82] text-black font-semibold"
                          : "bg-white border-[#E6DCCB] text-gray-700"}`}
              onclick={() => togglePattern(p.name)}
            >
              {p.short}
            </button>
          {/each}
        </div>

        {#if selectedPatternNames.length > 0}
          <p class="mt-3 text-[11px] text-gray-600">
            Selected: {selectedPatternNames.join(", ")}
          </p>
        {:else}
          <p class="mt-3 text-[11px] text-gray-400">
            No patterns selected yet.
          </p>
        {/if}
      </section>

      <!-- Tags (env-var style rows) -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5">
        <h2 class="text-sm font-semibold text-gray-700 mb-2">
          Tags (context)
        </h2>
        <p class="text-xs text-gray-600 mb-3">
          Each tag becomes a &lt;tag&gt; block in the meta-prompt.
          Example: <code>&lt;topic&gt; cancer mitigation</code>.
        </p>

        <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
          {#each tags as tag, i}
            <div class="flex items-start gap-2">
              <!-- Tag name -->
              <input
                type="text"
                class="w-28 rounded-md border border-[#E6DCCB] bg-white px-2 py-1 text-xs"
                placeholder="tag name"
                bind:value={tag.name}
              />

              <!-- Tag value -->
              <textarea
                rows="2"
                class="flex-1 rounded-md border border-[#E6DCCB] bg-white px-2 py-1 text-xs resize-y"
                placeholder="Context / description for this tag"
                bind:value={tag.value}>
              </textarea>

              <!-- Remove row -->
              <button
                type="button"
                class="mt-1 text-xs text-gray-500 hover:text-black"
                onclick={() => removeTagRow(i)}
              >
                ✕
              </button>
            </div>
          {/each}
        </div>

        <button
          type="button"
          class="mt-3 inline-flex items-center text-xs text-black border border-[#E6DCCB]
                 rounded-full px-3 py-1 bg-white"
          onclick={addTagRow}
        >
          + Add tag
        </button>
      </section>

      <!-- Generate button + error -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5 space-y-3">
        {#if errorMessage}
          <p class="text-xs text-red-600">{errorMessage}</p>
        {/if}

        <button
          type="button"
          class="w-full bg-[#D8C7A1] text-black font-semibold py-3 rounded-xl
                 disabled:opacity-60 disabled:cursor-not-allowed text-sm"
          onclick={handleGenerate}
          disabled={isGenerating}
        >
          {#if isGenerating}
            Generating prompt…
          {:else}
            Generate prompt
          {/if}
        </button>
      </section>
    </div>

    <!-- RIGHT PANEL: result -->
    <div class="space-y-4">
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5 h-full flex flex-col">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-black">
            Generated prompt
          </h2>

          {#if result}
            <div class="flex items-center gap-3 text-xs">
              <span class="px-2 py-1 rounded-full border border-[#E6DCCB] bg-white">
                Score: {(result.score * 100).toFixed(0)}%
              </span>
              <span
                class={`px-2 py-1 rounded-full text-xs ${
                    result.accepted
                        ? "bg-green-100 text-green-800 border border-green-300"
                        : "bg-red-100 text-red-700 border border-red-300"
                }`}
              >
                {result.accepted ? "Accepted" : "Rejected"}
              </span>
            </div>
          {/if}
        </div>

        <!-- Prompt text area -->
        <div class="flex-1 overflow-auto border border-[#E6DCCB] rounded-lg bg-white p-4 mb-3">
          <p class="whitespace-pre-wrap text-sm text-gray-800">
            {promptText || "Fill in tags, choose patterns, and click “Generate prompt” to see a draft here."}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-between gap-3 mt-auto">
          <div class="flex gap-2">
            <button
              type="button"
              class="px-3 py-2 rounded-lg border border-[#E6DCCB] bg-white text-xs"
              onclick={copyPrompt}
              disabled={!promptText}
            >
              Copy to clipboard
            </button>

            <button
              type="button"
              class="px-3 py-2 rounded-lg border border-[#E6DCCB] bg-white text-xs"
              onclick={downloadPrompt}
              disabled={!result || !result.download_url}
            >
              Download .txt
            </button>
          </div>

          {#if result?.download_url}
            <a
              href={result.download_url}
              target="_blank"
              rel="noreferrer"
              class="text-[11px] text-gray-600 underline"
            >
              Open saved prompt
            </a>
          {/if}
        </div>
      </section>
    </div>
  </main>
</div>
