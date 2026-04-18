'use client';

import { useEffect, useState } from 'react';
import { AnalysisResponse } from '@/app/page';

interface RiskMeterCardProps {
  riskData: AnalysisResponse['risk'];
  className?: string;
}

export function RiskMeterCard({ riskData, className = '' }: RiskMeterCardProps) {
  const [animatedConfidence, setAnimatedConfidence] = useState(0);

  useEffect(() => {
    // Animate the confidence value on load
    const timer = setTimeout(() => {
      setAnimatedConfidence(riskData.confidence);
    }, 200);
    return () => clearTimeout(timer);
  }, [riskData.confidence]);

  const getRiskColor = () => {
    switch (riskData.level) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#a0aac0';
    }
  };

  const getRiskLabel = () => {
    switch (riskData.level) {
      case 'high':
        return 'High Risk';
      case 'medium':
        return 'Medium Risk';
      case 'low':
        return 'Low Risk';
      default:
        return 'Unknown';
    }
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (animatedConfidence * circumference);
  const riskColor = getRiskColor();

  return (
    <div className={`group flex flex-col items-center rounded-lg border border-border bg-gradient-to-br from-secondary/40 to-secondary/20 p-6 backdrop-blur-sm transition-all duration-300 hover:border-accent/50 hover:shadow-lg hover:shadow-accent/10 hover-lift ${className}`}>
      <h3 className="mb-6 font-semibold text-white group-hover:text-accent transition-colors duration-300">Risk Assessment</h3>

      {/* Circular Gauge */}
      <div className="relative mb-6 h-40 w-40 group-hover:animate-pulse-slow">
        <svg className="h-full w-full" viewBox="0 0 120 120">
          {/* Background circle */}
          <circle
            cx="60"
            cy="60"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-border"
          />
          {/* Progress circle */}
          <circle
            cx="60"
            cy="60"
            r="45"
            fill="none"
            stroke={riskColor}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            transform="rotate(-90 60 60)"
          />
        </svg>
        {/* Confidence percentage in center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-white">
            {Math.round(animatedConfidence * 100)}%
          </span>
          <span className="text-xs text-muted-foreground">Confidence</span>
        </div>
      </div>

      {/* Risk Description */}
      <div className="w-full space-y-3 text-center">
        <p className="text-sm font-semibold text-white group-hover:text-accent transition-colors duration-300">{getRiskLabel()}</p>
        <p className="text-xs leading-relaxed text-muted-foreground group-hover:text-foreground/80 transition-colors duration-300">{riskData.description}</p>
        <div className="pt-2">
          <span
            className="inline-block rounded-full px-3 py-1 text-xs font-medium transition-all duration-300 hover:scale-105"
            style={{
              backgroundColor: riskColor + '20',
              color: riskColor,
            }}
          >
            {riskData.method === 'classifier' ? 'Trained Classifier' : 'Similarity Fallback'}
          </span>
        </div>
      </div>
    </div>
  );
}
