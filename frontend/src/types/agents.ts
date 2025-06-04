export interface Agent {
    id: string;
    name: string;
    description: string;
    status: string;
    features?: Record<string, any>;
    capabilities?: Record<string, any>;
    endpoints: Array<{
        name: string;
        path: string;
        description: string;
    }>;
}

export interface ViolationCategory {
    category: string;
    detected: boolean;
    confidence: number;
    description: string;
    evidence?: string[];
}

export interface ImageAnalysisResult {
    has_nsfw: boolean;
    has_violence: boolean;
    has_hate_symbols: boolean;
    extracted_text?: string;
    violations: ViolationCategory[];
    confidence_scores: Record<string, number>;
    processing_notes?: string;
}

export interface TextAnalysisResult {
    has_toxicity: boolean;
    has_hate_speech: boolean;
    has_harassment: boolean;
    has_pii: boolean;
    violations: ViolationCategory[];
    detected_pii: string[];
    confidence_scores: Record<string, number>;
    cleaned_text?: string;
}

export interface ModerationResponse {
    is_safe: boolean;
    overall_risk_level: string;
    summary: string;
    rationale: string;
    image_analysis?: ImageAnalysisResult;
    text_analysis?: TextAnalysisResult;
    violation_categories: string[];
    violations_found: ViolationCategory[];
    processing_time: number;
    content_types_analyzed: string[];
}

export interface BatchModerationResponse {
    results: ModerationResponse[];
    summary_stats: Record<string, number>;
    overall_safe_count: number;
    overall_unsafe_count: number;
    processing_time: number;
}

export interface Citation {
    url: string;
    title: string;
    start_index: number;
    end_index: number;
}

export interface ReasoningStep {
    step_number: number;
    action: string;
    description: string;
    query?: string;
    result: string;
    timestamp: string;
}

export interface ResearchResponse {
    query: string;
    answer: string;
    reasoning_steps: ReasoningStep[];
    safety_check_passed: boolean;
    processing_time: number;
    citations?: Citation[];
    content_moderation_flags?: any;
    timestamp?: string;
}

export interface ImageUpload {
    file: File;
    preview: string;
    id: string;
} 