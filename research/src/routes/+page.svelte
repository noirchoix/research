<script lang="ts">
    import { goto } from "$app/navigation";
    import { apiDownloadJob, apiJobAudio } from "$lib/api";
    import type {
        UploadResponse,
        GenerateResponse,
        RelatedArticlesResponse,
        TaskType
    } from "$lib/types";

    import {
        extractFileFromEvent,
        uploadDocument,
        generateForDocument,
        fetchRelatedArticles
    } from "$lib/landingHelpers";

    // -------------------------------------------
    // Upload state
    // -------------------------------------------
    let file: File | null = null;
    let uploadedDoc: UploadResponse | null = null;

    // -------------------------------------------
    // output format
    let outputFormat: "pdf" | "tex" = "pdf";


    // -------------------------------------------
    // Core state
    // -------------------------------------------
    let selectedTask: TaskType = "short_summary";
    let isGenerating = false;

    let generationResult: GenerateResponse | null = null;
    let resultText = "";

    let audioUrl: string | null = null;
    let downloadUrl: string | null = null;

    // Document meta
    let documentId: number | null = null;
    let documentTitle = "";
    let fileName = "";

    // Related articles
    let related: RelatedArticlesResponse | null = null;
    let relatedLoading = false;

    // -------------------------------------------
    // LOAD RELATED ARTICLES
    // -------------------------------------------
    async function loadRelated(query: string) {
        relatedLoading = true;
        try {
            related = await fetchRelatedArticles(query);
        } catch (err) {
            console.error("Related fetch failed:", err);
        } finally {
            relatedLoading = false;
        }
    }

    // -------------------------------------------
    // FILE UPLOAD
    // -------------------------------------------
    function handleFileChange(e: Event) {
        file = extractFileFromEvent(e);
    }

    async function upload() {
        if (!file) {
            alert("Choose a file first");
            return;
        }

        try {
            const res = await uploadDocument(file);

            uploadedDoc = res;
            documentId = res.document_id;
            documentTitle = res.title;
            fileName = res.filename;

            // Reset old results
            generationResult = null;
            resultText = "";
            audioUrl = null;
            downloadUrl = null;

            if (documentTitle) {
                loadRelated(documentTitle);
            }
        } catch (err) {
            console.error("Upload failed:", err);
            alert("Upload failed");
        }
    }

    // -------------------------------------------
    // GENERATE SUMMARY / ANALYSIS
    // -------------------------------------------
    async function handleGenerate() {
        if (!documentId) {
            alert("Upload a document first.");
            return;
        }

        isGenerating = true;
        resultText = "";
        audioUrl = null;
        downloadUrl = null;

        try {
            const res = await generateForDocument(
            documentId,
            selectedTask,
            selectedTask === "math_proof" ? outputFormat : undefined
        );


            generationResult = res;
            resultText = res.result_preview;
            downloadUrl = apiDownloadJob(res.job_id);

            if (documentTitle) {
                loadRelated(documentTitle);
            }
        } catch (err) {
            console.error("Failed to generate:", err);
            resultText = "Something went wrong.";
        } finally {
            isGenerating = false;
        }
    }

    // -------------------------------------------
    // GENERATE AUDIO (MP3)
    // -------------------------------------------
    async function generateAudio() {
        if (!generationResult) {
            alert("Generate text first.");
            return;
        }
        audioUrl = apiJobAudio(generationResult.job_id);
    }

    // -------------------------------------------
    // DOWNLOAD FILE (DOCX / PDF / TEX)
    // -------------------------------------------
    function downloadFile() {
        if (!downloadUrl) {
            alert("No file yet.");
            return;
        }
        window.open(downloadUrl, "_blank");
    }

    // -------------------------------------------
    // NAVIGATE TO PROMPT BUILDER
    // -------------------------------------------
    function goToPromptBuilder() {
        // Adjust path if your prompt-builder route is different
        goto("/prompt");
    }
</script>

