import React from 'react';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function MetricChart({ data, delay = 0 }) {
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#05020A]/95 backdrop-blur-2xl border border-[#7B61FF]/50 rounded-xl px-4 py-3 shadow-[0_10px_40px_rgba(123,97,255,0.2)]">
          <p className="text-[#3AB0FF] text-[10px] font-mono uppercase tracking-widest mb-3 drop-shadow-[0_0_5px_rgba(58,176,255,0.5)]">
            {label}
          </p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-6 mb-1 last:mb-0">
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full shadow-[0_0_10px_currentColor]"
                  style={{ backgroundColor: entry.color, color: entry.color }}
                />
                <span className="text-xs font-bold font-mono text-white uppercase">
                  {entry.name}
                </span>
              </div>
              <span className="text-sm font-bold text-white font-mono">
                {entry.value.toFixed(1)}
                <span className="text-[#3AB0FF] text-xs">%</span>
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
      className="cyber-panel p-6 h-[320px] flex flex-col relative overflow-hidden group shrink-0"
    >
      <div className="absolute top-0 right-0 w-72 h-72 bg-[#00FFA3]/10 rounded-full blur-[100px] pointer-events-none group-hover:bg-[#00FFA3]/20 transition-colors duration-1000" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-[#7B61FF]/10 rounded-full blur-[100px] pointer-events-none group-hover:bg-[#7B61FF]/20 transition-colors duration-1000" />

      <div className="flex justify-between items-center mb-6 relative z-10">
        <h3 className="text-[10px] font-mono text-[#3AB0FF] uppercase tracking-widest drop-shadow-[0_0_5px_rgba(58,176,255,0.5)]">
          System Performance Telemetry
        </h3>
        <div className="flex items-center gap-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00FFA3] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00FFA3] shadow-[0_0_10px_rgba(0,255,163,0.8)]"></span>
          </span>
          <span className="text-[9px] font-bold font-mono text-[#00FFA3] uppercase tracking-widest drop-shadow-[0_0_8px_rgba(0,255,163,0.5)]">
            Live
          </span>
        </div>
      </div>

      <div className="flex-grow w-full h-full min-h-[200px] relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 0, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00FFA3" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00FFA3" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3AB0FF" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3AB0FF" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              stroke="#7B61FF"
              strokeOpacity={0.15}
              strokeDasharray="4 4"
              vertical={false}
            />
            <XAxis
              dataKey="time"
              stroke="#7B61FF"
              strokeOpacity={0.4}
              tick={{ fill: 'rgba(58,176,255,0.7)', fontSize: 9, fontFamily: 'monospace' }}
              tickLine={false}
              axisLine={false}
              tickMargin={12}
            />
            <YAxis
              stroke="#7B61FF"
              strokeOpacity={0.4}
              tick={{ fill: 'rgba(58,176,255,0.7)', fontSize: 9, fontFamily: 'monospace' }}
              domain={[0, 100]}
              tickCount={6}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ stroke: 'rgba(0,255,163,0.4)', strokeWidth: 1, strokeDasharray: '4 4' }}
            />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              formatter={(value) => (
                <span className="text-[#3AB0FF] font-bold text-[10px] font-mono uppercase tracking-widest pl-1">
                  {value}
                </span>
              )}
              iconType="circle"
              iconSize={8}
            />
            <Area
              type="monotone"
              dataKey="cpu"
              name="CPU Core"
              stroke="#00FFA3"
              strokeWidth={4}
              fillOpacity={1}
              fill="url(#colorCpu)"
              isAnimationActive={true}
              animationDuration={500}
              activeDot={{
                r: 6,
                fill: '#00FFA3',
                strokeWidth: 0,
                style: { filter: 'drop-shadow(0px 0px 12px rgba(0,255,163,1))' },
              }}
            />
            <Area
              type="monotone"
              dataKey="ram"
              name="Mem Alloc"
              stroke="#3AB0FF"
              strokeWidth={4}
              fillOpacity={1}
              fill="url(#colorRam)"
              isAnimationActive={true}
              animationDuration={500}
              activeDot={{
                r: 6,
                fill: '#3AB0FF',
                strokeWidth: 0,
                style: { filter: 'drop-shadow(0px 0px 12px rgba(58,176,255,1))' },
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
