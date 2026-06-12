<script lang="ts">
    import { page } from "$app/stores";
    import { apiGenerate } from "$lib/api";
    import { onMount } from "svelte";
    import type { TaskType } from "$lib/types";


    let document_id: number;

    $: document_id = Number($page.url.searchParams.get("doc"));

    let task_type: TaskType = "short_summary";
    let outputFormat: "pdf" | "tex" = "pdf";

    let extra = "";

    type GenerateResult = {
        result_preview: string;
        download_url: string;
        job_id: string | number;
    };

    let result: GenerateResult | null = null;

    async function generate() {
    result = await apiGenerate({
        document_id,
        task_type,
        output_format: task_type === "math_proof" ? outputFormat : undefined,
        extra_instructions: extra
    });
    }

</script>

<h1 style="text-align: center;">Generate Output</h1>

<select bind:value={task_type}>
    <option value="short_summary">Short Summary</option>
    <option value="long_summary">Long Summary</option>
    <option value="research_summary">Research Summary</option>
    <option value="math_proof">Math Proof</option>
</select>

{#if task_type === "math_proof"}
  <select bind:value={outputFormat}>
      <option value="pdf">PDF</option>
      <option value="tex">LaTeX</option>
  </select>
{/if}

<textarea bind:value={extra} placeholder="Extra instructions..."></textarea>

<button onclick={generate}>Generate</button>

{#if result}
    <h2>Result Preview</h2>
    <pre>{result.result_preview}</pre>

    <a href={result.download_url} target="_blank">Download File</a>
    <br />
    <a href={`/jobs/${result.job_id}`}>View Job →</a>
{/if}
