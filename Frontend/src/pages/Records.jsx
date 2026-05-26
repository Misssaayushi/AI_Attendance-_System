import React, { useState, useMemo } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import RecordDetailModal from '../components/records/RecordDetailModal';
import { 
  Search, 
  Filter, 
  Download, 
  User, 
  Calendar, 
  Tag, 
  ChevronLeft, 
  ChevronRight, 
  ArrowUpDown,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle
} from 'lucide-react';

const mockAttendanceRecords = [
  { id: 'STU-2026-042', name: 'Rahul Sharma', date: '2026-05-20', time: '09:01 AM', department: 'CS', status: 'Present' },
  { id: 'STU-2026-015', name: 'Aman Verma', date: '2026-05-20', time: '09:12 AM', department: 'IT', status: 'Late' },
  { id: 'STU-2026-103', name: 'Priya Patel', date: '2026-05-20', time: '---', department: 'ME', status: 'Absent' },
  { id: 'STU-2026-089', name: 'Rohit Gupta', date: '2026-05-20', time: '08:55 AM', department: 'EE', status: 'Present' },
  { id: 'STU-2026-056', name: 'Neha Sharma', date: '2026-05-20', time: '09:02 AM', department: 'CS', status: 'Present' },
  { id: 'STU-2026-121', name: 'Shreya Sen', date: '2026-05-20', time: '09:05 AM', department: 'IT', status: 'Present' },
  { id: 'STU-2026-004', name: 'Karan Malhotra', date: '2026-05-20', time: '---', department: 'ME', status: 'Absent' },
  { id: 'STU-2026-077', name: 'Rohan Das', date: '2026-05-20', time: '09:00 AM', department: 'CS', status: 'Present' },
  { id: 'STU-2026-031', name: 'Aditya Roy', date: '2026-05-20', time: '09:15 AM', department: 'EE', status: 'Late' },
  { id: 'STU-2026-092', name: 'Sneha Patil', date: '2026-05-20', time: '08:58 AM', department: 'IT', status: 'Present' },
  { id: 'STU-2026-114', name: 'Vijay Singh', date: '2026-05-19', time: '09:03 AM', department: 'EE', status: 'Present' },
  { id: 'STU-2026-118', name: 'Poonam Yadav', date: '2026-05-19', time: '09:22 AM', department: 'CS', status: 'Late' },
  { id: 'STU-2026-125', name: 'Amit Shah', date: '2026-05-19', time: '---', department: 'ME', status: 'Absent' },
  { id: 'STU-2026-130', name: 'Suresh Kumar', date: '2026-05-19', time: '08:52 AM', department: 'IT', status: 'Present' },
  { id: 'STU-2026-144', name: 'Anita Desai', date: '2026-05-19', time: '09:01 AM', department: 'CS', status: 'Present' },
  { id: 'STU-2026-150', name: 'Vikram Seth', date: '2026-05-19', time: '09:10 AM', department: 'EE', status: 'Late' },
  { id: 'STU-2026-155', name: 'Kunal Kapoor', date: '2026-05-18', time: '08:59 AM', department: 'CS', status: 'Present' },
  { id: 'STU-2026-160', name: 'Meera Rajput', date: '2026-05-18', time: '---', department: 'IT', status: 'Absent' },
  { id: 'STU-2026-165', name: 'Rajesh Khanna', date: '2026-05-18', time: '09:05 AM', department: 'ME', status: 'Present' },
  { id: 'STU-2026-170', name: 'Deepika Padukone', date: '2026-05-18', time: '09:02 AM', department: 'EE', status: 'Present' }
];

