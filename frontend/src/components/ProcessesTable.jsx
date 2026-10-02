import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal } from 'lucide-react';

export default function ProcessesTable({ processes, searchQuery = '', delay = 0 }) {
  // Filter processes by the header search query
  const filteredProcesses = React.useMemo(() => {
    if (!processes) return [];
    let list = processes;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      list = processes.filter(
        (p) => p.name.toLowerCase().includes(query) || p.pid.toString().includes(query),
      );
    }
    return list.slice(0, 5); // Show at most 5 processes
  }, [processes, searchQuery]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
      className="cyber-panel p-6 flex-grow flex flex-col relative overflow-hidden min-h-[300px]"
    >
      <div className="flex items-center justify-between mb-6 border-b border-[#7B61FF]/20 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[#7B61FF]/20 border border-[#7B61FF]/50 text-[#00FFA3] shadow-[0_0_15px_rgba(0,255,163,0.3)]">
            <Terminal size={16} />
          </div>
          <h3 className="text-[10px] font-mono text-[#3AB0FF] uppercase tracking-widest drop-shadow-[0_0_5px_rgba(58,176,255,0.4)]">
            Active Processes
          </h3>
        </div>

        <div className="text-[10px] font-mono text-[#7B61FF]">
          Showing{' '}
          <span className="text-[#00FFA3] drop-shadow-[0_0_5px_rgba(0,255,163,0.5)]">
            {filteredProcesses.length}
          </span>{' '}
          processes
        </div>
      </div>

      <div className="flex-grow overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-[#7B61FF] text-[9px] font-mono uppercase tracking-widest border-b border-[#7B61FF]/20">
              <th className="pb-3 pl-4">PID</th>
              <th className="pb-3">Task Name</th>
              <th className="pb-3 text-right">CPU %</th>
              <th className="pb-3 text-right pr-4">Mem %</th>
            </tr>
          </thead>
          <tbody className="relative">
            {!filteredProcesses || filteredProcesses.length === 0 ? (
              <tr>
                <td colSpan="4" className="py-16 text-center">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Terminal size={24} className="text-[#7B61FF]/40" />
                    <span className="text-[#7B61FF] text-xs font-mono uppercase tracking-widest">
                      No matching processes
                    </span>
                  </div>
                </td>
              </tr>
            ) : (
              <AnimatePresence mode="popLayout">
                {filteredProcesses.map((proc) => (
                  <motion.tr
                    layout
                    initial={{ opacity: 0, x: -20, filter: 'blur(4px)' }}
                    animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, scale: 0.95, filter: 'blur(4px)' }}
                    transition={{
                      layout: { type: 'spring', bounce: 0.2, duration: 0.6 },
                      opacity: { duration: 0.2 },
                    }}
                    key={proc.pid}
                    className="group hover:bg-[#7B61FF]/20 transition-all duration-200 border-b border-[#7B61FF]/10 last:border-0 hover:shadow-[inset_0_0_20px_rgba(123,97,255,0.1)]"
                  >
                    <td className="py-3 text-xs font-mono text-[#3AB0FF] pl-4 rounded-l-xl group-hover:text-[#00FFA3] transition-colors">
                      {proc.pid}
                    </td>
                    <td
                      className="py-3 text-sm font-semibold text-white/90 max-w-[120px] truncate group-hover:text-white transition-colors tracking-tight drop-shadow-sm"
                      title={proc.name}
                    >
                      {proc.name}
                    </td>
                    <td className="py-3 text-sm font-mono text-right text-[#00FFA3] drop-shadow-[0_0_8px_rgba(0,255,163,0.3)]">
                      {proc.cpu_percent ? proc.cpu_percent.toFixed(1) : '0.0'}
                    </td>
                    <td className="py-3 text-sm font-mono text-right text-[#3AB0FF] pr-4 rounded-r-xl drop-shadow-[0_0_8px_rgba(58,176,255,0.3)]">
                      {proc.memory_percent ? proc.memory_percent.toFixed(1) : '0.0'}
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            )}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}
