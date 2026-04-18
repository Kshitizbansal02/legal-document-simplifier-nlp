'use client';

import { useState } from 'react';
import { InputSection } from '@/components/input-section';
import { ResultsSection } from '@/components/results-section';
import { SimilarClausesSection } from '@/components/similar-clauses-section';

export interface AnalysisResponse {
  anonymized_text: string;
  simplified: string;
  risk_explanation: string;
  risk: {
    level: 'low' | 'medium' | 'high';
    confidence: number;
    description: string;
    method: string;
  };
  similar_clauses: Array<{
    clause_text: string;
    clause_type: string;
    risk_level: string;
    score: number;
  }>;
}

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (text: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze clause');
      }

      const data = await response.json();
      setAnalysisResult(data);
      
      // Smooth scroll to results
      setTimeout(() => {
        const resultsElement = document.getElementById('results-section');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-20 right-40 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-40 left-20 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
      </div>

      <main className="relative mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8 z-10">
        {/* Header */}
        <div className="mb-12 animate-slideInDown">
          <h1 className="text-5xl font-bold text-white sm:text-6xl bg-gradient-to-r from-white via-accent to-white bg-clip-text text-transparent">
            Legal Clause Analyzer
          </h1>
          <p className="mt-4 text-xl text-muted-foreground">Understand, simplify, and analyze legal contracts with AI</p>
        </div>

        {/* Input Section */}
        <InputSection onAnalyze={handleAnalyze} isLoading={loading} />

        {/* Error Message */}
        {error && (
          <div className="mt-6 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-destructive animate-fadeInUp">
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {analysisResult && (
          <div id="results-section" className="mt-12 animate-fadeInUp space-y-8">
            <ResultsSection data={analysisResult} />
            <SimilarClausesSection clauses={analysisResult.similar_clauses} />
          </div>
        )}
      </main>
    </div>
  );
}
