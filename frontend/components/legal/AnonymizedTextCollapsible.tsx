'use client';

import { Card } from '@/components/ui/card';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { ChevronDown, Eye } from 'lucide-react';
import { useState } from 'react';

interface AnonymizedTextCollapsibleProps {
  text: string;
}

export default function AnonymizedTextCollapsible({ text }: AnonymizedTextCollapsibleProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className="bg-card border-border">
        <CollapsibleTrigger className="w-full p-4 hover:bg-card/80 transition-colors flex items-center justify-between group">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-primary" />
            <span className="font-semibold text-foreground">Anonymized Document</span>
          </div>
          <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="px-4 pb-4 border-t border-border pt-4">
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap font-mono text-xs max-h-64 overflow-y-auto bg-background/50 p-3 rounded">
              {text}
            </p>
          </div>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
