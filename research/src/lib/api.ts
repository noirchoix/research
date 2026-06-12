import type {
    UploadResponse,
    GenerateRequest,
    GenerateResponse,
    RelatedArticlesResponse,
    PromptBuilderRequest, 
    PromptBuilderResponse
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE) {
    throw new Error("VITE_API_BASE_URL is not defined");
}


export async function apiUpload(file: File): Promise<UploadResponse> {
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: form
    });

    if (!res.ok) {
        throw new Error("Upload failed");
    }

    return res.json();
}

export async function apiGenerate(body: GenerateRequest): Promise<GenerateResponse> {
    const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!res.ok) {
        throw new Error("Generation failed");
    }

    return res.json();
}

// ------------------ FIXED HERE ------------------

export function apiDownloadJob(job_id: number): string {
    return `/api/jobs/${job_id}/download`;
}

export function apiJobAudio(job_id: number): string {
    return `/api/jobs/${job_id}/audio`;
}

// ------------------------------------------------

export async function apiRelated(query: string): Promise<RelatedArticlesResponse> {
    const res = await fetch(`/api/related?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error("Related articles fetch failed");
    return res.json();
}


export async function apiPromptBuilder(
    body: PromptBuilderRequest
): Promise<PromptBuilderResponse> {
    const res = await fetch(`${API_BASE}/api/prompt-builder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!res.ok) {
        const msg = await res.text().catch(() => "Prompt builder failed");
        throw new Error(msg || "Prompt builder failed");
    }

    return res.json();
}
