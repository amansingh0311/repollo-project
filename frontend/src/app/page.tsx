'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Search, Shield, AlertTriangle } from 'lucide-react';

import { AgentsOverview } from '@/components/AgentsOverview';
import { ResearchAgent } from '@/components/ResearchAgent';
import { ModerationAgent } from '@/components/ModerationAgent';
import { Agent } from '@/types/agents';

export default function Home() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch agents');
      }

      setAgents(data.agents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading agents...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Alert className="max-w-md">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center mb-12">
          <Image
            src="/repollo-logo.svg"
            alt="Repollo Logo"
            width={180}
            height={48}
            className="mb-6"
            priority
          />
          <h1 className="text-4xl font-bold mb-2 text-center">
            AI Agents Dashboard
          </h1>
          <p className="text-muted-foreground text-center">
            Interact with research and content moderation agents
          </p>
        </div>

        {/* Agents Overview */}
        <AgentsOverview agents={agents} />

        {/* Interactive Panels */}
        <Tabs defaultValue="research" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger
              value="research"
              className="flex items-center space-x-2"
            >
              <Search className="h-4 w-4" />
              <span>Research Agent</span>
            </TabsTrigger>
            <TabsTrigger
              value="moderation"
              className="flex items-center space-x-2"
            >
              <Shield className="h-4 w-4" />
              <span>Moderation Agent</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="research">
            <ResearchAgent />
          </TabsContent>

          <TabsContent value="moderation">
            <ModerationAgent />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
