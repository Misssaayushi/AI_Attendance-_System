/**
 * SYNEXIntro.jsx
 * =========================================================================
 * The ultimate futuristic premium AI Landing Page Intro & Biometric Authentication screen.
 * Designed for AI Attendance Management & Facial Recognition Systems in Smart Universities.
 * 
 * Cinematic Timeline:
 * 1. Initial Load (0s - 4s): Matte black background. The emblem floats gently.
 *    The scanning laser sweeps vertically across the face.
 *    The terminal log console prints system telemetry step-by-step.
 * 2. Scan Completion (4s): The laser scan beam stops and fades out.
 *    The circular biometric checkmark badge springs out with an elastic bounce and pulses.
 *    The cinematic audio synthesizer plays an upward swept chord.
 *    "Identity Verified Successfully" system text fades in.
 *    A premium glowing "Enter Dashboard" button fades in with mouse-reactive highlights.
 * 3. 3D Mouse Parallax: Emblem tilts smoothly towards the cursor for high fidelity.
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';
import InteractiveFaceScanLogo from '../home/InteractiveFaceScanLogo';

// =========================================================================
// WEBAUDIO SYNTHESIZER UTILITIES (Fail-safe code-only sound generators)
// =========================================================================

// Generate futuristic high-pitch diagnostic bleeps
const playSynthBeep = (freq, duration, type = 'sine') => {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    gain.gain.setValueAtTime(0.015, ctx.currentTime); // Low volume for absolute comfort
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {
    // Fail-safe
  }
};

// Play microscopic premium hover ticks for buttons/columns
const playHoverTick = () => {
  playSynthBeep(2400, 0.03, 'sine');
};

// Play cinematic major upward sweep on successful validation
const playSuccessChime = () => {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const now = ctx.currentTime;
    
    const freqs = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 (Major sweep)
    freqs.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now + idx * 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      gain.gain.setValueAtTime(0.02, now + idx * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.08 + 0.4);
      
      osc.start(now + idx * 0.08);
      osc.stop(now + idx * 0.08 + 0.4);
    });
  } catch (e) {
    // Fail-safe
  }
};

export default function SYNEXIntro({ onEnter }) {
  // Verification states
  const [scanState, setScanState] = useState('scanning'); // 'scanning' | 'verified'
  const [loaded, setLoaded] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  
  // Webcam states
  const [stream, setStream] = useState(null);
  const videoRef = useRef(null);

  // Terminal logs state variables
  const [logs, setLogs] = useState([]);
  const [logIndex, setLogIndex] = useState(0);

  // Live tracking statistics states (flickers coordinate numbers)
  const [telemetry, setTelemetry] = useState({ x: 120.4, y: 340.2, match: 72.5 });

  const logSteps = useMemo(() => [
    { text: "⚡ CONNECTING TO SYNEX NEURAL CORE...", beep: 520 },
    { text: "📷 ACCESSING BIOMETRIC SENSOR FEED...", beep: 600 },
    { text: "🔍 SCANNING FACIAL SURFACE GEOMETRY...", beep: 680 },
    { text: "🧩 ANALYSIS: MAPPING COORDINATES...", beep: 750 },
    { text: "🛡️ SECURE SESSION KEY COMPILED...", beep: 840 },
    { text: "🟢 ACCESS LEVEL 1 GRANTED. AUTHORIZED.", beep: 1046, done: true }
  ], []);

  // Cycle through diagnostic prints with audio chirps
  useEffect(() => {
    if (logIndex < logSteps.length && scanState === 'scanning') {
      const step = logSteps[logIndex];
      const timer = setTimeout(() => {
        if (step.beep) {
          playSynthBeep(step.beep, 0.12, 'triangle');
        }
        setLogs(prev => [...prev, step.text]);
        setLogIndex(prev => prev + 1);
        
        if (step.done) {
          setScanState('verified');
          setLoaded(true);
          setTimeout(() => {
            playSuccessChime();
          }, 150);
        }
      }, logIndex === 0 ? 600 : logIndex === 1 ? 1000 : 700);
      
      return () => clearTimeout(timer);
    }
  }, [logIndex, logSteps, scanState]);

  // Live coordinates flicker generator (Simulating active AI computations)
  useEffect(() => {
    let interval;
    if (scanState === 'scanning') {
      interval = setInterval(() => {
        setTelemetry({
          x: (110 + Math.random() * 25).toFixed(2),
          y: (330 + Math.random() * 25).toFixed(2),
          match: (68 + Math.random() * 30).toFixed(1)
        });
      }, 90);
    } else {
      setTelemetry({ x: 120.0, y: 340.0, match: 100.0 });
    }
    return () => clearInterval(interval);
  }, [scanState]);

  // Click-to-Rescan (Allows repeating the visual scan sequence for examiners)
  const handleRescan = () => {
    if (isExiting) return;
    playSynthBeep(440, 0.15, 'sine');
    setScanState('scanning');
    setLoaded(false);
    setLogs([]);
    setLogIndex(0);
  };

  // Exit intro portal cleanly
  const handlePortalEnter = () => {
    playSynthBeep(880, 0.08); // Trigger confirmation chirp
    setIsExiting(true);
    setTimeout(() => {
      if (onEnter) onEnter();
    }, 800);
  };

  // Pre-generate static background particles once to avoid hydration flashes
  const particles = useMemo(() => {
    return Array.from({ length: 22 }).map((_, i) => ({
      id: i,
      top: `${Math.random() * 100}%`,
      left: `${Math.random() * 100}%`,
      duration: `${3 + Math.random() * 5}s`,
      delay: `${Math.random() * 2}s`,
      size: Math.random() > 0.65 ? 'w-1 h-1' : 'w-1.5 h-1.5'
    }));
  }, []);

  return (
    <div 
      className={`relative min-h-screen overflow-x-hidden bg-[#0a0a0c] flex flex-col items-center justify-center py-8 px-4 transition-all duration-1000 select-none ${
        isExiting ? 'animate-fadeOut' : ''
      }`}
    >
      {/* 1. BLUEPRINT GRID & METRIC NEURAL BACKDROP */}
      <div className="absolute inset-0 bg-[radial-gradient(#0f1118_40%,#0a0a0c_100%)] pointer-events-none"></div>
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(6,182,212,0.012)_1px,transparent_1px),linear-gradient(to_bottom,rgba(6,182,212,0.012)_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none"></div>

      {/* Ambient glows (Matching teal & violet details perfectly) */}
      <div className="absolute w-[600px] h-[600px] bg-cyan-500/5 blur-[140px] rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none animate-pulse" style={{ animationDuration: '8s' }}></div>
      <div className="absolute top-10 left-10 w-[400px] h-[400px] bg-violet-600/5 blur-[120px] rounded-full pointer-events-none"></div>

      {/* 2. BACKGROUND PARTICLE ATMOSPHERE */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {particles.map((p) => (
          <span
            key={p.id}
            className={`absolute ${p.size} bg-cyan-400/20 rounded-full animate-ping`}
            style={{
              top: p.top,
              left: p.left,
              animationDuration: p.duration,
              animationDelay: p.delay,
            }}
          ></span>
        ))}
      </div>

      {/* 3. HERO CONTENT WRAPPER */}
      <div className="relative z-10 w-full max-w-4xl flex flex-col items-center">
        
        {/* PARALLAX 3D EMBLEM MODULE */}
        <div className="animate-float-emblem">
          <div 
            onClick={handleRescan}
            title="Click to Trigger Re-Scan"
            className="relative w-[340px] h-[340px] flex items-center justify-center cursor-pointer group rounded-full"
          >
            {/* The new clean SVG-based Interactive Face Scanner Logo */}
            <div className="absolute inset-0 flex items-center justify-center z-10">
              <InteractiveFaceScanLogo navigateOnClick={false} onClick={handleRescan} />
            </div>

            {/* Rapidly changing coordinate overlays */}
            <div className="absolute top-8 left-0 font-mono text-[8px] text-cyan-400/60 bg-[#03050c]/85 border border-cyan-500/10 px-2 py-0.5 rounded shadow-lg pointer-events-none select-none z-30">
              POS_X: <span className="font-bold text-cyan-400">{telemetry.x}</span>
            </div>
            <div className="absolute top-8 right-0 font-mono text-[8px] text-cyan-400/60 bg-[#03050c]/85 border border-cyan-500/10 px-2 py-0.5 rounded shadow-lg pointer-events-none select-none z-30">
              POS_Y: <span className="font-bold text-cyan-400">{telemetry.y}</span>
            </div>
            <div className="absolute bottom-16 left-4 font-mono text-[8px] text-cyan-400/60 bg-[#03050c]/85 border border-cyan-500/10 px-2 py-0.5 rounded shadow-lg pointer-events-none select-none z-30">
              INDEX: <span className="font-bold text-cyan-400">{telemetry.match}%</span>
            </div>

            {/* Laser scanning laser line (Only active during 'scanning' phase) */}
            <div className={`absolute w-[210px] h-[4px] bg-cyan-400 left-1/2 -translate-x-1/2 shadow-[0_0_25px_#22d3ee,0_0_10px_#22d3ee] rounded-full animate-scan-line z-30 transition-opacity duration-700 ${
              scanState === 'scanning' ? 'opacity-100' : 'opacity-0'
            }`}></div>
            <div className={`absolute w-[210px] h-[70px] bg-gradient-to-b from-cyan-400/15 to-transparent left-1/2 -translate-x-1/2 animate-scan-light z-20 pointer-events-none rounded-t-lg transition-opacity duration-700 ${
              scanState === 'scanning' ? 'opacity-100' : 'opacity-0'
            }`}></div>
            
            {/* Click-to-scan prompt */}
            <div className="absolute inset-0 rounded-full group-hover:bg-cyan-500/[0.01] transition-all duration-300 z-30 flex items-center justify-center">
              <span className="font-mono text-[7px] text-cyan-400/0 group-hover:text-cyan-400/80 uppercase tracking-[2px] translate-y-[135px] transition-all duration-300 drop-shadow-md bg-black/40 px-2 py-1 rounded">
                [ Click to Re-Scan ]
              </span>
            </div>
          </div>
        </div>

        {/* BRAND TYPOGRAPHY (Matches original) */}
        <h1 className="mt-8 text-6xl md:text-7xl font-extrabold tracking-[6px] select-none uppercase drop-shadow-[0_4px_12px_rgba(0,0,0,0.6)] flex items-center justify-center">
          <span className="bg-gradient-to-b from-white via-slate-100 to-slate-400 text-transparent bg-clip-text">SYNE</span>
          <span className="bg-gradient-to-r from-cyan-400 to-violet-400 text-transparent bg-clip-text drop-shadow-[0_0_25px_rgba(34,211,238,0.8)] font-black ml-[1px] animate-[pulse_2s_infinite]">X</span>
          <span className="bg-gradient-to-b from-white via-slate-100 to-slate-400 text-transparent bg-clip-text ml-4">AI</span>
        </h1>
        
        <p className="mt-4 text-slate-400 tracking-[5px] text-[10px] md:text-xs font-semibold select-none flex items-center justify-center gap-2">
          <span className="w-8 h-[1px] bg-gradient-to-r from-transparent to-cyan-500/50"></span>
          AI ATTENDANCE MANAGEMENT & FACIAL RECOGNITION SYSTEM
          <span className="w-8 h-[1px] bg-gradient-to-l from-transparent to-violet-500/50"></span>
        </p>

        {/* INTERACTIVE SCAN CONSOLE & APPROVED CTAS */}
        <div className="mt-6 min-h-[160px] flex flex-col items-center justify-center">
          
          {/* TERMINAL STATUS CONSOLE */}
          <div className="w-[330px] bg-[#020408]/95 border border-cyan-500/10 rounded-xl p-4 font-mono text-[10px] text-left shadow-[0_0_25px_rgba(0,0,0,0.8)] mb-4 select-none relative overflow-hidden backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-cyan-500/10 pb-2 mb-2.5 text-[9px] text-slate-500 font-bold uppercase tracking-wider">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500/40"></span>
                <span className="w-2 h-2 rounded-full bg-yellow-500/40"></span>
                <span className="w-2 h-2 rounded-full bg-green-500/40"></span>
                <span className="ml-1 text-cyan-400/70 font-mono">BIOMETRIC TERMINAL</span>
              </div>
              <span className="animate-pulse text-cyan-400/90 font-mono">REC ●</span>
            </div>
            
            <div className="space-y-1.5 min-h-[90px]">
              {logs.map((log, index) => (
                <div key={index} className="flex items-start gap-1">
                  <span className="text-cyan-400 font-bold select-none">&gt;</span>
                  <p className={`${index === logSteps.length - 1 ? 'text-emerald-400 font-bold' : 'text-slate-300'} leading-relaxed font-mono`}>
                    {log}
                  </p>
                </div>
              ))}
              {logIndex < logSteps.length && (
                <div className="flex items-center gap-1">
                  <span className="text-cyan-400 font-bold select-none">&gt;</span>
                  <span className="w-2 h-3.5 bg-cyan-400/90 rounded-sm animate-[pulse_0.6s_infinite]"></span>
                </div>
              )}
            </div>
          </div>

          {/* TRANSITIONING ENTER ACTION */}
          <div className={`transition-all duration-1000 ease-[cubic-bezier(0.16,1,0.3,1)] ${
            scanState === 'verified' ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95 pointer-events-none'
          }`}>
            <button 
              onClick={handlePortalEnter}
              onMouseEnter={playHoverTick}
              className="px-12 py-3.5 rounded-full bg-gradient-to-r from-cyan-500 to-violet-600 text-white text-xs font-black tracking-[3px] uppercase shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:shadow-[0_0_45px_rgba(139,92,246,0.6)] hover:scale-[1.05] active:scale-95 transition-all duration-300 cursor-pointer border border-cyan-400/35 relative overflow-hidden group"
            >
              <span className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></span>
              ENTER DASHBOARD
            </button>
          </div>
        </div>

        {/* CAPSULE FEATURES PANEL */}
        <div className="mt-4 w-full max-w-4xl bg-[#080c18]/50 backdrop-blur-xl border-0 rounded-full py-6 px-10 shadow-[0_0_40px_rgba(6,182,212,0.06),inset_0_0_20px_rgba(139,92,246,0.04)] capsule-glow-border relative animate-[fade_1.2s_ease-out_forwards]">
          <div className="flex flex-row items-center justify-between w-full">
            
            {/* 1. FACIAL RECOGNITION */}
            <div 
              onMouseEnter={playHoverTick}
              className="flex-1 flex flex-col items-center justify-center p-2 text-center hover:scale-[1.04] transition-all duration-300 cursor-pointer group"
            >
              <div className="mb-2.5 transition-transform duration-300 group-hover:-translate-y-0.5">
                <svg className="w-7 h-7 text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2" strokeLinecap="round" />
                  <path d="M8 14q4 3 8 0" strokeLinecap="round" />
                  <circle cx="9" cy="9" r="1" fill="currentColor" />
                  <circle cx="15" cy="9" r="1" fill="currentColor" />
                  <path d="M12 7v5" strokeLinecap="round" />
                  <path d="M6 10c0-4 12-4 12 0c0 4-2 7-6 9c-4-2-6-5-6-9Z" strokeLinecap="round" />
                </svg>
              </div>
              <span className="text-slate-400 group-hover:text-cyan-400 text-[9px] font-bold tracking-[3px] uppercase select-none transition-colors duration-300">FACIAL RECOGNITION</span>
            </div>

            {/* Fading Divider */}
            <div className="w-[1px] h-10 bg-gradient-to-b from-transparent via-slate-700/30 to-transparent"></div>

            {/* 2. AI POWERED VISION */}
            <div 
              onMouseEnter={playHoverTick}
              className="flex-1 flex flex-col items-center justify-center p-2 text-center hover:scale-[1.04] transition-all duration-300 cursor-pointer group"
            >
              <div className="mb-2.5 transition-transform duration-300 group-hover:-translate-y-0.5">
                <svg className="w-7 h-7 text-violet-400 drop-shadow-[0_0_8px_rgba(139,92,246,0.5)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-2.5 2.5" strokeLinecap="round" />
                  <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 2.5 2.5" strokeLinecap="round" />
                  <path d="M12 4.5a3.5 3.5 0 0 1 3.5 3.5M12 19.5a3.5 3.5 0 0 0 3.5-3.5" strokeLinecap="round" />
                  <path d="M12 4.5a3.5 3.5 0 0 0-3.5 3.5M12 19.5a3.5 3.5 0 0 1-3.5-3.5" strokeLinecap="round" />
                  <circle cx="6" cy="8" r="1.5" fill="currentColor" />
                  <circle cx="18" cy="8" r="1.5" fill="currentColor" />
                  <circle cx="5" cy="14" r="1.5" fill="currentColor" />
                  <circle cx="19" cy="14" r="1.5" fill="currentColor" />
                  <path d="M8.5 8H6M15.5 8h2.5M8.5 14H5M15.5 14h3.5" strokeLinecap="round" />
                </svg>
              </div>
              <span className="text-slate-400 group-hover:text-violet-400 text-[9px] font-bold tracking-[3px] uppercase select-none transition-colors duration-300">AI POWERED VISION</span>
            </div>

            {/* Fading Divider */}
            <div className="w-[1px] h-10 bg-gradient-to-b from-transparent via-slate-700/30 to-transparent"></div>

            {/* 3. SMART ATTENDANCE */}
            <div 
              onMouseEnter={playHoverTick}
              className="flex-1 flex flex-col items-center justify-center p-2 text-center hover:scale-[1.04] transition-all duration-300 cursor-pointer group"
            >
              <div className="mb-2.5 transition-transform duration-300 group-hover:-translate-y-0.5">
                <svg className="w-7 h-7 text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="m9 11 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <span className="text-slate-400 group-hover:text-cyan-400 text-[9px] font-bold tracking-[3px] uppercase select-none transition-colors duration-300">SMART ATTENDANCE</span>
            </div>

            {/* Fading Divider */}
            <div className="w-[1px] h-10 bg-gradient-to-b from-transparent via-slate-700/30 to-transparent"></div>

            {/* 4. SMART UNIVERSITIES */}
            <div 
              onMouseEnter={playHoverTick}
              className="flex-1 flex flex-col items-center justify-center p-2 text-center hover:scale-[1.04] transition-all duration-300 cursor-pointer group"
            >
              <div className="mb-2.5 transition-transform duration-300 group-hover:-translate-y-0.5">
                <svg className="w-7 h-7 text-violet-400 drop-shadow-[0_0_8px_rgba(139,92,246,0.5)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M3 21h18M4 18h16" strokeLinecap="round" />
                  <path d="M6 10v8M10 10v8M14 10v8M18 10v8" strokeLinecap="round" />
                  <path d="M5 7h14" strokeLinecap="round" />
                  <path d="M12 2 3 7h18Z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <span className="text-slate-400 group-hover:text-violet-400 text-[9px] font-bold tracking-[3px] uppercase select-none transition-colors duration-300">SMART UNIVERSITIES</span>
            </div>

          </div>
        </div>

      </div>

      {/* STYLESHEET ANIMATIONS */}
      <style>
        {`
        .capsule-glow-border {
          position: relative;
        }
        .capsule-glow-border::before {
          content: "";
          position: absolute;
          inset: 0;
          border-radius: 9999px;
          padding: 1px;
          background: linear-gradient(to right, rgba(34, 211, 238, 0.15), rgba(139, 92, 246, 0.15));
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          pointer-events: none;
        }

        @keyframes scanLine {
          0% { top: 22%; }
          50% { top: 62%; }
          100% { top: 22%; }
        }

        @keyframes scanLight {
          0% { top: 22%; opacity: 0.15; }
          50% { top: 62%; opacity: 0.25; }
          100% { top: 22%; opacity: 0.15; }
        }

        @keyframes floatEmblem {
          0% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-8px) rotate(0.4deg); }
          100% { transform: translateY(0px) rotate(0deg); }
        }

        @keyframes fade {
          from {
            opacity: 0;
            transform: translateY(15px);
          }
          to {
            opacity: 1;
            transform: translateY(0px);
          }
        }

        @keyframes fadeOut {
          from {
            opacity: 1;
            transform: scale(1);
          }
          to {
            opacity: 0;
            transform: scale(1.04);
            filter: blur(10px);
          }
        }

        .animate-scan-line {
          animation: scanLine 4.5s ease-in-out infinite;
        }

        .animate-scan-light {
          animation: scanLight 4.5s ease-in-out infinite;
        }

        .animate-float-emblem {
          animation: floatEmblem 6.5s ease-in-out infinite;
        }

        .animate-fade {
          animation: fade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .animate-fadeOut {
          animation: fadeOut 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .animate-spin-slow {
          animation: spin 20s linear infinite;
        }
        `}
      </style>
    </div>
  );
}
