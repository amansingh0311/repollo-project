import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Loader2,
  Search,
  Clock,
  AlertTriangle,
  ExternalLink,
  FileText,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { ResearchResponse } from '@/types/agents';

export function ResearchAgent() {
  const [researchQuery, setResearchQuery] = useState('');
  const [researchLoading, setResearchLoading] = useState(false);
  const [researchResponse, setResearchResponse] =
    useState<ResearchResponse | null>(null);
  const [researchError, setResearchError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleResearchQuery = async () => {
    if (!researchQuery.trim()) return;

    setResearchLoading(true);
    setResearchError(null);
    setResearchResponse(null);
    setIsExpanded(false);

    try {
      const response = await fetch('/api/research/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: researchQuery,
          context_size: 'medium',
          max_reasoning_steps: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || data.error || 'Failed to process research query'
        );
      }

      setResearchResponse(data);
    } catch (err) {
      setResearchError(
        err instanceof Error ? err.message : 'Unknown error occurred'
      );
    } finally {
      setResearchLoading(false);
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const getDomainFromUrl = (url: string) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Search className="h-5 w-5 text-blue-500" />
          <span>Research Agent Query</span>
        </CardTitle>
        <CardDescription>
          Submit research queries with advanced AI-powered validation and web
          search capabilities
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="research-query" className="text-sm font-medium">
            Research Query
          </label>
          <Textarea
            id="research-query"
            placeholder="Enter your research question here..."
            value={researchQuery}
            onChange={(e) => setResearchQuery(e.target.value)}
            className="min-h-[100px]"
          />
        </div>

        <Button
          onClick={handleResearchQuery}
          disabled={researchLoading || !researchQuery.trim()}
          className="w-full"
        >
          {researchLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Processing Research...
            </>
          ) : (
            <>
              <Search className="h-4 w-4 mr-2" />
              Submit Research Query
            </>
          )}
        </Button>

        {researchError && (
          <Alert className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-red-800 dark:text-red-200">
              {researchError}
            </AlertDescription>
          </Alert>
        )}

        {researchResponse && (
          <div className="space-y-4">
            <Separator />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Research Results</h3>
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{researchResponse.processing_time.toFixed(2)}s</span>
                  </div>
                  <Badge
                    variant={
                      researchResponse.safety_check_passed
                        ? 'default'
                        : 'destructive'
                    }
                  >
                    {researchResponse.safety_check_passed ? 'Safe' : 'Unsafe'}
                  </Badge>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
                <h4 className="font-medium mb-2">Query:</h4>
                <p className="text-sm text-muted-foreground">
                  {researchResponse.query}
                </p>
              </div>

              <div className="w-full">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Answer:</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="h-8 px-2 text-xs"
                  >
                    {isExpanded ? (
                      <>
                        <ChevronUp className="h-3 w-3 mr-1" />
                        Read Less
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-3 w-3 mr-1" />
                        Read More
                      </>
                    )}
                  </Button>
                </div>
                <div className="border rounded-lg bg-slate-50 dark:bg-slate-800 w-full overflow-hidden relative">
                  <div
                    className={`p-4 overflow-y-auto scrollable transition-all duration-300 ${
                      isExpanded ? 'max-h-[70vh]' : 'max-h-80'
                    }`}
                    style={{
                      scrollbarWidth: 'thin',
                      scrollbarColor: '#94a3b8 transparent',
                    }}
                  >
                    <div className="prose max-w-none w-full">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          a: ({ href, children, ...props }) => (
                            <a
                              href={href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline break-words"
                              {...props}
                            >
                              {children}
                            </a>
                          ),
                          h1: ({ children, ...props }) => (
                            <h1
                              className="text-xl font-bold mb-3 mt-4 break-words"
                              {...props}
                            >
                              {children}
                            </h1>
                          ),
                          h2: ({ children, ...props }) => (
                            <h2
                              className="text-lg font-semibold mb-2 mt-3 break-words"
                              {...props}
                            >
                              {children}
                            </h2>
                          ),
                          h3: ({ children, ...props }) => (
                            <h3
                              className="text-base font-medium mb-2 mt-2 break-words"
                              {...props}
                            >
                              {children}
                            </h3>
                          ),
                          ul: ({ children, ...props }) => (
                            <ul
                              className="list-disc list-inside mb-3 space-y-1"
                              {...props}
                            >
                              {children}
                            </ul>
                          ),
                          ol: ({ children, ...props }) => (
                            <ol
                              className="list-decimal list-inside mb-3 space-y-1"
                              {...props}
                            >
                              {children}
                            </ol>
                          ),
                          li: ({ children, ...props }) => (
                            <li className="text-sm break-words" {...props}>
                              {children}
                            </li>
                          ),
                          p: ({ children, ...props }) => (
                            <p
                              className="mb-2 text-sm leading-relaxed break-words"
                              {...props}
                            >
                              {children}
                            </p>
                          ),
                          hr: ({ ...props }) => (
                            <hr
                              className="my-4 border-gray-300 dark:border-gray-600 w-full"
                              {...props}
                            />
                          ),
                        }}
                      >
                        {researchResponse.answer}
                      </ReactMarkdown>
                    </div>
                  </div>
                  {!isExpanded && (
                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-slate-50 to-transparent dark:from-slate-800 dark:to-transparent pointer-events-none rounded-b-lg" />
                  )}
                </div>
              </div>

              {/* Citations */}
              {researchResponse.citations &&
                researchResponse.citations.length > 0 && (
                  <div className="mt-6 w-full">
                    <h4 className="font-medium mb-3 flex items-center space-x-2">
                      <FileText className="h-4 w-4" />
                      <span>
                        Citations ({researchResponse.citations.length})
                      </span>
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 w-full">
                      {researchResponse.citations.map((citation, idx) => (
                        <div
                          key={idx}
                          className="border rounded-lg p-3 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors w-full overflow-hidden"
                        >
                          <div className="flex items-start space-x-3 w-full">
                            <Badge
                              variant="outline"
                              className="flex-shrink-0 mt-0.5"
                            >
                              #{idx + 1}
                            </Badge>
                            <div className="flex-1 min-w-0 overflow-hidden">
                              <a
                                href={citation.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium flex items-center space-x-1 group w-full"
                              >
                                <span className="truncate flex-1">
                                  {citation.title ||
                                    getDomainFromUrl(citation.url)}
                                </span>
                                <ExternalLink className="h-3 w-3 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                              </a>
                              <p className="text-xs text-muted-foreground mt-1 truncate">
                                {getDomainFromUrl(citation.url)}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* Reasoning Steps */}
              {researchResponse.reasoning_steps &&
                researchResponse.reasoning_steps.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Reasoning Steps:</h4>
                    <div className="space-y-3">
                      {researchResponse.reasoning_steps.map((step, idx) => (
                        <div
                          key={idx}
                          className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-800"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline">
                                Step {step.step_number}
                              </Badge>
                              <span className="text-sm font-medium capitalize">
                                {step.action.replace(/_/g, ' ')}
                              </span>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {formatDate(step.timestamp)}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {step.description}
                          </p>
                          {step.query && (
                            <div className="text-xs text-muted-foreground mb-2">
                              <strong>Query:</strong> {step.query}
                            </div>
                          )}
                          {step.result && (
                            <div className="text-xs bg-white dark:bg-slate-700 rounded p-2 border">
                              <strong>Result:</strong>{' '}
                              {step.result.length > 200
                                ? `${step.result.substring(0, 200)}...`
                                : step.result}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* Timestamp */}
              {researchResponse.timestamp && (
                <div className="text-xs text-muted-foreground pt-2 border-t">
                  <strong>Completed:</strong>{' '}
                  {formatDate(researchResponse.timestamp)}
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
