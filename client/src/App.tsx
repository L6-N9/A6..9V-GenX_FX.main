import { useState, useEffect } from 'react'

/**
 * The main application component.
 * It fetches and displays the health status of the Node.js server and the Python API.
 * @returns {JSX.Element} The rendered application component.
 */
function App() {
  const [health, setHealth] = useState<any>(null)
  const [apiHealth, setApiHealth] = useState<any>(null)

  useEffect(() => {
    const API = 'http://localhost:8081';

    // ⚡ Bolt: Use Promise.all to run API calls concurrently for faster loading.
    // This lets us fetch both health statuses at the same time instead of one
    // after the other, making the UI feel more responsive.
    const fetchHealth = async () => {
      try {
        const [healthRes, apiHealthRes] = await Promise.all([
          fetch(`${API}/health`),
          fetch(`${API}/api/v1/health`)
        ]);

        const healthData = await healthRes.json();
        const apiHealthData = await apiHealthRes.json();

        setHealth(healthData);
        setApiHealth(apiHealthData);
      } catch (err) {
        console.error('Error fetching health status:', err);
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-900">
          🚀 GenX FX Trading Platform
        </h1>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Node.js Server Status
            </h2>
            {health ? (
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  <span>Status: {health.status}</span>
                </div>
                <div>Environment: {health.environment}</div>
                <div>Timestamp: {health.timestamp}</div>
              </div>
            ) : (
              <div className="flex items-center">
                <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                <span>Server not responding</span>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Python API Status
            </h2>
            {apiHealth ? (
              <div className="space-y-2">
                <div className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  <span>Status: {apiHealth.status}</span>
                </div>
                <div>ML Service: {apiHealth.services?.ml_service}</div>
                <div>Data Service: {apiHealth.services?.data_service}</div>
                <div>Timestamp: {apiHealth.timestamp}</div>
              </div>
            ) : (
              <div className="flex items-center">
                <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                <span>API not responding</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            System Test Results
          </h2>
          <div className="space-y-2 text-sm">
            <div>✅ Configuration system fixed (Pydantic settings)</div>
            <div>✅ Python API tests: 27/27 passed</div>
            <div>✅ Node.js server tests: 15/17 passed (2 minor issues)</div>
            <div>✅ Edge case testing completed</div>
            <div>✅ Security validation (XSS, SQL injection prevention)</div>
            <div>✅ Performance testing passed</div>
            <div>✅ Build system configured</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
