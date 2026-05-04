'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { X } from 'lucide-react';

interface SimilarClause {
  clause_text: string;
  clause_type: string;
  risk_level: string;
  score: number;
}

interface ClauseModalProps {
  clause: SimilarClause;
  onClose: () => void;
}

export function ClauseModal({ clause, onClose }: ClauseModalProps) {
  const getRiskColor = (level: string) => {
    const normalized = level.toLowerCase();
    switch (normalized) {
      case 'high':
        return 'text-destructive';
      case 'medium':
        return 'text-warning';
      case 'low':
        return 'text-success';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="border-border bg-card">
        <DialogHeader className="border-b border-border pb-4">
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-xl text-white">{clause.clause_type}</DialogTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                {Math.round(clause.score * 100)}% similarity match
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-white transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Full Clause Text */}
          <div>
            <h3 className="mb-2 text-sm font-semibold text-white">Full Clause Text</h3>
            <p className="rounded-lg bg-secondary/30 p-4 text-sm leading-relaxed text-white">
              {clause.clause_text}
            </p>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Risk Level</p>
              <p className={`mt-1 font-semibold capitalize ${getRiskColor(clause.risk_level)}`}>
                {clause.risk_level}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Similarity Score</p>
              <p className="mt-1 font-semibold text-accent">{Math.round(clause.score * 100)}%</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
