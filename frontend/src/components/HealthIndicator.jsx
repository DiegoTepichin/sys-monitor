import React from 'react';
import { Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

const STATUS_CONFIG = {
  healthy: {
    dotColor: 'bg-[#00FFA3]',
    dotInlineColor: '#00FFA3',
    pulseColor: 'rgba(0, 255, 163, 0.6)',
    textColor: 'text-[#00FFA3]',
    text: 'SYS_ONLINE',
    Icon: Wifi,
  },
  warning: {
    dotColor: 'bg-amber-400',
    dotInlineColor: '#fbbf24',
    pulseColor: 'rgba(251,191,36,0.6)',
    textColor: 'text-amber-400',
    text: 'SYS_WARN',
    Icon: AlertTriangle,
  },
  error: {
    dotColor: 'bg-rose-500',
    dotInlineColor: '#f43f5e',
    pulseColor: 'rgba(244,63,94,0.6)',
    textColor: 'text-rose-400',
    text: 'SYS_OFFLINE',
    Icon: WifiOff,
  },
};

export default function HealthIndicator({ status, lastUpdated }) {
  const isOffline = status === 'error';
  const isWarning = status === 'warning';
  const key = isOffline ? 'error' : isWarning ? 'warning' : 'healthy';
  const { dotColor, dotInlineColor, pulseColor, textColor, text, Icon } = STATUS_CONFIG[key];

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex items-center gap-3 bg-[#0A0514]/80 border border-[#00FFA3]/30 rounded-full pl-3 pr-4 py-1.5 shadow-[0_0_15px_rgba(0,255,163,0.1)] backdrop-blur-md">
        <div className="relative flex items-center justify-center w-3 h-3">
          <motion.div
            className={`absolute w-full h-full rounded-full ${dotColor}`}
            initial={{ scale: 0.8, opacity: 1 }}
            animate={{ scale: 2.5, opacity: 0 }}
            transition={{ repeat: Infinity, duration: 1.5, ease: 'easeOut' }}
            style={{ backgroundColor: pulseColor }}
          />
          <div
            className={`relative w-2 h-2 rounded-full ${dotColor} shadow-[0_0_12px_currentColor]`}
            style={{ color: dotInlineColor }}
          ></div>
        </div>

        <div className="flex items-center gap-1.5">
          <Icon size={12} className={textColor} />
          <span
            className={`text-[10px] font-mono tracking-widest font-bold ${textColor} drop-shadow-[0_0_8px_currentColor]`}
          >
            {text}
          </span>
        </div>
      </div>

      {lastUpdated && (
        <span className="text-[9px] text-[#3AB0FF]/60 font-mono tracking-widest uppercase mr-2">
          Sync: {lastUpdated.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}
