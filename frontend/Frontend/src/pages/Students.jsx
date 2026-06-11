import { useState, useEffect, useMemo } from 'react';
import { Search, ChevronLeft, ChevronRight, Filter, Edit, Trash2, Users, Calendar, Download } from 'lucide-react';
import Container from '../components/Container';
import Card from '../components/Card';
import { listStudents } from '../services/api';
import { extractData } from '../services/apiHelpers';
import { useToast } from '../context/ToastContext';

const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = (err) => reject(err);
    document.body.appendChild(script);
  });
};

const formatArrivalTime = (timeStr) => {
  if (!timeStr) return '—';
  const parts = timeStr.split(':');
  if (parts.length < 2) return timeStr;
  const hour = parseInt(parts[0], 10);
  const min = parts[1];
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${min} ${ampm}`;
};

const getTodayStatusBadge = (status) => {
  if (!status) {
    return (
      <span className="px-2 py-1 rounded-lg text-[10px] font-bold uppercase border bg-gray-800/80 text-gray-500 border-gray-700/50">
        Not Marked
      </span>
    );
  }

  const normalizedStatus = status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();

  const colors = {
    Present: 'bg-green-500/10 text-green-400 border-green-500/20',
    Late: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    Absent: 'bg-red-500/10 text-red-400 border-red-500/20',
  };

  return (
    <span className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase border ${colors[normalizedStatus] || 'bg-gray-800/80 text-gray-500 border-gray-700/50'}`}>
      {normalizedStatus}
    </span>
  );
};

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const { addToast } = useToast();

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const params = { page: 1, page_size: 100 };
      if (selectedDate) params.date = selectedDate;
      const response = await listStudents(params);
      const data = extractData(response);
      setStudents(data?.items || []);
    } catch (err) {
      console.error('Failed to load students:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [selectedDate]);

  // Filter and Search Logic
  const filteredStudents = useMemo(() => {
    return students.filter(student => {
      const matchesSearch = 
        student.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        student.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        student.roll_number.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesDept = selectedDept === 'All' || student.department === selectedDept;

      return matchesSearch && matchesDept;
    });
  }, [students, searchQuery, selectedDept]);

  // Pagination Details
  const totalPages = Math.ceil(filteredStudents.length / itemsPerPage) || 1;
  
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  const paginatedStudents = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredStudents.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredStudents, currentPage]);

  const exportToExcel = async () => {
    if (!filteredStudents.length) {
      if (addToast) addToast('No students to export', 'error');
      return;
    }

    if (addToast) addToast('Generating Excel file...', 'info');

    try {
      await loadScript('https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js');
      
      const ExcelJS = window.ExcelJS;
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('Students');

      // Define columns
      worksheet.columns = [
        { header: 'First Name', key: 'first_name', width: 15 },
        { header: 'Last Name', key: 'last_name', width: 15 },
        { header: 'Email', key: 'email', width: 25 },
        { header: 'Roll Number', key: 'roll_number', width: 15 },
        { header: 'Department', key: 'department', width: 15 },
        { header: 'Year', key: 'year_batch', width: 15 },
        { header: 'Semester', key: 'semester', width: 10 },
        { header: 'Status', key: 'status', width: 15 },
        { header: 'Arrival Time', key: 'arrival_time', width: 15 }
      ];

      // Format headers
      const headerRow = worksheet.getRow(1);
      headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
      headerRow.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FF1E293B' } // slate-800
      };

      // Add rows
      filteredStudents.forEach(s => {
        const row = worksheet.addRow({
          first_name: s.first_name || '',
          last_name: s.last_name || '',
          email: s.email || '',
          roll_number: s.roll_number || '',
          department: s.department || '',
          year_batch: s.year_batch || '',
          semester: s.semester || '',
          status: s.status ? (s.status.charAt(0).toUpperCase() + s.status.slice(1).toLowerCase()) : 'Not Marked',
          arrival_time: formatArrivalTime(s.arrival_time)
        });

        // Color status cell
        const statusCell = row.getCell('status');
        const statusVal = (s.status || '').toLowerCase();
        if (statusVal === 'present') {
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFE6FFED' } // light green
          };
          statusCell.font = { color: { argb: 'FF147D36' }, bold: true };
        } else if (statusVal === 'late') {
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFEF3C7' } // light yellow
          };
          statusCell.font = { color: { argb: 'FFB45309' }, bold: true };
        } else if (statusVal === 'absent') {
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFEE2E2' } // light red
          };
          statusCell.font = { color: { argb: 'FFB91C1C' }, bold: true };
        }
      });

      // Write buffer
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `students_export_${selectedDate || 'all'}.xlsx`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      if (addToast) addToast('Exported to Excel successfully', 'success');
    } catch (error) {
      console.error('Excel export failed:', error);
      if (addToast) addToast('Failed to export to Excel', 'error');
    }
  };

  // Removed student update/delete handlers

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-gray-100 flex flex-col font-sans">
      <Container className="py-8 flex-1 flex flex-col">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Users className="text-blue-500" size={32} />
              Student Management
            </h1>
            <p className="text-gray-400 mt-1 font-medium">View, edit, and manage all enrolled students.</p>
          </div>
        </div>

        <Card className="p-0 flex-1 overflow-hidden border border-gray-800/80 bg-gray-900/40 flex flex-col">
          {/* Controls */}
          <div className="p-5 border-b border-gray-800/80 bg-gray-900/20 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="relative max-w-sm w-full">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
                  <Search size={14} />
                </span>
                <input 
                  type="text"
                  placeholder="Search by name or roll number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-850/50 border border-gray-800/80 rounded-xl py-2 pl-9 pr-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-colors"
                />
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" size={14} />
                  <input 
                    type="date"
                    value={selectedDate}
                    onChange={(e) => { setSelectedDate(e.target.value); setCurrentPage(1); }}
                    className="w-full md:w-auto pl-9 pr-4 py-1.5 bg-gray-850/50 border border-gray-800/85 rounded-lg text-xs text-gray-300 focus:outline-none focus:border-blue-500/50 appearance-none cursor-pointer"
                  />
                </div>

                <div className="flex items-center space-x-1.5 text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                  <Filter size={12} className="text-gray-500" />
                  <span>Department:</span>
                  <select 
                    value={selectedDept} 
                    onChange={(e) => { setSelectedDept(e.target.value); setCurrentPage(1); }}
                    className="bg-gray-850/50 border border-gray-800/85 text-[10px] text-gray-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500/50 ml-1"
                  >
                    <option value="All">All Departments</option>
                    <option value="CS">Computer Science</option>
                    <option value="IT">Information Tech</option>
                    <option value="ME">Mechanical</option>
                    <option value="EE">Electrical</option>
                  </select>
                </div>

                <button
                  onClick={exportToExcel}
                  className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-lg transition-colors ml-auto sm:ml-2"
                >
                  <Download size={14} />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Export Excel</span>
                </button>
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto relative flex-1 min-h-[300px]">
            {loading && (
              <div className="absolute inset-0 bg-gray-900/60 flex items-center justify-center z-10">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            )}
            <table className="min-w-full divide-y divide-gray-800">
              <thead className="bg-gray-900/30">
                <tr>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Student</th>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Roll Number</th>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Department</th>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Year/Sem</th>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Status</th>
                  <th className="px-6 py-4 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Arrival Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 bg-transparent">
                {!loading && paginatedStudents.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-sm text-gray-500 italic">
                      No students found.
                    </td>
                  </tr>
                ) : (
                  paginatedStudents.map((student) => (
                    <tr key={student.id} className="hover:bg-gray-850/20 transition-colors group">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold text-sm border border-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                            {student.first_name[0]}{student.last_name[0]}
                          </div>
                          <div>
                            <span className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors block">
                              {student.first_name} {student.last_name}
                            </span>
                            <span className="text-[10px] text-gray-500 block mt-0.5">{student.email}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-400">
                        {student.roll_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 bg-gray-800/80 border border-gray-700/50 rounded-lg text-xs font-bold text-gray-400 uppercase tracking-wider">
                          {student.department}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-400">
                        {student.year_batch} / Sem {student.semester}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getTodayStatusBadge(student.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-400">
                        {formatArrivalTime(student.arrival_time)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-gray-800/80 bg-gray-900/20 flex items-center justify-between">
              <p className="text-[10px] text-gray-500 font-semibold uppercase">
                Page {currentPage} of {totalPages}
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
      </Container>

      {/* Removed modals */}
    </div>
  );
};

export default Students;
