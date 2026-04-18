'use client';

import { AnalysisResponse } from '@/app/page';
import { RiskMeterCard } from './risk-meter-card';
import { InfoCard } from './info-card';
import { Scale, AlertTriangle, Lock, Info } from 'lucide-react';

interface ResultsSectionProps {
  data: AnalysisResponse;
}

export function ResultsSection({ data }: ResultsSectionProps) {
  const isHighRisk = data.risk.level === 'high';

  return (
    <div
      className={`rounded-xl border transition-all duration-500 animate-fadeInUp shadow-lg ${
        isHighRisk
          ? 'border-destructive/50 bg-destructive/5 shadow-destructive/20'
          : 'border-border bg-card shadow-accent/10 hover:shadow-accent/20'
      }`}
    >
      <div className="grid gap-6 p-6 sm:p-8 lg:grid-cols-[1fr_1fr_1fr_0.8fr]" style={{ animationDelay: '200ms' }}>
        {/* Plain English Card - spans 1 column */}
        <InfoCard
          title="Plain English"
          content={data.simplified}
          icon={<Scale className="h-5 w-5" />}
          className="lg:col-span-1"
        />

        {/* Why This Matters Card - spans 1 column */}
        <InfoCard
          title="Why This Matters"
          content={data.risk_explanation}
          icon={
            data.risk.level === 'high' ? (
              <AlertTriangle className="h-5 w-5 text-destructive" />
            ) : (
              <Info className="h-5 w-5 text-warning" />
            )
          }
          className="lg:col-span-1"
        />

        {/* Privacy Shield Card - spans 1 column */}
        <InfoCard
          title="Privacy Shield"
          content={data.anonymized_text}
          icon={<Lock className="h-5 w-5 text-accent" />}
          isMonospace
          tooltip="Your data was anonymized before being sent to AI"
          className="lg:col-span-1"
        />

        {/* Risk Meter Card - spans 1 column */}
        <RiskMeterCard riskData={data.risk} className="lg:col-span-1 lg:row-span-1" />
      </div>
    </div>
  );
}
