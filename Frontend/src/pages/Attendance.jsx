import React, { useState, useEffect } from 'react';
import Container from '../components/Container';
import Card from '../components/Card';
import WebcamFeed from '../components/register/WebcamFeed';
import DetectionOverlay from '../components/attendance/DetectionOverlay';
import StatusPanel from '../components/attendance/StatusPanel';
import ActivityFeed from '../components/attendance/ActivityFeed';
import { Clock, Activity, Users, Zap, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAttendanceFeed } from '../hooks/useAttendanceFeed';
import { getDailySummary, getHealthStatus } from '../services/api';
import { extractData } from '../services/apiHelpers';

const Attendance = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [recognitionState, setRecognitionState] = useState('idle');
  const [lastMatch, setLastMatch] = useState(null);
  const [attendanceStats, setAttendanceStats] = useState({ present: 0, total: 0, percentage: 0 });
  const [backendOnline, setBackendOnline] = useState(false);
  const [aiModuleOnline, setAiModuleOnline] = useState(false);
  const [time, setTime] = useState(new Date());

  const { latestEvent, eventHistory } = useAttendanceFeed();

  // Keep live clock running
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll backend health status
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await getHealthStatus();
        setBackendOnline(true);
      } catch (err) {
        setBackendOnline(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
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

  // Update recognition state and last matched student on new WebSocket events
  useEffect(() => {
    if (latestEvent) {
      setRecognitionState('success');
      setLastMatch({
        name: latestEvent.student_name,
        id: latestEvent.student_id,
        confidence: latestEvent.confidence,
      });
      
      // Auto-trigger stats refresh
      fetchStats();

      // Reset to idle state after 4 seconds
      const timer = setTimeout(() => {
        setRecognitionState('idle');
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [latestEvent]);

  // Track AI module activity (mark as active if we received a WebSocket event in the last 60 seconds)
  useEffect(() => {
    if (latestEvent) {
      setAiModuleOnline(true);
      const timer = setTimeout(() => setAiModuleOnline(false), 60000);
      return () => clearTimeout(timer);
    }
  }, [latestEvent]);

  // Transform real-time WebSocket events into the log structure expected by ActivityFeed
  const logs = eventHistory.map((event, idx) => ({
    id: idx,
    name: event.student_name,
    message: event.status === 'Present' ? 'Attendance Marked' : event.status,
    type: event.status === 'Present' ? 'success' : 'unknown',
    time: event.time ? event.time.substring(0, 8) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    confidence: event.confidence,
  }));

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
              <span className="text-[9px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">AI Module</span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`w-2 h-2 rounded-full ${aiModuleOnline ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'}`}></span>
                <span className={`text-xs font-bold uppercase leading-none ${aiModuleOnline ? 'text-emerald-400 animate-pulse' : 'text-amber-400'}`}>
                  {aiModuleOnline ? 'Active' : 'Standby'}
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
                onStreamStart={() => setIsCameraActive(true)}
                onStreamStop={() => {
                  setIsCameraActive(false);
                  setRecognitionState('idle');
                }}
              />
              {isCameraActive && (
                <DetectionOverlay isScanning={recognitionState === 'success'} />
              )}
              
              {/* Progress Overlay */}
              {recognitionState === 'success' && (
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-64 z-30">
                  <div className="flex justify-between text-[10px] text-green-400 font-bold uppercase mb-1">
                    <span>Scan Successful</span>
                    <span>100%</span>
                  </div>
                  <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden border border-white/5">
                    <div 
                      className="h-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]"
                      style={{ width: `100%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            <Card className="p-4 bg-gray-900/40 border-gray-700/30 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Zap className="text-blue-500 fill-blue-500/10 animate-pulse" size={24} />
                <div>
                  <span className="text-xs font-bold text-white block uppercase tracking-wider">Live AI Recognition Feed</span>
                  <span className="text-[10px] text-gray-500 block">The system monitors real-time face detections from the desktop OpenCV camera module.</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${aiModuleOnline ? 'bg-emerald-500 animate-ping' : 'bg-amber-500 animate-pulse'}`}></span>
                <span className="text-[10px] font-mono uppercase tracking-widest text-gray-400">
                  {aiModuleOnline ? 'AI Broadcaster Connected' : 'Waiting for AI Module...'}
                </span>
              </div>
            </Card>
          </div>

          {/* Right: Sidebar (40%) */}
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

            <ActivityFeed logs={logs} onClear={() => {}} />
          </div>
        </div>
      </Container>
    </div>
  );
};

export default Attendance;
