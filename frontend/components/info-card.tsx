'use client';

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import React from 'react';

interface InfoCardProps {
  title: string;
  content: string;
  icon: React.ReactNode;
  isMonospace?: boolean;
  tooltip?: string;
  className?: string;
}

export function InfoCard({
  title,
  content,
  icon,
  isMonospace = false,
  tooltip,
  className = '',
}: InfoCardProps) {
  return (
    <div className={`flex flex-col rounded-lg border border-border bg-secondary/30 p-4 ${className}`}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="text-muted-foreground">{icon}</div>
          <h3 className="font-semibold text-white">{title}</h3>
        </div>
        {tooltip && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button className="text-muted-foreground hover:text-accent transition-colors">
                  <HelpCircle className="h-4 w-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent>{tooltip}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
      <p
        className={`flex-1 text-sm leading-relaxed ${
          isMonospace
            ? 'font-mono text-xs text-muted-foreground'
            : 'text-muted-foreground'
        }`}
      >
        {content}
      </p>
    </div>
  );
}
