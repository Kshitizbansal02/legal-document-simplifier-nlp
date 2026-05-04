'use client';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AnalysisResult } from '@/lib/types';
import RiskBadge from './RiskBadge';
import SimilarClausesSection from './SimilarClausesSection';
import AnonymizedTextCollapsible from './AnonymizedTextCollapsible';

interface ResultsPanelProps {
  result: AnalysisResult;
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  return (
    <Card className="bg-card border-border h-full">
      <ScrollArea className="h-full">
        <div className="p-6 space-y-6">

          {/* Risk Badge */}
          <div>
            <h2 className="text-xl font-serif font-bold text-foreground mb-4">Analysis Results</h2>
            <RiskBadge
              riskLevel={result.risk.level}
              percentage={Math.round(result.risk.confidence * 100)}
            />
          </div>

          {/* Simplified Explanation */}
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Plain English
            </h3>
            <p className="text-foreground leading-relaxed">{result.simplified}</p>
          </div>

          {/* Risk Explanation */}
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              Why This Is Risky
            </h3>
            <p className="text-foreground leading-relaxed">{result.risk_explanation}</p>
            <p className="text-xs text-muted-foreground mt-2">
              Confidence: {Math.round(result.risk.confidence * 100)}% · Method: {result.risk.method}
            </p>
          </div>

          {/* Extraction Meta (file uploads only) */}
          {result.extraction_meta && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                File Info
              </h3>
              <p className="text-xs text-muted-foreground">
                {result.extraction_meta.filename} · {result.extraction_meta.characters_extracted} characters extracted · {result.extraction_meta.extraction_method}
              </p>
            </div>
          )}

          {/* Similar Clauses */}
          <div className="divide-y divide-border">
            <div className="pt-2">
              <SimilarClausesSection clauses={result.similar_clauses} />
            </div>
            <div className="pt-4">
              <AnonymizedTextCollapsible text={result.anonymized_text} />
            </div>
          </div>

        </div>
      </ScrollArea>
    </Card>
  );
}