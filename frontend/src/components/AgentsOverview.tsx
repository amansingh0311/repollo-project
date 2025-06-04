import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, Shield, CheckCircle, XCircle } from 'lucide-react';
import { Agent } from '@/types/agents';

interface AgentsOverviewProps {
  agents: Agent[];
}

export function AgentsOverview({ agents }: AgentsOverviewProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      {agents.map((agent) => (
        <Card key={agent.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {agent.id === 'research' ? (
                  <Search className="h-5 w-5 text-blue-500" />
                ) : (
                  <Shield className="h-5 w-5 text-green-500" />
                )}
                <CardTitle>{agent.name}</CardTitle>
              </div>
              <Badge
                variant={agent.status === 'healthy' ? 'default' : 'destructive'}
              >
                {agent.status === 'healthy' ? (
                  <CheckCircle className="h-3 w-3 mr-1" />
                ) : (
                  <XCircle className="h-3 w-3 mr-1" />
                )}
                {agent.status}
              </Badge>
            </div>
            <CardDescription>{agent.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Available Endpoints:</h4>
              {agent.endpoints.map((endpoint, idx) => (
                <div key={idx} className="text-sm">
                  <span className="font-medium">{endpoint.name}</span>
                  <span className="text-muted-foreground ml-2">
                    - {endpoint.description}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
