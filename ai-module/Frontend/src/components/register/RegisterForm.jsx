import React from 'react';
import Button from '../Button';

const RegisterForm = ({ formData, errors, onChange, onSubmit, onReset, isDisabled }) => {
  const inputClasses = (id) => `mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5 transition-all ${errors[id] ? 'border-red-500 ring-1 ring-red-500' : ''}`;
  const labelClasses = "block text-sm font-medium text-gray-300";

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className={`space-y-6 ${isDisabled ? 'opacity-50 pointer-events-none' : ''}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Info */}
        <div>
          <label htmlFor="fullName" className={labelClasses}>Full Name</label>
          <input 
            type="text" id="fullName" value={formData.fullName} 
            onChange={onChange} className={inputClasses('fullName')} 
            placeholder="John Doe" 
          />
          {errors.fullName && <p className="mt-1 text-xs text-red-400">{errors.fullName}</p>}
        </div>

        <div>
          <label htmlFor="studentId" className={labelClasses}>Roll Number / Student ID</label>
          <input 
            type="text" id="studentId" value={formData.studentId} 
            onChange={onChange} className={inputClasses('studentId')} 
            placeholder="STU-12345" 
          />
          {errors.studentId && <p className="mt-1 text-xs text-red-400">{errors.studentId}</p>}
        </div>

        <div>
          <label htmlFor="email" className={labelClasses}>Email Address</label>
          <input 
            type="email" id="email" value={formData.email} 
            onChange={onChange} className={inputClasses('email')} 
            placeholder="john@university.edu" 
          />
          {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email}</p>}
        </div>

        <div>
          <label htmlFor="contactNumber" className={labelClasses}>Contact Number</label>
          <input 
            type="tel" id="contactNumber" value={formData.contactNumber} 
            onChange={onChange} className={inputClasses('contactNumber')} 
            placeholder="+1 234 567 890" 
          />
        </div>

        {/* Academic Info */}
        <div>
          <label htmlFor="department" className={labelClasses}>Department</label>
          <select id="department" value={formData.department} onChange={onChange} className={inputClasses('department')}>
            <option value="">Select Department</option>
            <option value="CS">Computer Science</option>
            <option value="IT">Information Technology</option>
            <option value="ME">Mechanical Engineering</option>
            <option value="EE">Electrical Engineering</option>
          </select>
          {errors.department && <p className="mt-1 text-xs text-red-400">{errors.department}</p>}
        </div>

        <div>
          <label htmlFor="course" className={labelClasses}>Course</label>
          <input type="text" id="course" value={formData.course} onChange={onChange} className={inputClasses('course')} placeholder="e.g. B.Tech" />
        </div>

        <div>
          <label htmlFor="batch" className={labelClasses}>Year / Batch</label>
          <select id="batch" value={formData.batch} onChange={onChange} className={inputClasses('batch')}>
            <option value="">Select Batch</option>
            <option value="2022">2022-2026</option>
            <option value="2023">2023-2027</option>
            <option value="2024">2024-2028</option>
          </select>
        </div>

        <div>
          <label htmlFor="semester" className={labelClasses}>Semester</label>
          <select id="semester" value={formData.semester} onChange={onChange} className={inputClasses('semester')}>
            <option value="">Select Semester</option>
            {[1, 2, 3, 4, 5, 6, 7, 8].map(sem => (
              <option key={sem} value={sem}>Semester {sem}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="section" className={labelClasses}>Section</label>
          <input type="text" id="section" value={formData.section} onChange={onChange} className={inputClasses('section')} placeholder="e.g. A" />
        </div>

        <div>
          <label htmlFor="gender" className={labelClasses}>Gender</label>
          <select id="gender" value={formData.gender} onChange={onChange} className={inputClasses('gender')}>
            <option value="">Select Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row justify-end gap-4 pt-6 border-t border-gray-700">
        <Button variant="outline" type="button" onClick={onReset} className="w-full sm:w-auto border-red-500/50 text-red-400 hover:bg-red-500/10">
          Reset Form
        </Button>
        <Button type="submit" className="w-full sm:w-auto px-10">
          Submit Registration
        </Button>
      </div>
    </form>
  );
};

export default RegisterForm;
