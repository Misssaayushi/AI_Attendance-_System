import React, { useState, useEffect, useMemo } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import RecordDetailModal from '../components/records/RecordDetailModal';
import EditStudentModal from '../components/students/EditStudentModal';
import DeleteConfirmModal from '../components/students/DeleteConfirmModal';
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
  AlertTriangle,
  X,
  Edit,
  Trash2
} from 'lucide-react';
import { listStudents, markAttendance, updateAttendance, deleteAttendance, updateStudent, deleteStudent } from '../services/api';
import { extractData, extractErrorMessage } from '../services/apiHelpers';
import { useToast } from '../context/ToastContext';

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
  const [records, setRecords] = useState([]); // This will hold all students
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter States
  const [rawSearch, setRawSearch] = useState('');
  const debouncedSearch = useDebounce(rawSearch, 400);
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRecord, setSelectedRecord] = useState(null);
  
  // Edit/Delete States
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editRecord, setEditRecord] = useState(null);
  const [editStatus, setEditStatus] = useState('Present');
  const [editTime, setEditTime] = useState('');
  
  // Student Edit/Delete States
  const [editingStudent, setEditingStudent] = useState(null);
  const [deletingStudent, setDeletingStudent] = useState(null);
  const { addToast } = useToast();
  
  // Sorting State
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });

  const pageSize = 10;

  // Fetch all students and compute daily status
  const fetchRecords = async () => {
    try {
      setIsLoading(true);
      setError(null);

      let allStudents = [];
      let currentPageNum = 1;
      let morePages = true;
      
      while (morePages) {
        const params = {
          page: currentPageNum,
          page_size: 100, // Fetch max allowed by backend per page
        };
        if (selectedDate) params.date = selectedDate;

        const response = await listStudents(params);
        const responseData = extractData(response);
        const items = responseData.items || [];
        allStudents = [...allStudents, ...items];
        
        if (currentPageNum >= (responseData.pages || 1)) {
          morePages = false;
        } else {
          currentPageNum++;
        }
      }

      // Sort alphabetically by first name initially
      allStudents.sort((a, b) => (a.first_name || '').localeCompare(b.first_name || ''));

      setRecords(allStudents);
    } catch (err) {
      console.error('Failed to fetch records:', err);
      setError(extractErrorMessage(err) || 'Failed to load attendance database records.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
    // We only refetch when selectedDate changes because search/dept/status are done client-side
  }, [selectedDate]);

  // Handle client-side filtering and sorting
  const filteredAndSortedRecords = useMemo(() => {
    let result = [...records];

    // 1. Filter
    if (debouncedSearch) {
      const lowerSearch = debouncedSearch.toLowerCase();
      result = result.filter(r => 
        (r.first_name || '').toLowerCase().includes(lowerSearch) ||
        (r.last_name || '').toLowerCase().includes(lowerSearch) ||
        (r.roll_number || '').toLowerCase().includes(lowerSearch)
      );
    }
    if (selectedDept !== 'All') {
      result = result.filter(r => r.department === selectedDept);
    }

    // 2. Sort
    if (sortConfig.key) {
      result.sort((a, b) => {
        let valA = '';
        let valB = '';

        if (sortConfig.key === 'name') {
          valA = `${a.first_name} ${a.last_name}`;
          valB = `${b.first_name} ${b.last_name}`;
        } else if (sortConfig.key === 'department') {
          valA = a.department || '';
          valB = b.department || '';
        } else if (sortConfig.key === 'date') {
          // Both share the same date since we filter by day, sort by arrival time
          valA = a.arrival_time || '23:59:59';
          valB = b.arrival_time || '23:59:59';
        }

        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [records, debouncedSearch, selectedDept, sortConfig]);

  // Update pagination state when filtered data changes
  useEffect(() => {
    setTotalRecords(filteredAndSortedRecords.length);
    setTotalPages(Math.ceil(filteredAndSortedRecords.length / pageSize) || 1);
    setCurrentPage(1); // Reset to page 1 on filter changes
  }, [filteredAndSortedRecords]);

  // Paginated records for current page
  const paginatedRecords = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedRecords.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedRecords, currentPage]);

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
    setSelectedDate('');
    setCurrentPage(1);
    setSortConfig({ key: 'name', direction: 'asc' });
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

  // Client-Side Export CSV generator
  const handleExportCSV = () => {
    try {
      if (filteredAndSortedRecords.length === 0) {
        alert("No attendance data available to export for selected query.");
        return;
      }

      const headers = ['Student ID', 'Student Name', 'Department', 'Date', 'Time'];
      const displayDate = selectedDate || new Date().toISOString().split('T')[0];

      const csvRows = filteredAndSortedRecords.map(r => [
        r.roll_number || r.id || '',
        `${r.first_name} ${r.last_name}`.trim(),
        r.department || '',
        displayDate,
        formatTime(r.arrival_time) || '---'
      ]);

      const csvContent = "data:text/csv;charset=utf-8," 
        + [headers.join(','), ...csvRows.map(e => e.map(val => `"${val}"`).join(","))].join("\n");
        
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `attendance_records_${displayDate}.csv`);
      document.body.appendChild(link);
      
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Export CSV failed:', err);
      alert("Failed to export attendance data");
    }
  };



  const handleOpenDetailModal = (record) => {
    setSelectedRecord({
      id: record.roll_number || `STU-${record.id}`,
      name: `${record.first_name} ${record.last_name}`.trim(),
      department: record.department || 'General',
      date: selectedDate || new Date().toISOString().split('T')[0],
      time: formatTime(record.arrival_time),
      status: record.status || 'Absent'
    });
  };

  const handleOpenEditModal = (record) => {
    setEditRecord(record);
    setEditStatus(record.status || 'Present');
    
    let timeVal = '';
    if (record.arrival_time && record.arrival_time !== '---') {
      timeVal = record.arrival_time.substring(0, 5); // get HH:MM
    } else {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      timeVal = `${hours}:${minutes}`;
    }
    setEditTime(timeVal);
    setIsEditModalOpen(true);
  };

  const handleSaveEdit = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const targetDate = selectedDate || new Date().toISOString().split('T')[0];
      const timeToSend = editTime ? `${editTime}:00` : null;

      if (editRecord.attendance_id) {
        await updateAttendance(editRecord.attendance_id, {
          status: editStatus,
          attendance_time: timeToSend
        });
      } else {
        await markAttendance({
          student_id: editRecord.id,
          attendance_date: targetDate,
          attendance_time: timeToSend,
          status: editStatus,
          source: 'manual_admin'
        });
      }
      setIsEditModalOpen(false);
      fetchRecords();
    } catch (err) {
      console.error('Failed to save attendance record:', err);
      setError(extractErrorMessage(err) || 'Failed to save attendance record.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteRecord = async (record) => {
    if (!record.attendance_id) return;
    if (!window.confirm(`Are you sure you want to delete the attendance log for ${record.first_name} ${record.last_name}?`)) {
      return;
    }
    try {
      setIsLoading(true);
      setError(null);
      await deleteAttendance(record.attendance_id);
      fetchRecords();
    } catch (err) {
      console.error('Failed to delete attendance record:', err);
      setError(extractErrorMessage(err) || 'Failed to delete attendance record.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStudentEditSave = async (studentId, formData) => {
    try {
      await updateStudent(studentId, formData);
      setEditingStudent(null);
      addToast('Student updated successfully', 'success');
      fetchRecords();
    } catch (error) {
      console.error("Failed to update student:", error);
      addToast("Failed to update student", "error");
    }
  };

  const handleStudentDeleteConfirm = async (studentId) => {
    try {
      await deleteStudent(studentId);
      setDeletingStudent(null);
      addToast('Student deleted successfully', 'success');
      fetchRecords();
    } catch (error) {
      console.error("Failed to delete student:", error);
      if (error.response?.status === 404) {
        setDeletingStudent(null);
        fetchRecords();
      } else {
        addToast("Failed to delete student", "error");
      }
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
                    <span>Department / Sem</span>
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

                <th className="px-6 py-4 text-center text-[10px] font-black text-gray-500 uppercase tracking-widest select-none border-l border-gray-800">
                  Attendance Actions
                </th>
                <th className="px-6 py-4 text-center text-[10px] font-black text-gray-500 uppercase tracking-widest select-none border-l border-gray-800">
                  Profile Actions
                </th>
              </tr>
            </thead>
            
            <tbody className="divide-y divide-gray-800/60 bg-transparent">
              {isLoading ? (
                [...Array(pageSize)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan="4" className="px-6 py-5">
                      <div className="h-4 bg-gray-800/50 rounded w-full"></div>
                    </td>
                  </tr>
                ))
              ) : paginatedRecords.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-12 text-center text-xs text-gray-500 italic">
                    No students match the current filters.
                  </td>
                </tr>
              ) : (
                paginatedRecords.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-850/15 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                          <User size={16} />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white group-hover:text-blue-400 transition-colors leading-none mb-1">
                            {`${record.first_name} ${record.last_name}`.trim() || 'Unknown Student'}
                          </p>
                          <p className="text-[10px] text-gray-500 font-mono uppercase">{record.roll_number || `ID: ${record.id}`}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-gray-850 border border-gray-800 rounded-lg text-[9px] font-bold text-gray-400 uppercase tracking-wider">
                          {record.department || 'General'}
                        </span>
                        {record.semester && (
                          <span className="px-2 py-0.5 bg-gray-850 border border-gray-800 rounded-lg text-[9px] font-bold text-gray-400 uppercase tracking-wider">
                            Sem {record.semester}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-xs text-gray-300 font-semibold leading-none mb-1">{selectedDate || new Date().toISOString().split('T')[0]}</p>
                      <p className="text-[10px] text-gray-500 font-mono">{formatTime(record.arrival_time)}</p>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap text-center text-xs font-bold space-x-2 border-l border-gray-800/50">
                      <button 
                        onClick={() => handleOpenDetailModal(record)}
                        className="text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 px-2.5 py-1.5 rounded-lg border border-transparent hover:border-blue-500/20 transition-all"
                      >
                        View
                      </button>
                      <button 
                        onClick={() => handleOpenEditModal(record)}
                        className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 px-2.5 py-1.5 rounded-lg border border-transparent hover:border-blue-500/20 transition-all"
                      >
                        {record.arrival_time && record.arrival_time !== '---' ? 'Edit' : 'Mark'}
                      </button>
                      {record.arrival_time && record.arrival_time !== '---' && (
                        <button 
                          onClick={() => handleDeleteRecord(record)}
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2.5 py-1.5 rounded-lg border border-transparent hover:border-red-500/20 transition-all"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium border-l border-gray-800/50">
                      <button 
                        onClick={() => setEditingStudent(record)}
                        className="text-blue-400 hover:text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 p-2 rounded-lg transition-colors mr-2 inline-flex items-center"
                        title="Edit Student Profile"
                      >
                        <Edit size={16} />
                      </button>
                      <button 
                        onClick={() => setDeletingStudent(record)}
                        className="text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 p-2 rounded-lg transition-colors inline-flex items-center"
                        title="Delete Student Profile"
                      >
                        <Trash2 size={16} />
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
              
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                 let startPage = Math.max(1, currentPage - 2);
                 if (startPage + 4 > totalPages) startPage = Math.max(1, totalPages - 4);
                 return startPage + i;
              }).map(page => (
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

      {/* Edit/Mark Attendance Modal Overlay */}
      {isEditModalOpen && editRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
            onClick={() => setIsEditModalOpen(false)}
          />

          {/* Modal Content */}
          <Card className="relative w-full max-w-md bg-gray-900 border border-gray-800/80 shadow-2xl overflow-hidden rounded-2xl z-10 animate-in fade-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="p-5 border-b border-gray-800/80 flex items-center justify-between bg-gray-950/40">
              <div>
                <h3 className="text-base font-bold text-white uppercase tracking-wider">
                  {editRecord.arrival_time && editRecord.arrival_time !== '---' ? 'Edit Attendance Log' : 'Mark Attendance'}
                </h3>
                <p className="text-[10px] text-gray-500 mt-0.5">
                  Manual override for {`${editRecord.first_name} ${editRecord.last_name}`}
                </p>
              </div>
              <button 
                onClick={() => setIsEditModalOpen(false)}
                className="p-1.5 rounded-lg bg-gray-800/50 hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-4">
              {/* Status Selection */}
              <div className="space-y-2">
                <label className="text-[10px] font-black text-gray-500 uppercase tracking-wider">Status</label>
                <div className="grid grid-cols-3 gap-2">
                  {['Present', 'Late', 'Absent'].map((status) => (
                    <button
                      key={status}
                      type="button"
                      onClick={() => setEditStatus(status)}
                      className={`py-2 px-3 text-xs font-bold rounded-xl border transition-all ${
                        editStatus === status
                          ? status === 'Present'
                            ? 'bg-green-500/20 border-green-500 text-green-400'
                            : status === 'Late'
                              ? 'bg-orange-500/20 border-orange-500 text-orange-400'
                              : 'bg-red-500/20 border-red-500 text-red-400'
                          : 'bg-gray-850/50 border-gray-800 text-gray-400 hover:bg-gray-800/50'
                      }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Selection */}
              <div className="space-y-2">
                <label className="text-[10px] font-black text-gray-500 uppercase tracking-wider">Arrival Time</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={14} />
                  <input
                    type="time"
                    value={editTime}
                    onChange={(e) => setEditTime(e.target.value)}
                    className="w-full pl-9 pr-4 py-2.5 bg-gray-850/50 border border-gray-800 rounded-xl text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-800/80 bg-gray-950/20 flex justify-end gap-3">
              <button 
                onClick={() => setIsEditModalOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-750 text-white rounded-xl text-xs font-bold transition-all"
              >
                Cancel
              </button>
              <button 
                onClick={handleSaveEdit}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-blue-500/20"
              >
                Save Log
              </button>
            </div>
          </Card>
        </div>
      )}

      {/* Student Profile Modals */}
      {editingStudent && (
        <EditStudentModal 
          student={editingStudent} 
          onClose={() => setEditingStudent(null)} 
          onSave={handleStudentEditSave}
        />
      )}

      {deletingStudent && (
        <DeleteConfirmModal 
          student={deletingStudent} 
          onClose={() => setDeletingStudent(null)} 
          onConfirm={handleStudentDeleteConfirm}
        />
      )}
    </div>
  );
};

export default Records;
