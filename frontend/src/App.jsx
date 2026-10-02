import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import MetricCard from './components/MetricCard';
import MetricChart from './components/MetricChart';
import ProcessesTable from './components/ProcessesTable';
import { Cpu, MemoryStick, HardDrive, Activity } from 'lucide-react';
import { formatBytes, formatUptime } from './utils/formatters';

function App() {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState('connecting');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchData = async () => {
    try {
      const response = await fetch('/api/metrics');
      if (!response.ok) throw new Error('Network response was not ok');
      const result = await response.json();

      setData(result);
      setStatus(result.alerts?.length > 0 ? 'warning' : 'healthy');
      setLastUpdated(new Date());

      setHistory((prev) => {
        const newHistory = [
          ...prev,
          {
            time: new Date().toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }),
            cpu: result.cpu.percent,
            ram: result.memory.percent,
          },
        ];
        return newHistory.slice(-20); // Keep last 20 data points
      });
    } catch (err) {
      console.error('Fetch error:', err);
      setStatus('error');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Layout
      status={status}
      lastUpdated={lastUpdated}
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      uptime={formatUptime(data?.uptime)}
    >
      {/* Asymmetric Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-12 gap-6 w-full auto-rows-min">
        {/* KPI Cards: Column 1-4 on Desktop */}
        <div className="col-span-1 md:col-span-4 lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-6">
          <MetricCard
            title="CPU Usage"
            icon={Cpu}
            percent={data?.cpu?.percent || 0}
            subtext={`${data?.cpu?.cores} Cores @ ${
              data?.cpu?.frequency && data.cpu.frequency >= 100 ? data.cpu.frequency : 'N/A'
            }${data?.cpu?.frequency && data.cpu.frequency >= 100 ? ' MHz' : ''}`}
            extraMetrics={[
              {
                label: 'Load Avg',
                value: data?.cpu?.load_avg
                  ? `${data.cpu.load_avg[0].toFixed(2)} | ${data.cpu.load_avg[1].toFixed(
                      2,
                    )} | ${data.cpu.load_avg[2].toFixed(2)}`
                  : 'N/A',
              },
              { label: 'Total Processes', value: data?.total_processes || 0 },
            ]}
            thresholdWarning={80}
            thresholdDanger={90}
            delay={0.1}
          />
          <MetricCard
            title="Memory"
            icon={MemoryStick}
            percent={data?.memory?.percent || 0}
            subtext={`${formatBytes(data?.memory?.used)} / ${formatBytes(data?.memory?.total)}`}
            extraMetrics={[
              {
                label: 'Swap Usage',
                value: `${formatBytes(data?.memory?.swap_used)} / ${formatBytes(
                  data?.memory?.swap_total,
                )} (${(data?.memory?.swap_percent || 0).toFixed(1)}%)`,
              },
            ]}
            thresholdWarning={85}
            thresholdDanger={95}
            delay={0.2}
          />
          <MetricCard
            title="Disk I/O"
            icon={HardDrive}
            percent={data?.disk?.percent || 0}
            subtext={`${formatBytes(data?.disk?.free)} Free`}
            extraMetrics={[
              {
                label: 'Read',
                value: `${(data?.disk?.read_speed_mb || 0).toFixed(1)} MB/s`,
                icon: '📖',
              },
              {
                label: 'Write',
                value: `${(data?.disk?.write_speed_mb || 0).toFixed(1)} MB/s`,
                icon: '💾',
              },
            ]}
            thresholdWarning={85}
            thresholdDanger={95}
            delay={0.3}
          />
          <MetricCard
            title="Network Activity"
            icon={Activity}
            percent={Math.min(
              ((data?.network?.download_mb || 0) + (data?.network?.upload_mb || 0)) / 10,
              100,
            )}
            mainValue={data?.network?.download_mb || 0}
            mainUnit="MB/s"
            subtext="Current Download"
            extraMetrics={[
              {
                label: 'Download',
                value: `${(data?.network?.download_mb || 0).toFixed(2)} MB/s`,
                icon: '📥',
              },
              {
                label: 'Upload',
                value: `${(data?.network?.upload_mb || 0).toFixed(2)} MB/s`,
                icon: '📤',
              },
            ]}
            thresholdWarning={80}
            thresholdDanger={95}
            delay={0.4}
          />
        </div>

        {/* Right Column - Charts and Processes: Column 4-12 on Desktop */}
        <div className="col-span-1 md:col-span-4 lg:col-span-9 flex flex-col gap-6">
          <div className="h-[320px] w-full">
            <MetricChart data={history} delay={0.4} />
          </div>
          <div className="w-full flex-grow">
            <ProcessesTable
              processes={data?.processes || []}
              searchQuery={searchQuery}
              delay={0.5}
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;
