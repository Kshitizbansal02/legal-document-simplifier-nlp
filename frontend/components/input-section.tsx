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
    <div className="animate-fadeInUp rounded-xl border border-border bg-card p-6 sm:p-8 backdrop-blur-sm space-y-6 hover-lift shadow-lg hover:shadow-2xl transition-all duration-300">
      {/* Textarea */}
      <div className="relative group">
        <label className="block text-sm font-semibold text-white mb-3">Paste Your Legal Clause</label>
        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Paste your legal clause here…"
          className="w-full min-h-48 rounded-lg border border-border bg-input px-4 py-3 text-white placeholder:text-muted-foreground outline-none transition-all duration-300 focus:border-accent focus:ring-2 focus:ring-accent/30 focus:shadow-lg focus:shadow-accent/20"
        />
        <div className="absolute bottom-3 right-3 text-sm text-muted-foreground bg-background/50 px-2 py-1 rounded-md backdrop-blur-sm font-medium">
          {wordCount} words
        </div>
      </div>

      {/* Sample Buttons */}
      <div>
        <label className="block text-sm font-semibold text-white mb-3">Try Sample Clauses</label>
        <div className="grid gap-3 sm:grid-cols-3">
          {Object.entries(SAMPLE_CLAUSES).map(([key], index) => (
            <Button
              key={key}
              onClick={() => handleSampleClick(key as keyof typeof SAMPLE_CLAUSES)}
              variant="outline"
              className="border-border hover:bg-secondary/50 hover:border-accent transition-all duration-300 hover-lift text-white font-medium"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {key}
            </Button>
          ))}
        </div>
      </div>

      {/* Analyze Button */}
      <div className="flex justify-center pt-6">
        <Button
          onClick={handleAnalyze}
          disabled={!text.trim() || isLoading}
          size="lg"
          className="min-w-56 bg-gradient-to-r from-accent to-accent/80 text-accent-foreground hover:from-accent hover:to-accent font-semibold shadow-lg hover:shadow-accent/30 disabled:opacity-50 disabled:shadow-none transition-all duration-300 hover:scale-105"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Analyzing Your Clause…
            </>
          ) : (
            'Analyze Clause'
          )}
        </Button>
      </div>
    </div>
  );
}
