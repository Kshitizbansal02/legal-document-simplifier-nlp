'use client';

import { useState } from 'react';
import { AnalysisResult } from '@/lib/types';
import { analyzeText, analyzeFile } from '@/lib/api';
import TextInputSection from './TextInputSection';
import FileUploadSection from './FileUploadSection';
import ResultsPanel from './ResultsPanel';

export default function LegalAnalyzer() {
  const [textInput, setTextInput] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');

  const handleAnalyzeText = async () => {
    if (!textInput.trim() || textInput.length < 100) {
      setError('Please enter at least 100 characters');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const analysisResult = await analyzeText(textInput);
      setResult(analysisResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze document';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const analysisResult = await analyzeFile(file);
      setResult(analysisResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze file';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-serif font-bold text-primary">Legal Document Analyzer</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Analyze contracts and legal documents for risks and compliance
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
          <div className="lg:col-span-1 flex flex-col gap-4">
            <div className="flex gap-2 bg-card border border-border rounded-lg p-1">
              <button
                onClick={() => { setActiveTab('text'); setError(null); }}
                className={`flex-1 px-3 py-2 rounded transition-colors text-sm font-medium ${
                  activeTab === 'text'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Paste Text
              </button>
              <button
                onClick={() => { setActiveTab('file'); setError(null); }}
                className={`flex-1 px-3 py-2 rounded transition-colors text-sm font-medium ${
                  activeTab === 'file'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Upload File
              </button>
            </div>

            <div className="flex-1 flex flex-col">
              {activeTab === 'text' ? (
                <TextInputSection
                  value={textInput}
                  onChange={setTextInput}
                  onAnalyze={handleAnalyzeText}
                  isLoading={isLoading}
                />
              ) : (
                <FileUploadSection onFileSelect={handleFileSelect} isLoading={isLoading} />
              )}
            </div>

            {error && (
              <div className="bg-red-900/20 border border-red-600 rounded-lg p-3 text-sm text-red-400">
                {error}
              </div>
            )}
          </div>

          <div className="lg:col-span-2 flex flex-col">
            {result ? (
              <ResultsPanel result={result} />
            ) : (
              <div className="flex items-center justify-center h-full border border-border rounded-lg bg-card/30">
                <div className="text-center text-muted-foreground">
                  <p className="text-lg font-medium mb-1">No analysis yet</p>
                  <p className="text-sm">
                    {activeTab === 'text'
                      ? 'Paste a document and click analyze to get started'
                      : 'Upload a document to begin analysis'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}