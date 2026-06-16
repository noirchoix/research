import type {
    UploadResponse,
    GenerateRequest,
    GenerateResponse,
    RelatedArticlesResponse,
    PromptBuilderRequest,
    PromptBuilderResponse
} from "./types";

const configuredBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();

// The backend for this repo is normally started from the project root with:
// python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8009
// Keep a safe default so the frontend does not silently break when .env is missing.
const API_BASE = (configuredBase && configuredBase !== "/" ? configuredBase : "http://127.0.0.1:8009").replace(/\/$/, "");

export function apiUrl(path: string): string {
    if (/^https?:\/\//i.test(path)) return path;
    return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}

async function readError(res: Response, fallback: string): Promise<string> {
    try {
        const text = await res.text();
        if (!text) return fallback;
        try {
            const parsed = JSON.parse(text);
            if (typeof parsed?.detail === "string") return parsed.detail;
            return JSON.stringify(parsed);
        } catch {
            return text;
        }
    } catch {
        return fallback;
    }
}

export async function apiUpload(file: File): Promise<UploadResponse> {
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(apiUrl("/api/upload"), {
        method: "POST",
        body: form
    });

    if (!res.ok) {
        throw new Error(await readError(res, "Upload failed"));
    }

    return res.json();
}

export async function apiGenerate(body: GenerateRequest): Promise<GenerateResponse> {
    const res = await fetch(apiUrl("/api/generate"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!res.ok) {
        throw new Error(await readError(res, "Generation failed"));
    }

    return res.json();
}

export function apiDownloadJob(job_id: number): string {
    return apiUrl(`/api/jobs/${job_id}/download`);
}

export function apiJobAudio(job_id: number): string {
    return apiUrl(`/api/jobs/${job_id}/audio`);
}

export async function apiRelated(query: string): Promise<RelatedArticlesResponse> {
    const res = await fetch(apiUrl(`/api/related?query=${encodeURIComponent(query)}`));
    if (!res.ok) {
        throw new Error(await readError(res, "Related articles fetch failed"));
    }
    return res.json();
}

export async function apiPromptBuilder(
    body: PromptBuilderRequest
): Promise<PromptBuilderResponse> {
    const res = await fetch(apiUrl("/api/prompt-builder"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!res.ok) {
        throw new Error(await readError(res, "Prompt builder failed"));
    }

    return res.json();
}
