export interface RiskResult {
  level: 'low' | 'medium' | 'high';
  confidence: number;
  description: string;
  method: string;
}

export interface SimilarClause {
  clause_text: string;
  clause_type: string;
  risk_level: string;
  score: number;
}

export interface ExtractionMeta {
  filename: string;
  file_type: string;
  characters_extracted: number;
  extraction_method: string;
}

export interface AnalysisResult {
  anonymized_text: string;
  simplified: string;
  risk_explanation: string;
  risk: RiskResult;
  similar_clauses: SimilarClause[];
  extraction_meta?: ExtractionMeta;
}