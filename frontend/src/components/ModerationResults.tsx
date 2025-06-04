import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Clock } from 'lucide-react';
import { ModerationResponse } from '@/types/agents';

interface ModerationResultsProps {
  response: ModerationResponse;
}

export function ModerationResults({ response }: ModerationResultsProps) {
  return (
    <div className="space-y-4">
      <Separator />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Moderation Results</h3>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Clock className="h-3 w-3" />
              <span>{response.processing_time.toFixed(2)}s</span>
            </div>
            <Badge variant={response.is_safe ? 'default' : 'destructive'}>
              {response.is_safe ? 'Safe' : 'Unsafe'}
            </Badge>
            <Badge variant="outline">{response.overall_risk_level}</Badge>
          </div>
        </div>

        {/* Content Types Analyzed */}
        {response.content_types_analyzed.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Content Types Analyzed:</h4>
            <div className="flex flex-wrap gap-2">
              {response.content_types_analyzed.map((type, idx) => (
                <Badge key={idx} variant="secondary">
                  {type}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        <div>
          <h4 className="font-medium mb-2">Summary:</h4>
          <p className="text-sm bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
            {response.summary}
          </p>
        </div>

        {/* Rationale */}
        <div>
          <h4 className="font-medium mb-2">Rationale:</h4>
          <p className="text-sm bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
            {response.rationale}
          </p>
        </div>

        {/* Image Analysis Results */}
        {response.image_analysis && (
          <div>
            <h4 className="font-medium mb-2">Image Analysis:</h4>
            <div className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-800 space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center justify-between">
                  <span>NSFW Content:</span>
                  <Badge
                    variant={
                      response.image_analysis.has_nsfw
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.image_analysis.has_nsfw
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Violence:</span>
                  <Badge
                    variant={
                      response.image_analysis.has_violence
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.image_analysis.has_violence
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Hate Symbols:</span>
                  <Badge
                    variant={
                      response.image_analysis.has_hate_symbols
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.image_analysis.has_hate_symbols
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
              </div>

              {response.image_analysis.extracted_text && (
                <div>
                  <span className="text-sm font-medium">Extracted Text:</span>
                  <p className="text-sm text-muted-foreground bg-white dark:bg-slate-700 rounded p-2 mt-1">
                    {response.image_analysis.extracted_text}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Text Analysis Results */}
        {response.text_analysis && (
          <div>
            <h4 className="font-medium mb-2">Text Analysis:</h4>
            <div className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-800 space-y-3">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="flex items-center justify-between">
                  <span>Toxicity:</span>
                  <Badge
                    variant={
                      response.text_analysis.has_toxicity
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.text_analysis.has_toxicity
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Hate Speech:</span>
                  <Badge
                    variant={
                      response.text_analysis.has_hate_speech
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.text_analysis.has_hate_speech
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Harassment:</span>
                  <Badge
                    variant={
                      response.text_analysis.has_harassment
                        ? 'destructive'
                        : 'default'
                    }
                  >
                    {response.text_analysis.has_harassment
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>PII:</span>
                  <Badge
                    variant={
                      response.text_analysis.has_pii ? 'destructive' : 'default'
                    }
                  >
                    {response.text_analysis.has_pii
                      ? 'Detected'
                      : 'Not Detected'}
                  </Badge>
                </div>
              </div>

              {response.text_analysis.detected_pii.length > 0 && (
                <div>
                  <span className="text-sm font-medium">
                    PII Types Detected:
                  </span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {response.text_analysis.detected_pii.map((pii, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {pii}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Violation Categories */}
        {response.violation_categories.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Violation Categories:</h4>
            <div className="flex flex-wrap gap-2">
              {response.violation_categories.map((category, idx) => (
                <Badge key={idx} variant="destructive">
                  {category}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Violations */}
        {response.violations_found && response.violations_found.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Detailed Analysis:</h4>
            <div className="space-y-2">
              {response.violations_found.map((violation, idx) => (
                <div
                  key={idx}
                  className="border rounded-lg p-3 bg-slate-50 dark:bg-slate-800"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium capitalize">
                      {violation.category}
                    </span>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant={violation.detected ? 'destructive' : 'default'}
                      >
                        {violation.detected ? 'Detected' : 'Not Detected'}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {(violation.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {violation.description}
                  </p>
                  {violation.evidence && violation.evidence.length > 0 && (
                    <div className="mt-2">
                      <span className="text-xs font-medium">Evidence:</span>
                      <ul className="text-xs text-muted-foreground mt-1 list-disc list-inside">
                        {violation.evidence.map((evidence, evidenceIdx) => (
                          <li key={evidenceIdx}>{evidence}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
