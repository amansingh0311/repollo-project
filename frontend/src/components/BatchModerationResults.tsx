import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Clock } from 'lucide-react';
import { BatchModerationResponse } from '@/types/agents';

interface BatchModerationResultsProps {
  response: BatchModerationResponse;
}

export function BatchModerationResults({
  response,
}: BatchModerationResultsProps) {
  return (
    <div className="space-y-4">
      <Separator />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Batch Moderation Results</h3>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Clock className="h-3 w-3" />
              <span>{response.processing_time.toFixed(2)}s</span>
            </div>
            <Badge variant="outline">{response.results.length} items</Badge>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
            <div className="font-medium">Total Items</div>
            <div className="text-2xl font-bold">
              {response.summary_stats.total_items}
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
            <div className="font-medium text-green-800 dark:text-green-200">
              Safe Items
            </div>
            <div className="text-2xl font-bold text-green-600">
              {response.overall_safe_count}
            </div>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
            <div className="font-medium text-red-800 dark:text-red-200">
              Unsafe Items
            </div>
            <div className="text-2xl font-bold text-red-600">
              {response.overall_unsafe_count}
            </div>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
            <div className="font-medium text-blue-800 dark:text-blue-200">
              Processing Time
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {response.processing_time.toFixed(1)}s
            </div>
          </div>
        </div>

        {/* Individual Results */}
        <div>
          <h4 className="font-medium mb-3">Individual Results:</h4>
          <div className="space-y-3">
            {response.results.map((result, idx) => (
              <div
                key={idx}
                className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-800"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Item {idx + 1}</span>
                  <div className="flex items-center space-x-2">
                    <Badge variant={result.is_safe ? 'default' : 'destructive'}>
                      {result.is_safe ? 'Safe' : 'Unsafe'}
                    </Badge>
                    <Badge variant="outline">{result.overall_risk_level}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {result.processing_time.toFixed(2)}s
                    </span>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground mb-2">
                  {result.summary}
                </p>

                {result.content_types_analyzed.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {result.content_types_analyzed.map((type, typeIdx) => (
                      <Badge
                        key={typeIdx}
                        variant="secondary"
                        className="text-xs"
                      >
                        {type}
                      </Badge>
                    ))}
                  </div>
                )}

                {result.violation_categories.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {result.violation_categories.map((category, catIdx) => (
                      <Badge
                        key={catIdx}
                        variant="destructive"
                        className="text-xs"
                      >
                        {category}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
