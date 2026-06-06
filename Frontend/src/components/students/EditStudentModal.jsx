import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const EditStudentModal = ({ student, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    roll_number: '',
    department: '',
    course: '',
    year_batch: '',
    semester: 1,
    contact_number: '',
    gender: 'Other'
  });

  useEffect(() => {
    if (student) {
      setFormData({
        first_name: student.first_name || '',
        last_name: student.last_name || '',
        email: student.email || '',
        roll_number: student.roll_number || '',
        department: student.department || '',
        course: student.course || '',
        year_batch: student.year_batch || '',
        semester: student.semester || 1,
        contact_number: student.contact_number || '',
        gender: student.gender || 'Other'
      });
    }
  }, [student]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: name === 'semester' ? parseInt(value) || 1 : value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(student.id, formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        <div className="p-5 border-b border-gray-800 flex items-center justify-between bg-gray-800/50">
          <h2 className="text-lg font-bold text-white">Edit Student Record</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded-full text-gray-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto custom-scrollbar">
          <form id="edit-student-form" onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">First Name</label>
                <input required type="text" name="first_name" value={formData.first_name} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Last Name</label>
                <input required type="text" name="last_name" value={formData.last_name} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Roll Number</label>
                <input required type="text" name="roll_number" value={formData.roll_number} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Email</label>
                <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Department</label>
                <input required type="text" name="department" value={formData.department} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Course</label>
                <input required type="text" name="course" value={formData.course} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Batch Year</label>
                <input required type="text" name="year_batch" value={formData.year_batch} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Semester</label>
                <input required type="number" min="1" max="8" name="semester" value={formData.semester} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">Gender</label>
                <select name="gender" value={formData.gender} onChange={handleChange} className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 transition-colors">
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl mt-4">
              <p className="text-xs text-blue-400">
                <strong>Note:</strong> If you change the student's name, their face encoding file name will not automatically change on disk until Part 5 is implemented. DB will be updated successfully.
              </p>
            </div>
          </form>
        </div>

        <div className="p-5 border-t border-gray-800 bg-gray-800/30 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-5 py-2.5 text-sm font-bold text-gray-300 hover:text-white transition-colors">
            Cancel
          </button>
          <button type="submit" form="edit-student-form" className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold rounded-lg shadow-lg shadow-blue-500/20 transition-all">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditStudentModal;
