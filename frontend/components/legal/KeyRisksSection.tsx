'use client';

import { AlertCircle } from 'lucide-react';

interface KeyRisksSectionProps {
  risks: string[];
}

export default function KeyRisksSection({ risks }: KeyRisksSectionProps) {
  if (risks.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-foreground">Key Risks Identified</h3>
      <ul className="space-y-2">
        {risks.map((risk, idx) => (
          <li key={idx} className="flex gap-2 text-sm text-muted-foreground">
            <AlertCircle className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
            <span>{risk}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
