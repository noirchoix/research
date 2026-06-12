<script lang="ts">
    import { page } from "$app/stores";
    import { apiJobAudio, apiDownloadJob } from "$lib/api";
    import { onMount } from "svelte";

    const job_id = Number($page.params.job_id);
    let audioUrl = "";
    let downloadUrl = "";

    onMount(async () => {
        downloadUrl = await apiDownloadJob(job_id);
    });

    async function generateAudio() {
        audioUrl = await apiJobAudio(job_id);
    }
</script>

<h1>Job {job_id}</h1>

<a href={downloadUrl} target="_blank">Download Result File</a>

<hr />

<button onclick={generateAudio}>Generate Audio</button>

{#if audioUrl}
    <audio controls src={audioUrl}></audio>
{/if}
