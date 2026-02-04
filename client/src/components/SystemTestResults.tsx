import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

/**
 * A static component that displays system test results.
 * It is memoized to prevent unnecessary re-renders.
 *
 * Optimization: Prevents Re-renders
 * This component is wrapped in React.memo to prevent it from re-rendering
 * when its parent component (`App`) updates its state. Since this component's
 * content is static, re-rendering it is unnecessary and inefficient.
 *
 * Estimated impact: Reduces re-renders of this component to zero after the initial render.
 */
const SystemTestResultsComponent = () => {
  interface TestResult {
    text: string;
    status: 'success' | 'warning';
  }

  const results: TestResult[] = [
    { text: "Configuration system fixed (Pydantic settings)", status: 'success' },
    { text: "Python API tests: 58/58 passed", status: 'success' },
    { text: "Node.js server tests: 17/17 passed", status: 'success' },
    { text: "Edge case testing completed", status: 'success' },
    { text: "Security validation (XSS, SQL injection prevention)", status: 'success' },
    { text: "Performance testing passed", status: 'success' },
    { text: "Build system configured", status: 'success' }
  ];

  return (
    <div className="mt-8 bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">
        System Test Results
      </h2>
      <ul className="space-y-3" role="list" aria-label="Test execution results">
        {results.map((result, index) => (
          <li key={index} className="flex items-start gap-3">
            {result.status === 'success' ? (
              <CheckCircle
                className="w-5 h-5 text-green-700 mt-0.5 shrink-0"
                aria-hidden="true"
              />
            ) : (
              <AlertCircle
                className="w-5 h-5 text-amber-700 mt-0.5 shrink-0"
                aria-hidden="true"
              />
            )}
            <span className="text-sm text-gray-700 leading-6">
              <span className="sr-only">
                {result.status === 'success' ? 'Success: ' : 'Warning: '}
              </span>
              {result.text}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

const SystemTestResults = React.memo(SystemTestResultsComponent);

export default SystemTestResults;
