export interface UploadResponse {
    document_id: number;
    title: string;
    filename: string;
}

export type TaskType =
    | "short_summary"
    | "long_summary"
    | "research_summary"
    | "math_proof"
    | "prompt_draft";

export interface GenerateRequest {
    document_id: number;
    task_type: TaskType;
    output_format?: string | null;
    extra_instructions?: string | null;
}

export interface GenerateResponse {
    job_id: number;
    download_url: string;
    result_preview: string;
}

export interface RelatedArticle {
    field: string;
    title: string;
    link: string;
    authors_info: string;
    publication_year: string | null;
    snippet: string | null;
}

export interface RelatedArticlesResponse {
    query: string;
    articles: RelatedArticle[];
}

export interface TagIn {
    name: string;
    value: string;
}

export interface PromptBuilderRequest {
    tags: TagIn[];
    pattern_names: string[];
}

export interface PromptBuilderResponse {
    prompt_text: string;
    score: number;
    accepted: boolean;
    download_url: string | null;
    framework_blend: string[];
    prompt_spec_md: string;
    scoring_rubric_yaml: string;
    prompt_eval_suite_json: string;
    failure_analysis_md: string;
    recommendations: string[];
    structured_spec: Record<string, unknown>;
}
