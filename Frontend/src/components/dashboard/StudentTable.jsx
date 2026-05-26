import React, { useState, useMemo } from 'react';
import { Search, ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import Card from '../Card';

const mockStudents = [
  { id: 1, name: 'Rahul Sharma', roll: 'STU-2026-042', dept: 'CS', rate: 88, status: 'Present' },
  { id: 2, name: 'Aman Verma', roll: 'STU-2026-015', dept: 'IT', rate: 92, status: 'Late' },
  { id: 3, name: 'Priya Patel', roll: 'STU-2026-103', dept: 'ME', rate: 78, status: 'Absent' },
  { id: 4, name: 'Rohit Gupta', roll: 'STU-2026-089', dept: 'EE', rate: 85, status: 'Present' },
  { id: 5, name: 'Neha Sharma', roll: 'STU-2026-056', dept: 'CS', rate: 95, status: 'Present' },
  { id: 6, name: 'Shreya Sen', roll: 'STU-2026-121', dept: 'IT', rate: 80, status: 'Present' },
  { id: 7, name: 'Karan Malhotra', roll: 'STU-2026-004', dept: 'ME', rate: 75, status: 'Absent' },
  { id: 8, name: 'Rohan Das', roll: 'STU-2026-077', dept: 'CS', rate: 90, status: 'Present' },
  { id: 9, name: 'Aditya Roy', roll: 'STU-2026-031', dept: 'EE', rate: 82, status: 'Late' },
  { id: 10, name: 'Sneha Patil', roll: 'STU-2026-092', dept: 'IT', rate: 89, status: 'Present' }
];

const StudentTable = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // Filter and Search Logic
  const filteredStudents = useMemo(() => {
    return mockStudents.filter(student => {
      const matchesSearch = 
        student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        student.roll.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesDept = selectedDept === 'All' || student.dept === selectedDept;
      const matchesStatus = selectedStatus === 'All' || student.status === selectedStatus;

      return matchesSearch && matchesDept && matchesStatus;
    });
  }, [searchQuery, selectedDept, selectedStatus]);

  // Pagination Details
  const totalPages = Math.ceil(filteredStudents.length / itemsPerPage) || 1;
  
  // Adjust current page if filters reduce available results
  React.useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  const paginatedStudents = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredStudents.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredStudents, currentPage]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Present':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-500/10 text-green-400 border border-green-500/20">Present</span>;
      case 'Late':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">Late</span>;
      case 'Absent':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">Absent</span>;
      default:
        return null;
    }
  };

  const getRateColor = (rate) => {
    if (rate >= 90) return 'text-green-400';
    if (rate >= 80) return 'text-blue-400';
    return 'text-yellow-400';
  };

  return (
    <Card className="p-0 overflow-hidden border border-gray-800/80 bg-gray-900/40">
      {/* Table Header Controls */}
      <div className="p-5 border-b border-gray-800/80 bg-gray-900/20 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Attendance Register</h3>
            <p className="text-[10px] text-gray-500 mt-0.5">Enrolled student logs and daily verification status</p>
          </div>
          
          {/* Search bar */}
          <div className="relative max-w-xs w-full">
            <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
              <Search size={14} />
            </span>
            <input 
              type="text"
              placeholder="Search student or roll number..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-gray-850/50 border border-gray-800/80 rounded-xl py-2 pl-9 pr-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50 transition-colors"
            />
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-1.5 text-[10px] text-gray-400 font-bold uppercase tracking-wider">
            <Filter size={12} className="text-gray-500" />
            <span>Filters:</span>
          </div>

          {/* Department Filter */}
          <select 
            value={selectedDept} 
            onChange={(e) => { setSelectedDept(e.target.value); setCurrentPage(1); }}
            className="bg-gray-850/50 border border-gray-800/85 text-[10px] text-gray-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500/50"
          >
            <option value="All">All Departments</option>
            <option value="CS">Computer Science</option>
            <option value="IT">Information Tech</option>
            <option value="ME">Mechanical</option>
            <option value="EE">Electrical</option>
          </select>

          {/* Status Filter */}
          <select 
            value={selectedStatus} 
            onChange={(e) => { setSelectedStatus(e.target.value); setCurrentPage(1); }}
            className="bg-gray-850/50 border border-gray-800/85 text-[10px] text-gray-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500/50"
          >
            <option value="All">All Statuses</option>
            <option value="Present">Present</option>
            <option value="Late">Late</option>
            <option value="Absent">Absent</option>
          </select>
        </div>
      </div>

      {/* Table grid */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-900/30">
            <tr>
              <th className="px-6 py-3.5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Student Name</th>
              <th className="px-6 py-3.5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Roll Number</th>
              <th className="px-6 py-3.5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Department</th>
              <th className="px-6 py-3.5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Attendance %</th>
              <th className="px-6 py-3.5 text-left text-[10px] font-black text-gray-500 uppercase tracking-widest">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60 bg-transparent">
            {paginatedStudents.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-xs text-gray-500 italic">
                  No records found matching filters
                </td>
              </tr>
            ) : (
              paginatedStudents.map((student) => (
                <tr key={student.id} className="hover:bg-gray-850/20 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 font-bold text-xs border border-blue-500/20 group-hover:scale-105 transition-transform duration-200">
                        {student.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="text-xs font-bold text-white group-hover:text-blue-400 transition-colors">
                        {student.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-400">
                    {student.roll}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 bg-gray-800/80 border border-gray-700/50 rounded-lg text-[9px] font-bold text-gray-400 uppercase tracking-wider">
                      {student.dept}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <span className={`text-xs font-bold font-mono min-w-[32px] ${getRateColor(student.rate)}`}>
                        {student.rate}%
                      </span>
                      <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden hidden sm:block">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${
                            student.rate >= 90 ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' :
                            student.rate >= 80 ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.4)]' :
                            'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.4)]'
                          }`}
                          style={{ width: `${student.rate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(student.status)}
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
  );
};

export default StudentTable;
