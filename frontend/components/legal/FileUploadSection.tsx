'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, FileText, Loader2 } from 'lucide-react';

interface FileUploadSectionProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export default function FileUploadSection({ onFileSelect, isLoading }: FileUploadSectionProps) {
  const [fileName, setFileName] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">Upload Document</label>
      <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary hover:bg-card/50 transition-all cursor-pointer">
        <input
          type="file"
          id="file-upload"
          onChange={handleFileChange}
          accept=".txt,.pdf,.doc,.docx"
          className="hidden"
          disabled={isLoading}
        />
        <label htmlFor="file-upload" className="cursor-pointer block">
          <div className="flex justify-center mb-3">
            {fileName ? (
              <FileText className="w-8 h-8 text-primary" />
            ) : (
              <Upload className="w-8 h-8 text-muted-foreground" />
            )}
          </div>
          <p className="text-sm font-medium text-foreground mb-1">
            {fileName || 'Click to upload or drag and drop'}
          </p>
          <p className="text-xs text-muted-foreground">
            {fileName ? fileName : 'TXT, PDF, DOC, DOCX up to 10MB'}
          </p>
        </label>
      </div>
    </div>
  );
}
