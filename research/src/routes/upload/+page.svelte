<script lang="ts">
    import { apiUpload } from "$lib/api";
    import type { UploadResponse } from "$lib/types";

    let file: File | null = null;
    let result: UploadResponse | null = null;

    function handleFileChange(e: Event) {
        const target = e.target as HTMLInputElement | null;
        if (!target || !target.files || target.files.length === 0) {
            file = null;
            return;
        }
        file = target.files[0];
    }

    async function upload() {
        if (!file) {
            alert("Choose a file first");
            return;
        }
        result = await apiUpload(file);
    }
</script>

<h1>Upload Research Document</h1>

<input type="file" onchange={handleFileChange} />
<button onclick={upload}>Upload</button>

{#if result}
    <p>Uploaded: {result.title}</p>
    <a href={`/generate?doc=${result.document_id}`}>Generate Summary →</a>
{/if}
