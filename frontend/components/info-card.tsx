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
    <div className={`group flex flex-col rounded-lg border border-border bg-gradient-to-br from-secondary/40 to-secondary/20 p-5 backdrop-blur-sm transition-all duration-300 hover:border-accent/50 hover:shadow-lg hover:shadow-accent/10 hover-lift ${className}`}>
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-accent/10 group-hover:bg-accent/20 transition-colors duration-300 text-accent">
            {icon}
          </div>
          <h3 className="font-semibold text-white group-hover:text-accent transition-colors duration-300">{title}</h3>
        </div>
        {tooltip && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button className="text-muted-foreground hover:text-accent transition-colors duration-300">
                  <HelpCircle className="h-4 w-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent>{tooltip}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
      <p
        className={`flex-1 text-sm leading-relaxed transition-colors duration-300 ${
          isMonospace
            ? 'font-mono text-xs text-muted-foreground group-hover:text-foreground/80'
            : 'text-muted-foreground group-hover:text-foreground/90'
        }`}
      >
        {content}
      </p>
    </div>
  );
}
