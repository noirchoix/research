<script lang="ts">
    import { apiUpload } from "$lib/api";
    import type { UploadResponse } from "$lib/types";

    let file: File | null = null;
    let result: UploadResponse | null = null;
    let errorMessage = "";
    let isUploading = false;

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
            errorMessage = "Choose a file first";
            return;
        }
        errorMessage = "";
        isUploading = true;
        try {
            result = await apiUpload(file);
        } catch (err) {
            errorMessage = err instanceof Error ? err.message : "Upload failed";
        } finally {
            isUploading = false;
        }
    }
</script>

<h1>Upload Research Document</h1>

<input type="file" onchange={handleFileChange} />
<button onclick={upload} disabled={isUploading}>{isUploading ? "Uploading..." : "Upload"}</button>

{#if errorMessage}
    <p style="color: #b91c1c;">{errorMessage}</p>
{/if}

{#if result}
    <p>Uploaded: {result.title}</p>
    <a href={`/generate?doc=${result.document_id}`}>Generate Summary →</a>
{/if}