<!-- UI Layout -->
<div class="min-h-screen bg-white px-6 py-6 flex flex-col">
  <!-- Header -->
  <header class="flex items-center justify-between mb-8">
    <h1 class="text-2xl font-bold text-black" style="text-align: center;">Research Assistant</h1>

    <div class="flex flex-col items-end">
      <span class="text-xs uppercase tracking-wide text-gray-500">
        Current document
      </span>

      <button
        class="mt-1 inline-flex items-center gap-2 bg-[#F7F3EB] border border-[#E6DCCB]
               rounded-full px-4 py-2 text-sm text-black"
      >
        <span class="font-medium truncate max-w-xs">
          {documentTitle || (documentId ? `Document #${documentId}` : "No document selected")}
        </span>
        <span class="text-xs text-gray-500">▼</span>
      </button>
    </div>
  </header>

  <!-- Main -->
  <main class="flex-1 grid gap-8 md:grid-cols-[1.1fr_1.6fr]">

    <!-- LEFT COLUMN -->
    <div class="space-y-6">

      <!-- Document Viewer -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5">
        <h2 class="text-sm font-semibold text-gray-700 mb-3">Document details</h2>

        <p class="text-base font-medium text-black">
          {documentTitle || "No document uploaded"}
        </p>
        <p class="text-sm text-gray-600">{fileName || ""}</p>
      </section>

      <!-- UPLOAD SECTION -->
      <section class="bg-[#FFF] border border-[#E6DCCB] rounded-xl p-5 space-y-3">
        <h2 class="text-sm font-semibold text-black">Upload new document</h2>

        <input
          type="file"
          onchange={handleFileChange}
          class="block w-full mb-2"
        />

        <button
          class="w-full bg-[#D8C7A1] py-2 rounded-lg text-black font-semibold"
          onclick={upload}
        >
          Upload
        </button>

        {#if uploadedDoc}
          <p class="text-xs text-green-700">
            Uploaded: {uploadedDoc.title}
          </p>
        {/if}
      </section>

      <!-- TASK SELECTION -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5">
        <h2 class="text-lg font-semibold text-black mb-4">Select a task</h2>

        <!-- Scrollable task list -->
        <div class="space-y-4 max-h-56 overflow-y-auto pr-1">

          <!-- short -->
          <label class="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              bind:group={selectedTask}
              value="short_summary"
              class="mt-1 h-5 w-5"
            />
            <div>
              <p class="text-sm font-semibold text-black">Short summary</p>
              <p class="text-xs text-gray-600">A concise summary.</p>
            </div>
          </label>

          <!-- long -->
          <label class="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              bind:group={selectedTask}
              value="long_summary"
              class="mt-1 h-5 w-5"
            />
            <div>
              <p class="text-sm font-semibold text-black">Long summary</p>
              <p class="text-xs text-gray-600">Full structured review.</p>
            </div>
          </label>

          <!-- research -->
          <label class="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              bind:group={selectedTask}
              value="research_summary"
              class="mt-1 h-5 w-5"
            />
            <div>
              <p class="text-sm font-semibold text-black">Research summary</p>
              <p class="text-xs text-gray-600">Technical contributions overview.</p>
            </div>
          </label>

          <!-- math proof -->
          <label class="flex items-start space-x-3 cursor-pointer">
            <input
              type="radio"
              bind:group={selectedTask}
              value="math_proof"
              class="mt-1 h-5 w-5"
            />
            <div>
              <p class="text-sm font-semibold text-black">Mathematical proof</p>
              <p class="text-xs text-gray-600">Formal logic + LaTeX reasoning.</p>
            </div>
          </label>

          <!-- (Future tasks can be added here and scroll will handle them) -->
        </div>

        {#if selectedTask === "math_proof"}
          <div class="mt-3">
            <label for="outputFormat" class="block text-xs font-semibold text-gray-700 mb-1">
              Output format
            </label>
            <select
              id="outputFormat"
              bind:value={outputFormat}
              class="w-full rounded-md border border-[#E6DCCB] bg-white px-2 py-1 text-sm"
            >
              <option value="pdf">PDF</option>
              <option value="tex">LaTeX (.tex)</option>
            </select>
          </div>
        {/if}


        <!-- Button to go to prompt builder -->
        <button
          type="button"
          class="mt-4 w-full border border-[#E6DCCB] rounded-xl py-2 text-sm bg-white text-black"
          onclick={goToPromptBuilder}
        >
          Generate prompt (advanced)
        </button>
      </section>

      <!-- ACTIONS -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5 space-y-3">
        <button
          class="w-full bg-[#D8C7A1] py-3 rounded-xl text-black font-semibold
                 disabled:opacity-60 disabled:cursor-not-allowed"
          onclick={handleGenerate}
          disabled={isGenerating}
        >
          {#if isGenerating}
            Generating…
          {:else}
            Generate
          {/if}
        </button>

        <div class="flex gap-3">
          <button
            class="flex-1 border rounded-xl py-2 text-sm bg-white text-black"
            onclick={downloadFile}
          >
            Download file
          </button>
          <button
            class="flex-1 border rounded-xl py-2 text-sm bg-white text-black"
            onclick={generateAudio}
          >
            Generate audio
          </button>
        </div>

        {#if audioUrl}
          <audio controls class="w-full mt-3">
            <source src={audioUrl} type="audio/mpeg" />
          </audio>
        {/if}
      </section>
    </div>

    <!-- RIGHT COLUMN -->
    <div class="space-y-6">

      <!-- RESULT -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5 h-2/3 flex flex-col">
        <h2 class="text-lg font-semibold text-black mb-3">Result</h2>

        <div class="flex-1 overflow-auto bg-white p-4 rounded-lg border border-[#E6DCCB]">
          <p class="whitespace-pre-wrap text-sm text-gray-800">
            {resultText || "Generate a task to see output."}
          </p>
        </div>
      </section>

      <!-- RELATED ARTICLES -->
      <section class="bg-[#F7F3EB] border border-[#E6DCCB] rounded-xl p-5">
        <h2 class="text-lg font-semibold mb-3 text-black">Related articles</h2>

        {#if relatedLoading}
          <p class="text-xs text-gray-500">Loading…</p>
        {:else if related}
          <ul class="space-y-2">
            {#each related.articles as paper}
              <li>
                <a
                  href={paper.link}
                  class="underline font-medium text-sm text-black"
                  target="_blank"
                  rel="noreferrer"
                >
                  {paper.title}
                </a>
                <p class="text-xs text-gray-600">
                  {paper.authors_info}
                </p>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-xs text-gray-500">
            Generate something to see suggestions.
          </p>
        {/if}
      </section>
    </div>

  </main>
</div>
