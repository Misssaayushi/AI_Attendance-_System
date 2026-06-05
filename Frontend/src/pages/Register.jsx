import React, { useState } from 'react';
import Card from '../components/Card';
import Container from '../components/Container';
import WebcamFeed from '../components/register/WebcamFeed';
import RegisterForm from '../components/register/RegisterForm';
import Alert from '../components/ui/Alert';
import { createStudent, registerFace, triggerEncoding } from '../services/api';
import { extractData, extractErrorMessage } from '../services/apiHelpers';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const Register = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [isFaceCaptured, setIsFaceCaptured] = useState(false);
  const [alert, setAlert] = useState(null);
  const [webcamKey, setWebcamKey] = useState(0);
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
  const [errors, setErrors] = useState({});


  const handleCapture = (imageData) => {
    setCapturedImage(imageData);
    setIsFaceCaptured(!!imageData);
    if (imageData) {
      setAlert({ variant: 'success', message: 'Faces captured successfully! Please fill in the details below.' });
    } else {
      setAlert(null);
    }
  };

  const handleInputChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
    // Clear error when user starts typing
    if (errors[id]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[id];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.fullName) newErrors.fullName = "Full Name is required";
    if (!formData.studentId) newErrors.studentId = "Student ID is required";
    if (!formData.email) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Invalid email format";
    if (!formData.department) newErrors.department = "Department is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      setAlert({ variant: 'error', message: 'Please correct the highlighted errors.' });
      return;
    }

    if (!isFaceCaptured) {
      setAlert({ variant: 'error', message: 'Please capture your face first.' });
      return;
    }

    try {
      setAlert({ variant: 'info', message: 'Registering student... please wait.' });

      // Split fullName into first_name + last_name
      const nameParts = formData.fullName.trim().split(' ');
      const firstName = nameParts[0];
      const lastName = nameParts.slice(1).join(' ') || nameParts[0];

      const payload = {
        first_name: firstName,
        last_name: lastName,
        email: formData.email,
        roll_number: formData.studentId,
        contact_number: formData.contactNumber || null,
        department: formData.department,
        course: formData.course,
        year_batch: formData.batch,
        semester: formData.semester ? parseInt(formData.semester) : null,
        section: formData.section || null,
        gender: formData.gender,
      };

      const response = await createStudent(payload);
      const studentData = response.data.data || extractData(response);
      const studentId = studentData.id || studentData.student_id;

      if (studentId) {
        setAlert({ variant: 'info', message: 'Student created. Saving face images...' });
        await registerFace(studentId, capturedImage);

        setAlert({ variant: 'info', message: 'Triggering AI model encoding...' });
        try {
          await triggerEncoding(studentId);
        } catch (encodeErr) {
          console.warn('Encoding trigger failed or timed out:', encodeErr);
          // Don't fail the whole registration if just encoding failed/timed out
        }

        setAlert({ variant: 'success', message: 'Registration Successful! Student dataset created. Ready for next student.' });
        setTimeout(() => {
          handleReset();
          setAlert(null);
        }, 3000);
      } else {
        throw new Error("Failed to retrieve student ID after creation.");
      }
    } catch (error) {
      console.error('Registration error:', error);
      setAlert({
        variant: 'error',
        message: extractErrorMessage(error)
      });
    }
  };

  const handleReset = () => {
    setFormData({
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
    setErrors({});
    setCapturedImage(null);
    setIsFaceCaptured(false);
    setWebcamKey(prev => prev + 1);
  };

  const handleError = (msg) => {
    setAlert({ variant: 'error', message: msg });
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-gray-100 font-sans">
      <Container className="py-12">
        {/* Back Button */}
        <Link to="/" className="text-cyan-500 hover:text-cyan-400 flex items-center gap-2 text-xs font-mono uppercase tracking-widest transition-colors mb-6 w-max">
          <ArrowLeft size={14} /> Back to Hub
        </Link>

        <div className="max-w-4xl mx-auto space-y-8">
          {/* Page Heading */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">Student Enrollment</h1>
            <p className="text-gray-400">Capture face and enter details to register in the AI system.</p>
          </div>
        </div>
        {alert && <Alert variant={alert.variant} message={alert.message} onClose={() => setAlert(null)} />}

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left: Webcam Section */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <span className="w-8 h-8 bg-blue-600/20 text-blue-500 rounded-full flex items-center justify-center text-sm">1</span>
              Face Capture
            </h2>
            <WebcamFeed
              key={webcamKey}
              onCapture={handleCapture}
              onError={handleError}
            />

            <Card className="bg-blue-500/5 border-blue-500/20 p-4">
              <h4 className="text-sm font-semibold text-blue-400 mb-2">Instructions:</h4>
              <ul className="text-xs text-gray-400 space-y-2 list-disc pl-4">
                <li>Ensure neutral lighting on your face.</li>
                <li>Position your face within the frame guide.</li>
                <li>Remove glasses or hats if possible.</li>
                <li>Click 'Capture Face' once positioned.</li>
              </ul>
            </Card>
          </div>

          {/* Right: Form Section */}
          <div className="lg:col-span-3 space-y-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <span className="w-8 h-8 bg-blue-600/20 text-blue-500 rounded-full flex items-center justify-center text-sm">2</span>
              Student Details
            </h2>
            <Card className="p-6 sm:p-8">
              <RegisterForm
                formData={formData}
                errors={errors}
                onChange={handleInputChange}
                onSubmit={handleSubmit}
                onReset={handleReset}
                isDisabled={!isFaceCaptured}
              />
              {!isFaceCaptured && (
                <div className="mt-4 p-3 bg-gray-900/50 rounded-lg text-center">
                  <p className="text-xs text-gray-500 italic">Please capture your face to unlock the details form.</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default Register;
