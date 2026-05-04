'use client';

import { Card } from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';

interface SimplifiedExplanationProps {
  summary: string;
}

export default function SimplifiedExplanation({ summary }: SimplifiedExplanationProps) {
  return (
    <Card className="bg-card border-border p-4">
      <div className="flex gap-3">
        <Lightbulb className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-foreground mb-2">Key Takeaway</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{summary}</p>
        </div>
      </div>
    </Card>
  );
}
