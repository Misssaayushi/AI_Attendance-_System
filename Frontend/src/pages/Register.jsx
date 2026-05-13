import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Container from '../components/Container';
import { User, Camera, CheckCircle } from 'lucide-react';

const Register = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    fullName: '',
    studentId: '',
    email: '',
    contactNumber: '',
    department: '',
    batch: '',
    semester: '',
    section: '',
    gender: '',
    course: ''
  });

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const nextStep = () => setCurrentStep(prev => prev + 1);
  const prevStep = () => setCurrentStep(prev => prev - 1);

  const inputClasses = "mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2.5";
  const labelClasses = "block text-sm font-medium text-gray-300";

  return (
    <Container className="py-10">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">Student Registration</h1>
          <p className="text-gray-400">Step {currentStep} of 3: {currentStep === 1 ? 'Personal Details' : currentStep === 2 ? 'Biometric Capture' : 'Review & Submit'}</p>
        </div>

        {/* Stepper Indicator */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-700'} text-white`}>
            <User size={20} />
          </div>
          <div className={`h-1 w-12 ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-700'}`}></div>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-700'} text-white`}>
            <Camera size={20} />
          </div>
          <div className={`h-1 w-12 ${currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-700'}`}></div>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-700'} text-white`}>
            <CheckCircle size={20} />
          </div>
        </div>

        {/* Step 1: Student Details */}
        {currentStep === 1 && (
          <Card className="p-8">
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Row 1 */}
                <div>
                  <label htmlFor="fullName" className={labelClasses}>Full Name</label>
                  <input type="text" id="fullName" value={formData.fullName} onChange={handleChange} className={inputClasses} placeholder="John Doe" required />
                </div>
                <div>
                  <label htmlFor="studentId" className={labelClasses}>Student ID</label>
                  <input type="text" id="studentId" value={formData.studentId} onChange={handleChange} className={inputClasses} placeholder="STU-12345" required />
                </div>

                {/* Row 2 */}
                <div>
                  <label htmlFor="email" className={labelClasses}>Email Address</label>
                  <input type="email" id="email" value={formData.email} onChange={handleChange} className={inputClasses} placeholder="john@university.edu" required />
                </div>
                <div>
                  <label htmlFor="contactNumber" className={labelClasses}>Contact Number</label>
                  <input type="tel" id="contactNumber" value={formData.contactNumber} onChange={handleChange} className={inputClasses} placeholder="+1 234 567 890" />
                </div>

                {/* Row 3 */}
                <div>
                  <label htmlFor="department" className={labelClasses}>Department</label>
                  <select id="department" value={formData.department} onChange={handleChange} className={inputClasses}>
                    <option value="">Select Department</option>
                    <option value="CS">Computer Science</option>
                    <option value="IT">Information Technology</option>
                    <option value="ME">Mechanical Engineering</option>
                    <option value="EE">Electrical Engineering</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="batch" className={labelClasses}>Year / Batch</label>
                  <select id="batch" value={formData.batch} onChange={handleChange} className={inputClasses}>
                    <option value="">Select Batch</option>
                    <option value="2022">2022-2026</option>
                    <option value="2023">2023-2027</option>
                    <option value="2024">2024-2028</option>
                  </select>
                </div>

                {/* Row 4 */}
                <div>
                  <label htmlFor="semester" className={labelClasses}>Semester</label>
                  <select id="semester" value={formData.semester} onChange={handleChange} className={inputClasses}>
                    <option value="">Select Semester</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(sem => (
                      <option key={sem} value={sem}>Semester {sem}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="gender" className={labelClasses}>Gender</label>
                  <select id="gender" value={formData.gender} onChange={handleChange} className={inputClasses}>
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Row 5 */}
                <div>
                  <label htmlFor="course" className={labelClasses}>Course</label>
                  <input type="text" id="course" value={formData.course} onChange={handleChange} className={inputClasses} placeholder="e.g. B.Tech" />
                </div>
                <div>
                  <label htmlFor="section" className={labelClasses}>Section</label>
                  <input type="text" id="section" value={formData.section} onChange={handleChange} className={inputClasses} placeholder="e.g. A" />
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={nextStep} type="button">Next: Face Capture</Button>
              </div>
            </form>
          </Card>
        )}

        {/* Step 2: Placeholder for Capture */}
        {currentStep === 2 && (
          <Card className="p-8 flex flex-col items-center space-y-6">
             <div className="w-full aspect-video bg-black rounded-lg flex flex-col items-center justify-center border-2 border-dashed border-gray-600 relative">
                <Camera size={48} className="text-gray-600 mb-4" />
                <p className="text-gray-500">Camera Interface (Step 4)</p>
                <div className="absolute inset-0 border-[3px] border-blue-500/30 rounded-lg m-12 pointer-events-none border-dashed"></div>
             </div>
             <div className="flex space-x-4 w-full justify-between">
                <Button variant="secondary" onClick={prevStep}>Back</Button>
                <Button onClick={nextStep}>Capture & Continue</Button>
             </div>
          </Card>
        )}

        {/* Step 3: Placeholder for Review */}
        {currentStep === 3 && (
          <Card className="p-8 text-center space-y-6">
             <CheckCircle size={64} className="text-green-500 mx-auto" />
             <h2 className="text-2xl font-bold">Review Details</h2>
             <p className="text-gray-400">Verify your information before submitting (Step 5)</p>
             <div className="flex space-x-4 justify-between pt-8">
                <Button variant="secondary" onClick={prevStep}>Back</Button>
                <Button>Submit Registration</Button>
             </div>
          </Card>
        )}
      </div>
    </Container>
  );
};

export default Register;
