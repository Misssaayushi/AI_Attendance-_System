import React from 'react';
import { AlertTriangle, Trash2, X } from 'lucide-react';

const DeleteConfirmModal = ({ student, onClose, onConfirm }) => {
  if (!student) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-gray-900 border border-red-500/30 rounded-2xl w-full max-w-md overflow-hidden shadow-[0_0_40px_rgba(239,68,68,0.15)] flex flex-col">
        <div className="p-6 text-center pt-8">
          <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle size={32} className="text-red-500" />
          </div>
          
          <h2 className="text-xl font-bold text-white mb-2">Delete Student Record?</h2>
          <p className="text-gray-400 text-sm px-4">
            You are about to permanently delete <strong className="text-white">{student.first_name} {student.last_name}</strong> (Roll: {student.roll_number}). This action cannot be undone and will remove all associated attendance data.
          </p>
        </div>

        <div className="p-6 pt-2 pb-8 flex justify-center gap-3">
          <button 
            onClick={onClose} 
            className="px-6 py-2.5 text-sm font-bold text-gray-300 hover:text-white bg-gray-800 rounded-lg transition-colors border border-gray-700 w-full"
          >
            Cancel
          </button>
          <button 
            onClick={() => onConfirm(student.id)} 
            className="flex items-center justify-center gap-2 px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white text-sm font-bold rounded-lg shadow-lg shadow-red-500/20 transition-all w-full"
          >
            <Trash2 size={16} /> Delete Student
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmModal;
