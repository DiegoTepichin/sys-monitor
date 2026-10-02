import React, { useEffect, useRef, useState } from 'react';
import HealthIndicator from './HealthIndicator';
import { motion, AnimatePresence } from 'framer-motion';
import { Monitor, Search, Menu, X, Command } from 'lucide-react';

export default function Layout({
  children,
  status,
  lastUpdated,
  searchQuery,
  setSearchQuery,
  uptime,
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const searchInputRef = useRef(null);

  // Cmd+K (macOS) / Ctrl+K (elsewhere) focuses the process search
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        searchInputRef.current?.focus();
        searchInputRef.current?.select();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen flex flex-col relative z-0">
      {/* Header */}
      <div className="pt-6 px-4 md:px-6 max-w-7xl mx-auto w-full">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="sticky top-0 z-50 cyber-panel px-4 py-3 md:px-6 md:py-4 flex justify-between items-center bg-[#0A0514]/80 backdrop-blur-3xl border border-[#7B61FF]/30"
        >
          {/* Logo Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="flex items-center gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00FFA3]/20 to-[#7B61FF]/20 border border-[#00FFA3]/50 flex items-center justify-center text-[#00FFA3] shadow-[0_0_20px_rgba(0,255,163,0.3)]">
              <Monitor size={20} />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2 drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
                SYS_MONITOR
              </h1>
            </div>
          </motion.div>

          {/* Process search (Desktop) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="hidden md:flex items-center relative max-w-md w-full mx-8"
          >
            <div className="absolute left-3 text-[#3AB0FF]/60 pointer-events-none">
              <Search size={16} />
            </div>
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search processes..."
              aria-label="Search processes (Cmd+K or Ctrl+K)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#1E0F36]/80 border border-[#7B61FF]/30 rounded-xl py-2 pl-10 pr-12 text-sm text-white focus:outline-none focus:border-[#00FFA3] focus:ring-1 focus:ring-[#00FFA3] transition-all placeholder:text-[#3AB0FF]/40 shadow-inner"
            />
            <div className="absolute right-3 text-[#7B61FF] pointer-events-none flex items-center gap-1">
              <Command size={12} />
              <span className="text-[10px] font-mono">K</span>
            </div>
          </motion.div>

          {/* Status & Mobile Toggle */}
          <div className="flex items-center gap-4">
            {uptime && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1, duration: 0.5 }}
                className="hidden lg:flex flex-col items-end border-r border-[#7B61FF]/30 pr-4 mr-1"
              >
                <span className="text-[9px] text-[#3AB0FF]/60 font-mono tracking-widest uppercase">
                  Uptime
                </span>
                <span className="text-[11px] font-mono font-bold text-[#00FFA3] drop-shadow-[0_0_5px_rgba(0,255,163,0.3)]">
                  {uptime}
                </span>
              </motion.div>
            )}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="hidden sm:block"
            >
              <HealthIndicator status={status} lastUpdated={lastUpdated} />
            </motion.div>

            {/* Mobile Menu Toggle */}
            <button
              className="md:hidden p-2 text-[#7B61FF] hover:text-[#00FFA3] transition-colors"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </motion.header>

        {/* Mobile Menu Dropdown */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0, y: -10 }}
              animate={{ opacity: 1, height: 'auto', y: 0 }}
              exit={{ opacity: 0, height: 0, y: -10 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="md:hidden mt-2 cyber-panel p-4 overflow-hidden"
            >
              <div className="flex flex-col gap-4">
                <div className="relative">
                  <div className="absolute left-3 top-2.5 text-[#3AB0FF]/60">
                    <Search size={16} />
                  </div>
                  <input
                    type="text"
                    placeholder="Search processes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-[#1E0F36]/80 border border-[#7B61FF]/30 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-[#00FFA3]"
                  />
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-[#7B61FF]/20">
                  <span className="text-xs text-[#3AB0FF]/80">System Status</span>
                  <HealthIndicator status={status} lastUpdated={lastUpdated} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col gap-6">
        {children}
      </main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="py-8 text-center"
      >
        <p className="text-xs text-[#7B61FF]/60 font-mono tracking-wide">
          SYS_MONITOR · MIT License
        </p>
      </motion.footer>
    </div>
  );
}
