const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || 'http://localhost:8000';

export async function GET() {
    try {
        // Get health status for both agents to determine availability
        const [researchResponse, moderationResponse] = await Promise.all([
            fetch(`${BACKEND_URL}/research/health`),
            fetch(`${BACKEND_URL}/moderation/health`)
        ]);

        const researchHealth = researchResponse.ok ? await researchResponse.json() : null;
        const moderationHealth = moderationResponse.ok ? await moderationResponse.json() : null;

        const agents = [
            {
                id: 'research',
                name: 'Research Agent',
                description: 'AI-powered research assistant with web search capabilities and advanced safety features',
                status: researchHealth ? 'healthy' : 'unhealthy',
                features: researchHealth?.features || {},
                endpoints: [
                    { name: 'Research Query', path: '/research/query', description: 'Submit research queries with advanced validation' },
                    { name: 'Quick Search', path: '/research/quick-search', description: 'Fast web search with basic validation' },
                    { name: 'Validate Query', path: '/research/validate-query', description: 'Test query safety without research' }
                ]
            },
            {
                id: 'moderation',
                name: 'Content Moderation Agent',
                description: 'Multi-modal content analysis for safety and policy compliance',
                status: moderationHealth ? 'healthy' : 'unhealthy',
                capabilities: moderationHealth?.capabilities || {},
                endpoints: [
                    { name: 'Analyze Content', path: '/moderation/analyze', description: 'Analyze text and/or image content' },
                    { name: 'Quick Check', path: '/moderation/quick-check', description: 'Fast safety check for high-volume scenarios' },
                    { name: 'Batch Analyze', path: '/moderation/batch-analyze', description: 'Analyze multiple items in batch' }
                ]
            }
        ];

        return Response.json({ agents });
    } catch (error) {
        console.error('Error fetching agents:', error);
        return Response.json(
            { error: 'Failed to fetch agents', details: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
} 