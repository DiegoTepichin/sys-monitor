import React, { useEffect, useRef } from 'react';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { motion, useSpring, useTransform, useMotionValue } from 'framer-motion';

const HEALTHY_COLOR = '#00FFA3';
const WARNING_COLOR = '#fbbf24';
const DANGER_COLOR = '#fb7185';

const STATUS_MAP = {
  healthy: {
    Icon: CheckCircle2,
    statusColor: `text-[${HEALTHY_COLOR}]`,
    progressGradient: 'from-[#00FFA3] to-[#3AB0FF]',
    glowClass: 'bg-[#00FFA3]',
    inlineColor: HEALTHY_COLOR,
  },
  warning: {
    Icon: AlertTriangle,
    statusColor: `text-[${WARNING_COLOR}]`,
    progressGradient: 'from-amber-400 to-orange-400',
    glowClass: 'bg-amber-400',
    inlineColor: WARNING_COLOR,
  },
  danger: {
    Icon: XCircle,
    statusColor: `text-[${DANGER_COLOR}]`,
    progressGradient: 'from-rose-500 to-orange-400',
    glowClass: 'bg-rose-500',
    inlineColor: DANGER_COLOR,
  },
};

function AnimatedNumber({ value }) {
  const spring = useSpring(value, { mass: 0.8, stiffness: 75, damping: 15 });
  const display = useTransform(spring, (current) => current.toFixed(1));

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  return <motion.span>{display}</motion.span>;
}

export default function MetricCard({
  title,
  icon: Icon,
  percent,
  mainValue,
  mainUnit = '%',
  subtext,
  extraMetrics = [],
  thresholdWarning,
  thresholdDanger,
  delay = 0,
}) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-100, 100], [15, -15]);
  const rotateY = useTransform(x, [-100, 100], [-15, 15]);
  const rafId = useRef(null);

  function handleMouseMove(event) {
    if (rafId.current) return;
    rafId.current = requestAnimationFrame(() => {
      const rect = event.currentTarget.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      x.set(event.clientX - centerX);
      y.set(event.clientY - centerY);
      rafId.current = null;
    });
  }

  function handleMouseLeave() {
    if (rafId.current) {
      cancelAnimationFrame(rafId.current);
      rafId.current = null;
    }
    x.set(0);
    y.set(0);
  }

  let status;
  if (percent >= thresholdDanger) {
    status = 'danger';
  } else if (percent >= thresholdWarning) {
    status = 'warning';
  } else {
    status = 'healthy';
  }

  const {
    Icon: StatusIcon,
    statusColor,
    progressGradient,
    glowClass,
    inlineColor,
  } = STATUS_MAP[status];

  return (
    <motion.div
      style={{ perspective: 1000 }}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
      className="h-full"
    >
      <motion.div
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }}
        className="cyber-panel p-6 h-full flex flex-col justify-between group cursor-crosshair relative overflow-hidden"
      >
        <div
          className={`absolute -right-20 -top-20 w-48 h-48 rounded-full blur-[90px] opacity-25 pointer-events-none transition-colors duration-1000 ${glowClass}`}
        />

        <div
          className="flex justify-between items-start mb-6"
          style={{ transform: 'translateZ(30px)' }}
        >
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ rotate: 180, scale: 1.1 }}
              transition={{ duration: 0.4 }}
              className={`p-2 rounded-lg bg-[#7B61FF]/10 border border-[#7B61FF]/40 ${statusColor}`}
              style={{ color: inlineColor }}
            >
              <Icon size={18} />
            </motion.div>
            <h3 className="text-[10px] font-mono uppercase tracking-widest text-[#3AB0FF] drop-shadow-[0_0_5px_rgba(58,176,255,0.4)]">
              {title}
            </h3>
          </div>
          <motion.div whileHover={{ scale: 1.2 }}>
            <StatusIcon size={16} className={`${statusColor} drop-shadow-[0_0_8px_currentColor]`} />
          </motion.div>
        </div>

        <div className="mb-6" style={{ transform: 'translateZ(40px)' }}>
          <div className="text-5xl font-bold text-white mb-2 tracking-tighter flex items-baseline drop-shadow-[0_0_20px_rgba(255,255,255,0.4)]">
            <AnimatedNumber value={mainValue !== undefined ? mainValue : percent} />
            <span className="text-2xl text-[#3AB0FF] ml-1 font-mono drop-shadow-[0_0_10px_rgba(58,176,255,0.5)]">
              {mainUnit}
            </span>
          </div>
          <div className="text-xs text-[#7B61FF] font-mono tracking-wider mb-2 drop-shadow-[0_0_5px_rgba(123,97,255,0.3)] min-h-4">
            {subtext}
          </div>
          {extraMetrics && extraMetrics.length > 0 && (
            <div
              className="flex flex-col gap-1.5 mt-2 border-t border-[#7B61FF]/20 pt-3"
              style={{ transform: 'translateZ(10px)' }}
            >
              {extraMetrics.map((metric, i) => (
                <div key={i} className="flex justify-between items-center text-[10px] font-mono">
                  <span className="text-[#3AB0FF]/70 uppercase tracking-widest flex items-center gap-1">
                    {metric.icon && <span>{metric.icon}</span>}
                    {metric.label}
                  </span>
                  <span className="text-white drop-shadow-[0_0_5px_rgba(255,255,255,0.3)]">
                    {metric.value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div
          className="w-full h-2 bg-[#05020A]/80 rounded-full overflow-hidden border border-[#7B61FF]/30 relative shadow-inner"
          style={{ transform: 'translateZ(20px)' }}
        >
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${percent}%` }}
            transition={{ duration: 1, ease: 'circOut' }}
            className={`absolute left-0 top-0 h-full rounded-full bg-gradient-to-r ${progressGradient} shadow-[0_0_15px_currentColor]`}
          />
        </div>
      </motion.div>
    </motion.div>
  );
}
