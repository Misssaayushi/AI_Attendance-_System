import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

const Records = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Attendance Records</h1>
          <p className="text-gray-400">View and export historical data.</p>
        </div>
        <Button variant="outline">Export CSV</Button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-800/50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Name</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">ID</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">2026-05-13</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">Alice Smith</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">STU-90210</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">09:01 AM</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">Present</td>
              </tr>
              {/* More rows would be mapped here */}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default Records;
