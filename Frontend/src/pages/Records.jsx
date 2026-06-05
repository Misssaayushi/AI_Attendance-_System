import React, { useState, useEffect, useMemo } from 'react';
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
import { listAttendance, getExportPreview } from '../services/api';
import { extractData, extractErrorMessage } from '../services/apiHelpers';

// Debounce custom hook to optimize search inputs
const useDebounce = (value, delay = 400) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
};

const Records = () => {
  const [records, setRecords] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter States
  const [rawSearch, setRawSearch] = useState('');
  const debouncedSearch = useDebounce(rawSearch, 400);
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // Sorting State
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' });

  const pageSize = 10;

  // Fetch Attendance Records from API whenever filters or pages change
  const fetchRecords = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = {
        page: currentPage,
        page_size: pageSize,
      };

      if (debouncedSearch) params.search = debouncedSearch;
      if (selectedDept !== 'All') params.department = selectedDept;
      if (selectedStatus !== 'All') params.status = selectedStatus;
      if (selectedDate) {
        params.from_date = selectedDate;
        params.to_date = selectedDate;
      }

      const response = await listAttendance(params);
      const responseData = extractData(response);

      setRecords(responseData.items || []);
      setTotalRecords(responseData.total || 0);
      setTotalPages(responseData.pages || 1);
    } catch (err) {
      console.error('Failed to fetch records:', err);
      setError(extractErrorMessage(err) || 'Failed to load attendance database records.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [currentPage, debouncedSearch, selectedDept, selectedStatus, selectedDate]);

  // Adjust pagination if inputs change
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearch, selectedDept, selectedStatus, selectedDate]);

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
    setRawSearch('');
    setSelectedDept('All');
    setSelectedStatus('All');
    setSelectedDate('');
    setCurrentPage(1);
  };

  // Format Time representation from backend HH:MM:SS to 12h formats
  const formatTime = (timeStr) => {
    if (!timeStr || timeStr === '---') return '---';
    try {
      const parts = timeStr.split(':');
      if (parts.length < 2) return timeStr;
      const hour = parseInt(parts[0], 10);
      const min = parts[1];
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${min} ${ampm}`;
    } catch (e) {
      return timeStr;
    }
  };

  // Sorting Logic on returned Records
  const sortedRecords = useMemo(() => {
    if (!sortConfig.key) return records;

    const sorted = [...records];
    sorted.sort((a, b) => {
      let valA = '';
      let valB = '';

      if (sortConfig.key === 'name') {
        valA = a.student_name || '';
        valB = b.student_name || '';
      } else if (sortConfig.key === 'department') {
        valA = a.department || '';
        valB = b.department || '';
      } else if (sortConfig.key === 'date') {
        valA = `${a.attendance_date}T${a.attendance_time || '00:00:00'}`;
        valB = `${b.attendance_date}T${b.attendance_time || '00:00:00'}`;
      } else if (sortConfig.key === 'status') {
        valA = a.status || '';
        valB = b.status || '';
      }

      if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
      if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [records, sortConfig]);

  // Server-Side Export CSV generator
  const handleExportCSV = async () => {
    try {
      const params = {};
      if (selectedDate) {
        params.from_date = selectedDate;
        params.to_date = selectedDate;
      }

      const response = await getExportPreview(params);
      const responseData = extractData(response);
      const rows = responseData.rows || [];

      if (rows.length === 0) {
        alert("No attendance data available to export for selected query.");
        return;
      }

      const headers = ['Student ID', 'Student Name', 'Department', 'Date', 'Time', 'Status'];
      const csvRows = rows.map(r => [
        r.roll_number || r.student_id || '',
        r.student_name || '',
        r.department || '',
        r.attendance_date || r.date || '',
        formatTime(r.attendance_time || r.time),
        r.status || ''
      ]);

      const csvContent = "data:text/csv;charset=utf-8," 
        + [headers.join(','), ...csvRows.map(e => e.map(val => `"${val}"`).join(","))].join("\n");
        
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `attendance_records_${selectedDate || 'all'}.csv`);
      document.body.appendChild(link);
      
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Export CSV failed:', err);
      alert("Failed to export attendance data: " + extractErrorMessage(err));
    }
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
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-500/10 text-gray-400 border border-gray-500/20">
            <span>{status || 'Unknown'}</span>
          </span>
        );
    }
  };

  // Maps flat attendance schema object to the format expected by the RecordDetailModal
  const handleOpenDetailModal = (record) => {
    setSelectedRecord({
      id: record.roll_number || `STU-${record.student_id}`,
      name: record.student_name || 'Registered Student',
      department: record.department || 'General',
      date: record.attendance_date,
      time: formatTime(record.attendance_time),
      status: record.status
    });
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
              onChange={(e) => setSelectedDate(e.target.value)}
              className="w-full md:w-auto pl-9 pr-4 py-2 bg-gray-900/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer"
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
              value={rawSearch}
              onChange={(e) => setRawSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            />
          </div>

          {/* Department Selection filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
            <select 
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer"
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
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none cursor-pointer"
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
        {error && (
          <div className="p-4 bg-red-950/20 border-b border-red-900/30 text-center text-xs text-red-400">
            {error}
          </div>
        )}
        
        <div className="overflow-x-auto relative min-h-[250px]">
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
              {isLoading ? (
                [...Array(pageSize)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan="5" className="px-6 py-5">
                      <div className="h-4 bg-gray-800/50 rounded w-full"></div>
                    </td>
                  </tr>
                ))
              ) : sortedRecords.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-xs text-gray-500 italic">
                    No biometric attendance logs found.
                  </td>
                </tr>
              ) : (
                sortedRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-850/15 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                          <User size={16} />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white group-hover:text-blue-400 transition-colors leading-none mb-1">
                            {record.student_name || 'Unknown Student'}
                          </p>
                          <p className="text-[10px] text-gray-500 font-mono uppercase">{record.roll_number || `ID: ${record.student_id}`}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 bg-gray-850 border border-gray-800 rounded-lg text-[9px] font-bold text-gray-400 uppercase tracking-wider">
                        {record.department || 'General'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-xs text-gray-300 font-semibold leading-none mb-1">{record.attendance_date}</p>
                      <p className="text-[10px] text-gray-500 font-mono">{formatTime(record.attendance_time)}</p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(record.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-xs font-bold space-x-2">
                      <button 
                        onClick={() => handleOpenDetailModal(record)}
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
        {!isLoading && totalPages > 1 && (
          <div className="p-4 border-t border-gray-800/80 bg-gray-900/20 flex items-center justify-between">
            <p className="text-[10px] text-gray-500 font-semibold uppercase">
              Page {currentPage} of {totalPages} ({totalRecords} Logs)
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
