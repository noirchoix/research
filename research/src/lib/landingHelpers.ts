import {
    apiUpload,
    apiGenerate,
    apiRelated
} from "$lib/api";

import type {
    UploadResponse,
    GenerateResponse,
    RelatedArticlesResponse,
    TaskType
} from "$lib/types";

/**
 * Safely extract a File from an <input type="file"> change event.
 */
export function extractFileFromEvent(e: Event): File | null {
    const target = e.target as HTMLInputElement | null;
    if (!target?.files || target.files.length === 0) {
        return null;
    }
    return target.files[0];
}

/**
 * Upload a document via the backend upload endpoint.
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
    return apiUpload(file);
}

/**
 * Generate output for a specific document and task type.
 */
type MathProofFormat = "pdf" | "tex";

export async function generateForDocument(
    documentId: number,
    task: TaskType,
    outputFormat?: MathProofFormat
): Promise<GenerateResponse> {
    return apiGenerate({
        document_id: documentId,
        task_type: task,
        output_format: task === "math_proof" ? (outputFormat ?? "pdf") : undefined
    });
}
/**
 * Fetch related articles for a given query string.
 */
export async function fetchRelatedArticles(
    query: string
): Promise<RelatedArticlesResponse> {
    return apiRelated(query);
}
