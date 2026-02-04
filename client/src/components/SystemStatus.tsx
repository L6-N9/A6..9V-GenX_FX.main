import React, { useState, useEffect } from 'react';
import { Activity, Shield, Database, Zap, Clock } from 'lucide-react';

interface SystemStatusData {
  api_status: string;
  database_status: string;
  model_status: string;
  trading_enabled: boolean;
  last_update: string;
  active_strategies: string[];
}

interface SystemMetrics {
  requests_total: number;
  predictions_total: number;
  trades_total: number;
  accuracy: number;
}

const SystemStatus: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusData | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const API = import.meta.env.VITE_API_URL || '';
      try {
        const [statusRes, metricsRes] = await Promise.all([
          fetch(`${API}/api/v1/system/status`),
          fetch(`${API}/api/v1/system/metrics`)
        ]);

        if (statusRes.ok && metricsRes.ok) {
          const statusData = await statusRes.json();
          const metricsData = await metricsRes.json();
          setStatus(statusData);
          setMetrics(metricsData);
        } else {
          setError('Failed to fetch system data');
        }
      } catch (err) {
        setError('Error connecting to the system API');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mt-8 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mt-8">
        <div className="text-red-600 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-8">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 flex items-center gap-2">
        <Activity className="w-6 h-6 text-blue-600" />
        System Health & Metrics
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-600">API Status</span>
            <Shield className={`w-4 h-4 ${status?.api_status === 'healthy' ? 'text-green-500' : 'text-red-500'}`} />
          </div>
          <div className="text-lg font-bold text-gray-900 capitalize">{status?.api_status}</div>
        </div>

        <div className="p-4 bg-green-50 rounded-lg border border-green-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-600">Database</span>
            <Database className={`w-4 h-4 ${status?.database_status === 'healthy' ? 'text-green-500' : 'text-red-500'}`} />
          </div>
          <div className="text-lg font-bold text-gray-900 capitalize">{status?.database_status}</div>
        </div>

        <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-600">ML Model</span>
            <Zap className={`w-4 h-4 ${status?.model_status === 'healthy' ? 'text-green-500' : 'text-red-500'}`} />
          </div>
          <div className="text-lg font-bold text-gray-900 capitalize">{status?.model_status}</div>
        </div>

        <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-orange-600">Trading</span>
            <div className={`w-3 h-3 rounded-full ${status?.trading_enabled ? 'bg-green-500' : 'bg-red-500'}`}></div>
          </div>
          <div className="text-lg font-bold text-gray-900">{status?.trading_enabled ? 'Enabled' : 'Disabled'}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{metrics?.requests_total.toLocaleString()}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">Total Requests</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{metrics?.predictions_total.toLocaleString()}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">AI Predictions</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{metrics?.trades_total.toLocaleString()}</div>
          <div className="text-xs text-gray-500 uppercase mt-1">Total Trades</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">{((metrics?.accuracy || 0) * 100).toFixed(1)}%</div>
          <div className="text-xs text-gray-500 uppercase mt-1">ML Accuracy</div>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-gray-100 flex flex-wrap gap-4 items-center justify-between text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4" />
          <span>Last Updated: {status?.last_update ? new Date(status.last_update).toLocaleTimeString() : 'N/A'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-medium">Active Strategies:</span>
          <div className="flex gap-2">
            {status?.active_strategies.map((strategy) => (
              <span key={strategy} className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                {strategy.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;
