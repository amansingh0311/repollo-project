// Configuration utility for environment variables
export const config = {
    // Backend API base URL - can be overridden via environment variable
    BACKEND_BASE_URL: process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000',
} as const;

// Helper function to build backend API URLs
export function getBackendUrl(path: string): string {
    const baseUrl = config.BACKEND_BASE_URL;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${baseUrl}${cleanPath}`;
} 