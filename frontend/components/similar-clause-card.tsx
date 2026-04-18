'use client';

import { Progress } from '@/components/ui/progress';

interface SimilarClause {
  clause_text: string;
  clause_type: string;
  risk_level: string;
  score: number;
}

interface SimilarClauseCardProps {
  clause: SimilarClause;
  onClick: () => void;
}

export function SimilarClauseCard({ clause, onClick }: SimilarClauseCardProps) {
  const getTypeColor = (type: string) => {
    const normalized = type.toLowerCase().replace(/\s+/g, '-');
    switch (normalized) {
      case 'anti-assignment':
        return { bg: 'bg-purple-500/20', text: 'text-purple-400', label: 'Purple' };
      case 'license-grant':
        return { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Blue' };
      case 'exclusivity':
        return { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'Orange' };
      default:
        return { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Gray' };
    }
  };

  const getRiskColor = (level: string) => {
    const normalized = level.toLowerCase();
    switch (normalized) {
      case 'high':
        return { dot: 'bg-red-500', text: 'text-red-400' };
      case 'medium':
        return { dot: 'bg-yellow-500', text: 'text-yellow-400' };
      case 'low':
        return { dot: 'bg-green-500', text: 'text-green-400' };
      default:
        return { dot: 'bg-gray-500', text: 'text-gray-400' };
    }
  };

  const typeColor = getTypeColor(clause.clause_type);
  const riskColor = getRiskColor(clause.risk_level);

  return (
    <button
      onClick={onClick}
      className="group w-80 rounded-lg border border-border bg-gradient-to-br from-secondary/40 to-secondary/20 p-4 text-left transition-all duration-300 hover:border-accent hover:shadow-lg hover:shadow-accent/30 hover-lift backdrop-blur-sm active:scale-95 cursor-pointer"
    >
      {/* Clause Type Badge */}
      <div className="mb-3 inline-block">
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium transition-all duration-300 ${typeColor.bg} ${typeColor.text} group-hover:scale-110 group-hover:shadow-lg`}>
          {clause.clause_type}
        </span>
      </div>

      {/* Clause Text Preview */}
      <p className="mb-4 line-clamp-3 text-sm text-white leading-relaxed group-hover:text-white/95 transition-colors duration-300">
        {clause.clause_text}
      </p>

      {/* Similarity Score Bar */}
      <div className="mb-4 space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground group-hover:text-muted-foreground/80 transition-colors">Similarity</span>
          <span className="text-xs font-semibold text-accent group-hover:text-white transition-colors duration-300">{Math.round(clause.score * 100)}%</span>
        </div>
        <Progress value={clause.score * 100} className="h-2 group-hover:shadow-accent/30 transition-all" />
      </div>

      {/* Risk Level Badge */}
      <div className="flex items-center gap-2">
        <div className={`h-2 w-2 rounded-full ${riskColor.dot} group-hover:animate-pulse`} />
        <span className={`text-xs font-medium ${riskColor.text} group-hover:font-semibold transition-all`}>{clause.risk_level}</span>
      </div>
    </button>
  );
}
