'use client';

import { useState } from 'react';
import { SimilarClauseCard } from './similar-clause-card';
import { ClauseModal } from './clause-modal';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface SimilarClause {
  clause_text: string;
  clause_type: string;
  risk_level: string;
  score: number;
}

interface SimilarClausesSectionProps {
  clauses: SimilarClause[];
}

export function SimilarClausesSection({ clauses }: SimilarClausesSectionProps) {
  const [selectedClause, setSelectedClause] = useState<SimilarClause | null>(null);
  const [scrollPosition, setScrollPosition] = useState(0);

  const handleScroll = (direction: 'left' | 'right') => {
    const container = document.getElementById('clauses-scroll');
    if (container) {
      const scrollAmount = 320;
      const newPosition =
        direction === 'left'
          ? Math.max(0, scrollPosition - scrollAmount)
          : scrollPosition + scrollAmount;
      container.scrollLeft = newPosition;
      setScrollPosition(newPosition);
    }
  };

  if (!clauses || clauses.length === 0) {
    return null;
  }

  return (
    <>
      <div className="mt-8 space-y-4 animate-fadeInUp" style={{ animationDelay: '400ms' }}>
        <h2 className="text-3xl font-bold text-white bg-gradient-to-r from-white via-accent to-white bg-clip-text text-transparent">Similar Clauses Found in Our Database</h2>
        <p className="text-muted-foreground leading-relaxed">
          Below are similar clauses we&apos;ve encountered, with their risk levels and similarity scores.
        </p>

        {/* Scroll Container */}
        <div className="relative">
          <div
            id="clauses-scroll"
            className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide"
            style={{ scrollBehavior: 'smooth' }}
          >
            {clauses.map((clause, index) => (
              <div key={index} className="flex-shrink-0">
                <SimilarClauseCard
                  clause={clause}
                  onClick={() => setSelectedClause(clause)}
                />
              </div>
            ))}
          </div>

          {/* Scroll Buttons */}
          <button
            onClick={() => handleScroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-accent/80 to-accent p-2 text-accent-foreground hover:from-accent hover:to-accent hover:shadow-lg hover:shadow-accent/30 transition-all duration-300 z-10 hover:scale-110 active:scale-95"
            aria-label="Scroll left"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={() => handleScroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-accent to-accent/80 p-2 text-accent-foreground hover:from-accent hover:to-accent hover:shadow-lg hover:shadow-accent/30 transition-all duration-300 z-10 hover:scale-110 active:scale-95"
            aria-label="Scroll right"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Clause Modal */}
      {selectedClause && (
        <ClauseModal clause={selectedClause} onClose={() => setSelectedClause(null)} />
      )}
    </>
  );
}
