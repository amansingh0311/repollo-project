const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

export async function POST(request: Request) {
    try {
        const body = await request.json();

        const response = await fetch(`${BACKEND_URL}/moderation/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            return Response.json(data, { status: response.status });
        }

        return Response.json(data);
    } catch (error) {
        console.error('Error in moderation analysis:', error);
        return Response.json(
            { error: 'Failed to process moderation analysis', details: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
} 