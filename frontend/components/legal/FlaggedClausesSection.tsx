'use client';

import { Card } from '@/components/ui/card';
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react';
import { FlaggedClause } from '@/lib/types';

interface FlaggedClausesSectionProps {
  clauses: FlaggedClause[];
}

export default function FlaggedClausesSection({ clauses }: FlaggedClausesSectionProps) {
  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'low':
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      default:
        return null;
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'border-red-900/30 bg-red-900/10';
      case 'medium':
        return 'border-amber-900/30 bg-amber-900/10';
      case 'low':
        return 'border-emerald-900/30 bg-emerald-900/10';
      default:
        return '';
    }
  };

  if (clauses.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-foreground">Flagged Clauses</h3>
      <div className="space-y-2">
        {clauses.map((clause, idx) => (
          <Card
            key={idx}
            className={`p-3 border ${getRiskColor(clause.riskLevel)} bg-card`}
          >
            <div className="flex gap-3">
              {getRiskIcon(clause.riskLevel)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground mb-1 break-words">
                  {clause.text}
                </p>
                <p className="text-xs text-muted-foreground">{clause.reason}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
