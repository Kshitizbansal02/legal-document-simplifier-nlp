'use client';

import { CheckCircle } from 'lucide-react';

interface RecommendedActionsSectionProps {
  actions: string[];
}

export default function RecommendedActionsSection({ actions }: RecommendedActionsSectionProps) {
  if (actions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-foreground">Recommended Actions</h3>
      <ul className="space-y-2">
        {actions.map((action, idx) => (
          <li key={idx} className="flex gap-2 text-sm text-muted-foreground">
            <CheckCircle className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
            <span>{action}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
