import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer } from
'recharts';
import { Keyword } from '../../types';
import { Skeleton } from '../ui/Skeleton';
interface KeywordChartProps {
  keywords?: Keyword[];
  isLoading?: boolean;
}
export function KeywordChart({ keywords, isLoading }: KeywordChartProps) {
  if (isLoading) {
    return <Skeleton className="w-full h-[300px] rounded-2xl" />;
  }
  if (!keywords || keywords.length === 0) return null;
  const data = keywords.
  map((k) => ({
    name: k.term,
    score: Math.round(k.score * 100)
  })).
  sort((a, b) => b.score - a.score).
  slice(0, 10);
  return (
    <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-bold text-slate-900 mb-6">
        Top Keywords by Relevance
      </h3>
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{
              top: 5,
              right: 30,
              left: 40,
              bottom: 5
            }}>
            
            <CartesianGrid
              strokeDasharray="3 3"
              horizontal={true}
              vertical={false}
              stroke="#f1f5f9" />
            
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis
              dataKey="name"
              type="category"
              axisLine={false}
              tickLine={false}
              tick={{
                fill: '#475569',
                fontSize: 12
              }}
              width={120} />
            
            <Tooltip
              cursor={{
                fill: '#f8fafc'
              }}
              contentStyle={{
                borderRadius: '12px',
                border: 'none',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
              formatter={(value: number) => [`${value}%`, 'Relevance']} />
            
            <Bar
              dataKey="score"
              fill="#3b82f6"
              radius={[0, 4, 4, 0]}
              barSize={24} />
            
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>);

}