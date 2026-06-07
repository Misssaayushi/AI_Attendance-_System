import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Plus, Trash2, Edit2, AlertCircle } from 'lucide-react';
import { listClassTimings, upsertClassTiming, deleteClassTiming } from '../services/api';
import { useToast } from '../context/ToastContext';
import Container from '../components/Container';

const Settings = () => {
  const [timings, setTimings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTiming, setEditingTiming] = useState(null);
  const { addToast } = useToast();

  const [formData, setFormData] = useState({
    department: '',
    semester: '',
    class_start_time: '08:00:00',
    class_end_time: '16:00:00',
    present_cutoff: '09:00:00',
    late_cutoff: '11:30:00'
  });

  const fetchTimings = async () => {
    try {
      setLoading(true);
      const res = await listClassTimings();
      setTimings(res.data.data.items);
    } catch (error) {
      addToast('Failed to fetch class timings', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimings();
  }, []);

  const handleOpenModal = (timing = null) => {
    if (timing) {
      setEditingTiming(timing);
      setFormData({
        department: timing.department || '',
        semester: timing.semester || '',
        class_start_time: timing.class_start_time,
        class_end_time: timing.class_end_time,
        present_cutoff: timing.present_cutoff,
        late_cutoff: timing.late_cutoff
      });
    } else {
      setEditingTiming(null);
      setFormData({
        department: '',
        semester: '',
        class_start_time: '08:00:00',
        class_end_time: '16:00:00',
        present_cutoff: '09:00:00',
        late_cutoff: '11:30:00'
      });
    }
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        department: formData.department === '' ? null : formData.department,
        semester: formData.semester === '' ? null : parseInt(formData.semester)
      };
      
      await upsertClassTiming(payload);
      addToast('Class timing rule saved successfully', 'success');
      setShowModal(false);
      fetchTimings();
    } catch (error) {
      let msg = error.response?.data?.message || 'Failed to save class timing rule';
      if (error.response?.data?.error_type === 'ValidationError' && error.response?.data?.details?.errors) {
        msg = error.response.data.details.errors.map(e => `${e.field}: ${e.message}`).join(', ');
      }
      addToast(msg, 'error');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        await deleteClassTiming(id);
        addToast('Rule deleted successfully', 'success');
        fetchTimings();
      } catch (error) {
        addToast('Failed to delete rule', 'error');
      }
    }
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return '';
    // timeStr is like "08:00:00"
    const [h, m] = timeStr.split(':');
    let hours = parseInt(h);
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${hours}:${m} ${ampm}`;
  };

  return (
    <Container title="Settings" subtitle="System Configuration" icon={SettingsIcon}>
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden mb-6">
        <div className="p-6 border-b border-gray-800 flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-white">Class Timings & Attendance Rules</h3>
            <p className="text-gray-400 text-sm mt-1">Configure when students are marked Present, Late, or Absent.</p>
          </div>
          <button 
            onClick={() => handleOpenModal()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Plus size={18} />
            <span>Add Rule</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-800/50 border-b border-gray-800">
                <th className="py-3 px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider">Group</th>
                <th className="py-3 px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider">Class Window</th>
                <th className="py-3 px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider">Present Cutoff</th>
                <th className="py-3 px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider">Late Cutoff</th>
                <th className="py-3 px-6 text-xs font-semibold text-gray-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-gray-500">Loading rules...</td>
                </tr>
              ) : timings.length === 0 ? (
                <tr>
                  <td colSpan="5" className="py-8 text-center text-gray-500">
                    <div className="flex flex-col items-center">
                      <AlertCircle className="w-8 h-8 mb-2 opacity-50" />
                      <p>No class timing rules found. System is using hardcoded defaults (9:00 AM / 11:30 AM).</p>
                    </div>
                  </td>
                </tr>
              ) : (
                timings.map(t => (
                  <tr key={t.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-4 px-6">
                      {t.department === null && t.semester === null ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                          Global Default
                        </span>
                      ) : (
                        <div className="flex flex-col">
                          <span className="font-medium text-white">{t.department || 'All Depts'}</span>
                          <span className="text-xs text-gray-400">Sem {t.semester || 'All'}</span>
                        </div>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      <div className="text-sm text-gray-300">
                        {formatTime(t.class_start_time)} - {formatTime(t.class_end_time)}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="text-sm font-medium text-green-400">{formatTime(t.present_cutoff)}</span>
                    </td>
                    <td className="py-4 px-6">
                      <span className="text-sm font-medium text-yellow-400">{formatTime(t.late_cutoff)}</span>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex justify-end gap-3">
                        <button 
                          onClick={() => handleOpenModal(t)}
                          className="text-gray-400 hover:text-blue-400 transition-colors"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(t.id)}
                          className="text-gray-400 hover:text-red-400 transition-colors"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center bg-gray-800/30">
              <h3 className="text-lg font-semibold text-white">
                {editingTiming ? 'Edit Timing Rule' : 'New Timing Rule'}
              </h3>
              <button 
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Department</label>
                  <select 
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  >
                    <option value="">Global (All)</option>
                    <option value="CS">Computer Science (CS)</option>
                    <option value="IT">Information Technology (IT)</option>
                    <option value="EC">Electronics (EC)</option>
                    <option value="ME">Mechanical (ME)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Semester</label>
                  <select 
                    value={formData.semester}
                    onChange={(e) => setFormData({...formData, semester: e.target.value})}
                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  >
                    <option value="">Global (All)</option>
                    {[1,2,3,4,5,6,7,8].map(sem => (
                      <option key={sem} value={sem}>Semester {sem}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <p className="text-xs text-blue-300">
                  Leave both blank to set the <strong>Global Default</strong> rule, which applies when no specific rule matches.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Class Start Time</label>
                  <input 
                    type="time" 
                    step="1"
                    required
                    value={formData.class_start_time}
                    onChange={(e) => setFormData({...formData, class_start_time: e.target.value})}
                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Class End Time</label>
                  <input 
                    type="time" 
                    step="1"
                    required
                    value={formData.class_end_time}
                    onChange={(e) => setFormData({...formData, class_end_time: e.target.value})}
                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Present Cutoff</label>
                  <input 
                    type="time" 
                    step="1"
                    required
                    value={formData.present_cutoff}
                    onChange={(e) => setFormData({...formData, present_cutoff: e.target.value})}
                    className="w-full bg-gray-950 border border-green-500/30 rounded-lg px-3 py-2 text-sm text-white focus:border-green-500 focus:ring-1 focus:ring-green-500 outline-none"
                  />
                  <p className="text-[10px] text-gray-500 mt-1">Before this = Present</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1">Late Cutoff</label>
                  <input 
                    type="time" 
                    step="1"
                    required
                    value={formData.late_cutoff}
                    onChange={(e) => setFormData({...formData, late_cutoff: e.target.value})}
                    className="w-full bg-gray-950 border border-yellow-500/30 rounded-lg px-3 py-2 text-sm text-white focus:border-yellow-500 focus:ring-1 focus:ring-yellow-500 outline-none"
                  />
                  <p className="text-[10px] text-gray-500 mt-1">Before this = Late</p>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-800 mt-6">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Save Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Container>
  );
};

export default Settings;
