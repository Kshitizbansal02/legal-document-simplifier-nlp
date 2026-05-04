'use client';
import { Card } from '@/components/ui/card';
import { BookOpen } from 'lucide-react';
import { SimilarClause } from '@/lib/types';

interface SimilarClausesSectionProps {
  clauses: SimilarClause[];
}

const riskColors: Record<string, string> = {
  high:    'text-red-400 bg-red-900/20 border-red-600',
  medium:  'text-amber-400 bg-amber-900/20 border-amber-600',
  low:     'text-emerald-400 bg-emerald-900/20 border-emerald-600',
};

export default function SimilarClausesSection({ clauses }: SimilarClausesSectionProps) {
  if (!clauses || clauses.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-foreground">Similar Clauses from Real Contracts</h3>
      <div className="space-y-2">
        {clauses.map((clause, idx) => (
          <Card key={idx} className="bg-card border-border p-3 hover:bg-card/80 transition-colors">
            <div className="flex gap-3">
              <BookOpen className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground mb-2 break-words line-clamp-3">
                  {clause.clause_text}
                </p>
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{clause.clause_type}</span>
                    <span className={`text-xs px-2 py-0.5 rounded border font-medium ${riskColors[clause.risk_level] ?? 'text-muted-foreground'}`}>
                      {clause.risk_level}
                    </span>
                  </div>
                  <span className="text-xs text-primary font-medium">
                    {Math.round(clause.score * 100)}% match
                  </span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}