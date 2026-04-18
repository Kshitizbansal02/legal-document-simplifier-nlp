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
      <DialogContent className="animate-fadeInUp border-border bg-gradient-to-br from-card to-secondary/30 backdrop-blur-md shadow-2xl shadow-accent/10">
        <DialogHeader className="border-b border-border/50 pb-4">
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-2xl bg-gradient-to-r from-white to-accent bg-clip-text text-transparent">{clause.clause_type}</DialogTitle>
              <p className="mt-2 text-sm text-muted-foreground">
                {Math.round(clause.score * 100)}% similarity match
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-accent hover:bg-secondary/50 transition-all duration-300 p-2 rounded-lg hover:scale-110 active:scale-95"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </DialogHeader>

        <div className="space-y-5 py-4">
          {/* Full Clause Text */}
          <div>
            <h3 className="mb-3 text-sm font-semibold text-white">Full Clause Text</h3>
            <p className="rounded-lg bg-gradient-to-br from-secondary/40 to-secondary/20 p-4 text-sm leading-relaxed text-white/90 backdrop-blur-sm border border-border/30 hover:border-accent/30 transition-colors duration-300">
              {clause.clause_text}
            </p>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg bg-secondary/30 p-4 backdrop-blur-sm border border-border/30 hover:border-accent/30 transition-colors duration-300">
              <p className="text-xs text-muted-foreground font-medium">Risk Level</p>
              <p className={`mt-2 font-bold text-lg capitalize ${getRiskColor(clause.risk_level)}`}>
                {clause.risk_level}
              </p>
            </div>
            <div className="rounded-lg bg-secondary/30 p-4 backdrop-blur-sm border border-border/30 hover:border-accent/30 transition-colors duration-300">
              <p className="text-xs text-muted-foreground font-medium">Similarity Score</p>
              <p className="mt-2 font-bold text-lg text-accent">{Math.round(clause.score * 100)}%</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
