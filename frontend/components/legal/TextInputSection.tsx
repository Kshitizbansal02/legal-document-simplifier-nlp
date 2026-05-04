'use client';

import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface TextInputSectionProps {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  placeholder?: string;
}

export default function TextInputSection({
  value,
  onChange,
  onAnalyze,
  isLoading,
  placeholder = 'Paste your legal document here...',
}: TextInputSectionProps) {
  const charCount = value.length;
  const isValidLength = charCount >= 100;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">Paste Document Text</label>
        <span className="text-xs text-muted-foreground">
          {charCount} characters {charCount < 100 && '(minimum 100 required)'}
        </span>
      </div>
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="min-h-48 resize-none bg-card border-border text-foreground placeholder:text-muted-foreground focus:ring-primary focus:ring-offset-0"
      />
      <Button
        onClick={onAnalyze}
        disabled={!isValidLength || isLoading}
        className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-2 h-auto"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Analyzing...
          </>
        ) : (
          'Analyze Document'
        )}
      </Button>
    </div>
  );
}