const Records = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // Sorting State
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });

  const itemsPerPage = 8;

  // Sorting Handler
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Reset Filters utility
  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedDept('All');
    setSelectedStatus('All');
    setSelectedDate('');
    setCurrentPage(1);
  };

  // Filter and Sort Logic combined
  const filteredAndSortedRecords = useMemo(() => {
    let result = mockAttendanceRecords.filter(record => {
      const matchesSearch = 
        record.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.id.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesDept = selectedDept === 'All' || record.department === selectedDept;
      const matchesStatus = selectedStatus === 'All' || record.status === selectedStatus;
      const matchesDate = !selectedDate || record.date === selectedDate;

      return matchesSearch && matchesDept && matchesStatus && matchesDate;
    });

    // Apply Sorting
    if (sortConfig.key) {
      result.sort((a, b) => {
        let valA = a[sortConfig.key];
        let valB = b[sortConfig.key];

        if (sortConfig.key === 'time') {
          // Normalize absent time for logical sorting
          if (valA === '---') valA = 'ZZZZ';
          if (valB === '---') valB = 'ZZZZ';
        }

        if (valA < valB) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (valA > valB) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return result;
  }, [searchQuery, selectedDept, selectedStatus, selectedDate, sortConfig]);

  // Pagination bounds calculation
  const totalPages = Math.ceil(filteredAndSortedRecords.length / itemsPerPage) || 1;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedRecords = useMemo(() => {
    return filteredAndSortedRecords.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredAndSortedRecords, currentPage]);

  // Adjust page number if result sizes change
  React.useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  // Client-Side CSV Exporter
  const handleExportCSV = () => {
    if (filteredAndSortedRecords.length === 0) {
      alert("No data available to export.");
      return;
    }
    
    // Headers
    const headers = ['Student ID', 'Student Name', 'Department', 'Date', 'Time', 'Status'];
    
    // Convert rows
    const rows = filteredAndSortedRecords.map(record => [
      record.id,
      record.name,
      record.department,
      record.date,
      record.time,
      record.status
    ]);
    
    // Build CSV Content
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${val}"`).join(","))].join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `attendance_records_${selectedDate || 'all'}.csv`);
    document.body.appendChild(link);
    
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Present':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-500/10 text-green-400 border border-green-500/20">
            <CheckCircle size={10} />
            <span>Present</span>
          </span>
        );
      case 'Late':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
            <Clock size={10} />
            <span>Late</span>
          </span>
        );
      case 'Absent':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle size={10} />
            <span>Absent</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Title Header with action buttons */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-wide uppercase">Attendance Database</h1>
          <p className="text-[11px] text-gray-500 mt-1 font-medium">Query, filter, and audit full historical biometric scans.</p>
        </div>
        <div className="flex gap-3 w-full md:w-auto">
          <Button 
            onClick={handleExportCSV} 
            variant="outline" 
            className="flex items-center justify-center gap-2 flex-1 md:flex-none border-gray-800 bg-gray-900/50 hover:bg-gray-800/80 text-gray-300 hover:text-white"
          >
            <Download size={14} />
            <span>Export CSV</span>
          </Button>
          <div className="relative flex-1 md:flex-none">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" size={14} />
            <input 
              type="date"
              value={selectedDate}
              onChange={(e) => { setSelectedDate(e.target.value); setCurrentPage(1); }}
              className="w-full md:w-auto pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none"
            />
          </div>
        </div>
      </div>

      {/* Filters Card Panel */}
      <Card className="p-4 bg-gray-900/30 border border-gray-800/80">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {/* Search by student details */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
            <input 
              type="text" 
              placeholder="Search ID or Name..." 
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            />
          </div>

          {/* Department Selection filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
            <select 
              value={selectedDept}
              onChange={(e) => { setSelectedDept(e.target.value); setCurrentPage(1); }}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none"
            >
              <option value="All">All Departments</option>
              <option value="CS">Computer Science</option>
              <option value="IT">Information Technology</option>
              <option value="ME">Mechanical Engineering</option>
              <option value="EE">Electrical Engineering</option>
            </select>
          </div>

          {/* Status Selection filter */}
          <div className="relative">
            <Tag className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
            <select 
              value={selectedStatus}
              onChange={(e) => { setSelectedStatus(e.target.value); setCurrentPage(1); }}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none"
            >
              <option value="All">All Statuses</option>
              <option value="Present">Present</option>
              <option value="Absent">Absent</option>
              <option value="Late">Late</option>
            </select>
          </div>

          <Button 
            variant="secondary" 
            onClick={handleResetFilters} 
            className="w-full bg-gray-800 hover:bg-gray-750 text-gray-300 text-xs py-2 rounded-xl border border-gray-700/30"
          >
            Clear Filters
          </Button>
        </div>
      </Card>

      {/* Main Records Data Table Card */}
      <Card className="overflow-hidden border border-gray-800/80 bg-gray-900/40">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-900/30">
              <tr>
                <th 
                  onClick={() => handleSort('name')}
                  className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest cursor-pointer hover:text-blue-400 select-none transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Student</span>
                    <ArrowUpDown size={10} />
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('department')}
                  className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest cursor-pointer hover:text-blue-400 select-none transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Department</span>
                    <ArrowUpDown size={10} />
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('date')}
                  className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest cursor-pointer hover:text-blue-400 select-none transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Date / Time</span>
                    <ArrowUpDown size={10} />
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('status')}
                  className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest cursor-pointer hover:text-blue-400 select-none transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Status</span>
                    <ArrowUpDown size={10} />
                  </div>
                </th>
                <th className="px-6 py-4 text-right text-[10px] font-black text-gray-500 uppercase tracking-widest select-none">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 bg-transparent">
              {paginatedRecords.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-xs text-gray-500 italic">
                    No biometric attendance logs matched the filters.
                  </td>
                </tr>
              ) : (
                paginatedRecords.map((record, index) => (
                  <tr key={index} className="hover:bg-gray-850/15 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                          <User size={16} />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white group-hover:text-blue-400 transition-colors leading-none mb-1">{record.name}</p>
                          <p className="text-[10px] text-gray-500 font-mono uppercase">{record.id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 bg-gray-850 border border-gray-800 rounded-lg text-[9px] font-bold text-gray-400 uppercase tracking-wider">
                        {record.department}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-xs text-gray-300 font-semibold leading-none mb-1">{record.date}</p>
                      <p className="text-[10px] text-gray-500 font-mono">{record.time}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(record.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-xs font-bold space-x-2">
                      <button 
                        onClick={() => setSelectedRecord(record)}
                        className="text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 px-2.5 py-1.5 rounded-lg border border-transparent hover:border-blue-500/20 transition-all"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Footer controls with pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-gray-800/80 bg-gray-900/20 flex items-center justify-between">
            <p className="text-[10px] text-gray-500 font-semibold uppercase">
              Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredAndSortedRecords.length)} of {filteredAndSortedRecords.length} Logs
            </p>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="p-1.5 rounded-lg border border-gray-800 bg-gray-850 hover:bg-gray-800 text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={14} />
              </button>
              
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-7 h-7 text-xs font-bold rounded-lg border transition-all ${
                    currentPage === page 
                      ? 'bg-blue-600 border-blue-500 text-white shadow-md shadow-blue-500/20' 
                      : 'border-gray-850 bg-gray-850/40 text-gray-400 hover:text-white'
                  }`}
                >
                  {page}
                </button>
              ))}

              <button 
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="p-1.5 rounded-lg border border-gray-800 bg-gray-850 hover:bg-gray-800 text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </Card>

      {/* Verification Audit Detail Modal Overlay */}
      <RecordDetailModal 
        record={selectedRecord} 
        onClose={() => setSelectedRecord(null)} 
      />
    </div>
  );
};

export default Records;
