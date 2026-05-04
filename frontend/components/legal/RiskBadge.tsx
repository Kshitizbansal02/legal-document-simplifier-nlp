'use client';

import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

interface RiskBadgeProps {
  riskLevel: 'low' | 'medium' | 'high';
  percentage?: number;
}

export default function RiskBadge({ riskLevel, percentage }: RiskBadgeProps) {
  const colors = {
    low: 'bg-emerald-900/20 border-emerald-600 text-emerald-400',
    medium: 'bg-amber-900/20 border-amber-600 text-amber-400',
    high: 'bg-red-900/20 border-red-600 text-red-400',
  };

  const icons = {
    low: CheckCircle,
    medium: AlertTriangle,
    high: AlertCircle,
  };

  const Icon = icons[riskLevel];
  const labels = {
    low: 'Low Risk',
    medium: 'Medium Risk',
    high: 'High Risk',
  };

  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${colors[riskLevel]}`}>
      <Icon className="w-5 h-5" />
      <div className="flex flex-col">
        <span className="font-semibold text-sm">{labels[riskLevel]}</span>
        {percentage !== undefined && (
          <span className="text-xs opacity-75">{percentage}% Risk Score</span>
        )}
      </div>
    </div>
  );
}
