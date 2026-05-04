'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

const SAMPLE_CLAUSES = {
  'Anti-Assignment': `Neither party may assign, delegate or transfer any rights or obligations under this Agreement 
without the prior written consent of the other party. Any attempted assignment without such consent 
shall be void. This restriction shall not apply to assignments to affiliates or pursuant to a 
change of control.`,
  'Governing Law': `This Agreement shall be governed by and construed in accordance with the laws of the State of 
Delaware, without regard to its conflict of law provisions. The parties agree to submit to the 
exclusive jurisdiction of the state and federal courts located in Wilmington, Delaware.`,
  'Exclusivity': `During the term of this Agreement and for a period of two (2) years thereafter, neither party shall, 
directly or indirectly, engage in any business that competes with the services provided under this 
Agreement within a 50-mile radius of the other party's principal place of business.`,
};

interface InputSectionProps {
  onAnalyze: (text: string) => Promise<void>;
  isLoading: boolean;
}

export function InputSection({ onAnalyze, isLoading }: InputSectionProps) {
  const [text, setText] = useState('');
  const [wordCount, setWordCount] = useState(0);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setText(value);
    const count = value.trim() ? value.trim().split(/\s+/).length : 0;
    setWordCount(count);
  };

  const handleSampleClick = (clauseKey: keyof typeof SAMPLE_CLAUSES) => {
    const clauseText = SAMPLE_CLAUSES[clauseKey];
    setText(clauseText);
    const count = clauseText.trim().split(/\s+/).length;
    setWordCount(count);
  };

  const handleAnalyze = () => {
    if (text.trim()) {
      onAnalyze(text);
    }
  };

  return (
    <div className="space-y-6 rounded-xl border border-border bg-card p-6 sm:p-8">
      {/* Textarea */}
      <div className="relative">
        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Paste your legal clause here…"
          className="w-full min-h-48 rounded-lg border border-border bg-input px-4 py-3 text-white placeholder:text-muted-foreground outline-none transition-all duration-200 focus:border-accent focus:ring-2 focus:ring-accent/30"
        />
        <div className="absolute bottom-3 right-3 text-sm text-muted-foreground">
          {wordCount} words
        </div>
      </div>

      {/* Sample Buttons */}
      <div className="grid gap-2 sm:grid-cols-3">
        {Object.entries(SAMPLE_CLAUSES).map(([key]) => (
          <Button
            key={key}
            onClick={() => handleSampleClick(key as keyof typeof SAMPLE_CLAUSES)}
            variant="outline"
            className="border-border hover:bg-secondary/50"
          >
            {key}
          </Button>
        ))}
      </div>

      {/* Analyze Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleAnalyze}
          disabled={!text.trim() || isLoading}
          size="lg"
          className="min-w-48 bg-accent text-accent-foreground hover:bg-accent/90 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Analyzing…
            </>
          ) : (
            'Analyze Clause'
          )}
        </Button>
      </div>
    </div>
  );
}
