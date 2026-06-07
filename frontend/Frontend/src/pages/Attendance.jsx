import { useCallback, useState, useEffect, useRef } from 'react';
import Container from '../components/Container';
import Card from '../components/Card';
import WebcamFeed from '../components/register/WebcamFeed';
import DetectionOverlay from '../components/attendance/DetectionOverlay';
import StatusPanel from '../components/attendance/StatusPanel';
import { Activity, Users, Zap, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { getDailySummary } from '../services/api';
import { extractData } from '../services/apiHelpers';

// Raw axios instance that does NOT have the 401 redirect interceptor.
// The attendance terminal is a public page — no admin JWT required.
const rawApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

const formatArrivalTime = (timeValue) => {
  if (!timeValue) {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  if (typeof timeValue === 'string' && /^\d{2}:\d{2}/.test(timeValue)) {
    const [hourValue, minuteValue] = timeValue.split(':');
    const hour = parseInt(hourValue, 10);
    const displayHour = hour % 12 || 12;
    const ampm = hour >= 12 ? 'PM' : 'AM';
    return `${displayHour}:${minuteValue} ${ampm}`;
  }

  const parsedDate = new Date(timeValue);
  if (!Number.isNaN(parsedDate.getTime())) {
    return parsedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  return timeValue;
};

const Attendance = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [recognitionState, setRecognitionState] = useState('idle');
  // 'idle' | 'scanning' | 'success' | 'duplicate' | 'unrecognized' | 'error'
  const [lastMatch, setLastMatch] = useState(null);
  const [attendanceStats, setAttendanceStats] = useState({ present: 0, total: 0, percentage: 0 });
  const [backendOnline, setBackendOnline] = useState(false);
  const [time, setTime] = useState(new Date());
  const [cameraSessionKey, setCameraSessionKey] = useState(0);
  const isBusyRef = useRef(false);

  // Keep live clock running
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll backend health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await rawApi.get('/api/v1/health');
        setBackendOnline(true);
      } catch {
        setBackendOnline(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Fetch daily attendance stats
  const fetchStats = async () => {
    try {
      const response = await getDailySummary();
      const data = extractData(response);
      setAttendanceStats({
        present: data.present_count || 0,
        total: data.total_students || 0,
        percentage: data.attendance_percentage || 0,
      });
    } catch (err) {
      console.error('Stats fetch error:', err);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  const resetTerminalForNextStudent = useCallback((delay = 2500) => {
    setTimeout(() => {
      setRecognitionState('idle');
      setLastMatch(null);
      setCameraSessionKey(prev => prev + 1);
      isBusyRef.current = false;
    }, delay);
  }, []);

  // The core recognition handler — fires on every camera frame
  const handleLiveFrame = useCallback(async (frame) => {
    // Don't send frames while we're showing success/error state or already processing
    if (isBusyRef.current) return;
    
    isBusyRef.current = true;
    setRecognitionState('scanning');
    
    try {
      const response = await rawApi.post('/api/v1/attendance/recognize-frame', {
        image_base64: frame,
      });

      const result = response.data?.data;
      
      if (!result) {
        isBusyRef.current = false;
        return;
      }

      // --- Multi-face recognition response ---
      if (result.type === 'multi_recognition' && Array.isArray(result.results)) {
        const marked = result.results.filter(r => r.type === 'attendance_marked');
        const duplicates = result.results.filter(r => r.status === 'duplicate');
        const unrecognized = result.results.filter(r => r.status === 'unrecognized');
        const allBoxes = result.results.map(r => ({
          box: r.box,
          type: r.type === 'attendance_marked' ? 'marked' : r.status === 'duplicate' ? 'duplicate' : 'unrecognized',
          name: r.student_name || null,
        }));

        if (marked.length > 0) {
          const names = marked.map(r => r.student_name).filter(Boolean);
          setRecognitionState('multi_success');
          setLastMatch({
            names,
            count: marked.length,
            duplicateCount: duplicates.length,
            unrecognizedCount: unrecognized.length,
            boxes: allBoxes,
            results: marked,
          });
          fetchStats();
          resetTerminalForNextStudent(3000);
        } else if (duplicates.length > 0) {
          setRecognitionState('duplicate');
          const names = duplicates.map(r => r.student_name).filter(Boolean);
          setLastMatch({
            name: names.length > 1 ? `${names.join(', ')}` : 'Already Marked',
            id: duplicates.map(r => r.student_id).join(', '),
            confidence: 100,
            box: null,
            boxes: allBoxes,
            arrivalTime: duplicates[0]?.time ? formatArrivalTime(duplicates[0].time) : null,
            message: `Attendance already recorded for ${names.length} student(s).`,
          });
          resetTerminalForNextStudent(2200);
        } else {
          setRecognitionState('unrecognized');
          setLastMatch({
            name: 'Unknown Persons',
            id: 'Please register first',
            confidence: 0,
            boxes: allBoxes,
            message: `${unrecognized.length} unrecognized face(s). Students should register first.`,
          });
          resetTerminalForNextStudent(3000);
        }
        return;
      }

      // --- Single-face responses (backward compatibility) ---
      if (result.type === 'attendance_marked') {
        // SUCCESS: Face recognized & attendance marked
        setRecognitionState('success');
        setLastMatch({
          name: result.student_name,
          id: result.student_id,
          confidence: result.confidence,
          box: result.box,
          status: result.status,
          arrivalTime: formatArrivalTime(result.time),
        });
        fetchStats();
        resetTerminalForNextStudent(2500);
        return;

      } else if (result.status === 'cooldown' || result.status === 'duplicate') {
        // Already marked today
        setRecognitionState('duplicate');
        setLastMatch({
          name: 'Already Marked',
          id: result.student_id || '',
          confidence: 100,
          box: null,
          arrivalTime: result.time ? formatArrivalTime(result.time) : null,
          message: result.message || 'Attendance already recorded for today.',
        });
        resetTerminalForNextStudent(2200);
        return;

      } else if (result.status === 'unrecognized') {
        // NOT REGISTERED — tell the user
        setRecognitionState('unrecognized');
        setLastMatch({
          name: 'Unknown Person',
          id: 'Please register yourself first',
          confidence: 0,
          message: result.message || 'Student should register first.',
        });
        resetTerminalForNextStudent(3000);
        return;
      }

      // no_face_found or other — silently continue scanning
      setRecognitionState('idle');
      isBusyRef.current = false;

    } catch (err) {
      console.error("Frame recognition error:", err);
      setRecognitionState('error');
      setLastMatch({ message: 'Recognition failed. Checking the next frame...' });
      isBusyRef.current = false;
    }
  }, [resetTerminalForNextStudent]);

  // Activity log from matches
  const [activityLog, setActivityLog] = useState([]);
  useEffect(() => {
    if (recognitionState === 'success' && lastMatch && lastMatch.name !== 'Already Marked') {
      setActivityLog(prev => [{
        name: lastMatch.name,
        time: lastMatch.arrivalTime || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        confidence: lastMatch.confidence,
      }, ...prev].slice(0, 10));
    }
    // Multi-face: add all marked students to the log
    if (recognitionState === 'multi_success' && lastMatch?.results) {
      const newEntries = lastMatch.results.map(r => ({
        name: r.student_name,
        time: r.time ? formatArrivalTime(r.time) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        confidence: r.confidence,
      }));
      setActivityLog(prev => [...newEntries, ...prev].slice(0, 10));
    }
  }, [recognitionState, lastMatch]);

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-gray-100 flex flex-col font-sans">
      <Container className="py-8 flex-1 flex flex-col">
        {/* Back Button */}
        <Link to="/" className="text-cyan-500 hover:text-cyan-400 flex items-center gap-2 text-xs font-mono uppercase tracking-widest transition-colors mb-6 w-max">
          <ArrowLeft size={14} /> Back to Hub
        </Link>
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Zap className="text-blue-500 fill-blue-500/20" size={32} />
              Attendance Terminal
            </h1>
            <p className="text-gray-400 mt-1 font-medium italic">Biometric Verification System v2.0</p>
          </div>
          
          <div className="flex items-center flex-wrap gap-6 bg-gray-900/80 backdrop-blur-xl px-6 py-3 rounded-2xl border border-gray-700/50 shadow-2xl">
            {/* Live Clock */}
            <div className="flex flex-col items-end">
              <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Live Clock</span>
              <span className="text-lg font-mono text-blue-400 leading-none">{time.toLocaleTimeString()}</span>
            </div>
            <div className="hidden sm:block h-8 w-px bg-gray-700"></div>
            
            {/* Camera Status */}
            <div className="flex flex-col items-start">
              <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Local Camera</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`w-2 h-2 rounded-full ${isCameraActive ? 'bg-green-500 animate-pulse' : 'bg-red-500'} shadow-[0_0_8px_rgba(34,197,94,0.5)]`}></span>
                <span className={`text-xs font-bold uppercase leading-none ${isCameraActive ? 'text-green-400' : 'text-red-400'}`}>
                  {isCameraActive ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
            <div className="hidden sm:block h-8 w-px bg-gray-700"></div>

            {/* Backend Connection */}
            <div className="flex flex-col items-start">
              <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Backend Link</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'} shadow-[0_0_8px_rgba(34,197,94,0.5)]`}></span>
                <span className={`text-xs font-bold uppercase leading-none ${backendOnline ? 'text-green-400' : 'text-red-400'}`}>
                  {backendOnline ? 'Connected' : 'Offline'}
                </span>
              </div>
            </div>
            <div className="hidden sm:block h-8 w-px bg-gray-700"></div>

            {/* AI Module Status */}
            <div className="flex flex-col items-start">
              <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Web UI AI</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`w-2 h-2 rounded-full ${isCameraActive && backendOnline ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'}`}></span>
                <span className={`text-xs font-bold uppercase leading-none ${isCameraActive && backendOnline ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`}>
                  {isCameraActive && backendOnline ? 'Active' : 'Standby'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
          {/* Left: Camera & Info (70%) */}
          <div className="lg:col-span-8 flex flex-col space-y-6">
            <div className="relative group rounded-3xl overflow-hidden border-2 border-gray-700/50 shadow-[0_0_60px_rgba(0,0,0,0.8)] bg-black aspect-video">
              <WebcamFeed 
                key={cameraSessionKey}
                autoStart={true}
                autoInterval={1500}
                onLiveFrame={handleLiveFrame}
                onStreamStart={() => setIsCameraActive(true)}
                onStreamStop={() => {
                  setIsCameraActive(false);
                  setRecognitionState('idle');
                }}
              />
              {isCameraActive && (
                <DetectionOverlay 
                  isScanning={recognitionState === 'scanning' || recognitionState === 'success' || recognitionState === 'multi_success'} 
                  trackingBox={lastMatch?.box}
                  trackingBoxes={lastMatch?.boxes}
                />
              )}
              
              {/* Success Overlay (single face) */}
              {recognitionState === 'success' && lastMatch && (
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-72 z-30">
                  <div className="bg-green-900/80 backdrop-blur-md border border-green-500/50 rounded-2xl px-5 py-3 text-center shadow-[0_0_40px_rgba(34,197,94,0.3)]">
                    <p className="text-green-400 font-bold text-sm">{lastMatch.name}</p>
                    <p className="text-green-300/70 text-[10px] font-mono mt-1">
                      Confidence: {lastMatch.confidence?.toFixed(1)}% | {lastMatch.arrivalTime}
                    </p>
                  </div>
                </div>
              )}

              {/* Multi-Success Overlay */}
              {recognitionState === 'multi_success' && lastMatch && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-80 z-30">
                  <div className="bg-green-900/85 backdrop-blur-lg border border-green-500/50 rounded-2xl px-5 py-4 text-center shadow-[0_0_50px_rgba(34,197,94,0.4)]">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p className="text-green-300 font-bold text-sm">
                        {lastMatch.count} Student{lastMatch.count > 1 ? 's' : ''} Marked ✅
                      </p>
                    </div>
                    <div className="space-y-1">
                      {lastMatch.names?.map((name, i) => (
                        <p key={i} className="text-green-400/90 text-xs font-semibold">{name}</p>
                      ))}
                    </div>
                    {(lastMatch.duplicateCount > 0 || lastMatch.unrecognizedCount > 0) && (
                      <p className="text-green-300/50 text-[9px] font-mono mt-2 uppercase">
                        {lastMatch.duplicateCount > 0 && `${lastMatch.duplicateCount} already marked`}
                        {lastMatch.duplicateCount > 0 && lastMatch.unrecognizedCount > 0 && ' • '}
                        {lastMatch.unrecognizedCount > 0 && `${lastMatch.unrecognizedCount} unrecognized`}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Unrecognized Overlay */}
              {recognitionState === 'unrecognized' && (
                <div className="absolute inset-0 flex items-center justify-center z-30 bg-black/40 backdrop-blur-sm">
                  <div className="bg-red-900/90 backdrop-blur-md border-2 border-red-500/60 rounded-3xl px-8 py-6 text-center shadow-[0_0_60px_rgba(239,68,68,0.4)] animate-in zoom-in duration-300">
                    <div className="bg-red-500/20 rounded-full p-3 w-16 h-16 flex items-center justify-center mx-auto mb-3">
                      <svg className="w-10 h-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                    </div>
                    <p className="text-red-300 font-bold text-lg">{lastMatch?.name || 'Unknown Person'}</p>
                    <p className="text-red-400/80 text-xs mt-1">{lastMatch?.message || 'Please register yourself first.'}</p>
                  </div>
                </div>
              )}
            </div>

            <Card className="p-4 bg-gray-900/40 border-gray-700/30 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Zap className="text-blue-500 fill-blue-500/10 animate-pulse" size={24} />
                <div>
                  <span className="text-xs font-bold text-white block uppercase tracking-wider">Live AI Recognition Feed</span>
                  <span className="text-[10px] text-gray-500 block">Camera automatically scans faces and marks attendance in real-time.</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${isCameraActive && backendOnline ? 'bg-emerald-500 animate-ping' : 'bg-amber-500 animate-pulse'}`}></span>
                <span className="text-[10px] font-mono uppercase tracking-widest text-gray-400">
                  {isCameraActive && backendOnline ? 'AI Recognition Active' : 'Waiting for connection...'}
                </span>
              </div>
            </Card>
          </div>

          {/* Right: Sidebar (30%) */}
          <div className="lg:col-span-4 flex flex-col h-full space-y-6">
            <StatusPanel state={recognitionState} student={lastMatch} />

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <Card className="p-4 bg-blue-600/5 border-blue-600/20 flex flex-col items-center group hover:bg-blue-600/10 transition-colors">
                <span className="text-[9px] text-blue-400 font-black tracking-tighter uppercase mb-1">Present Today</span>
                <div className="flex items-center gap-2">
                  <Users size={14} className="text-blue-500" />
                  <span className="text-2xl font-bold text-white tracking-tighter">{attendanceStats.present}</span>
                </div>
              </Card>
              <Card className="p-4 bg-violet-600/5 border-violet-600/20 flex flex-col items-center group hover:bg-violet-600/10 transition-colors">
                <span className="text-[9px] text-violet-400 font-black tracking-tighter uppercase mb-1">Attendance Percentage</span>
                <div className="flex items-center gap-2">
                  <Activity size={14} className="text-violet-500" />
                  <span className="text-2xl font-bold text-white tracking-tighter">{attendanceStats.percentage}%</span>
                </div>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="flex flex-col flex-1 overflow-hidden border border-gray-800/80 bg-gray-900/40 p-0">
              <div className="p-5 border-b border-gray-800/80 bg-gray-900/20 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Recent Activity</h3>
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
              </div>
              <div className="p-5 space-y-3 overflow-y-auto max-h-[300px]">
                {activityLog.length === 0 ? (
                  <div className="text-center py-10">
                    <p className="text-gray-500 text-sm">No activity recorded yet.</p>
                  </div>
                ) : (
                  activityLog.map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-gray-800/30 border border-gray-700/50">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-green-500/10 flex items-center justify-center">
                          <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white">{item.name}</p>
                          <p className="text-[10px] text-gray-500">{item.confidence?.toFixed(1)}% match</p>
                        </div>
                      </div>
                      <span className="text-[10px] text-gray-500 font-mono">{item.time}</span>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>
      </Container>
    </div>
  );
};

export default Attendance;
