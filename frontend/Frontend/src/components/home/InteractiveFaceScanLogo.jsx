import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// =========================================================================
// WEBAUDIO SYNTHESIZER UTILITIES
// =========================================================================
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
    
    gain.gain.setValueAtTime(0.015, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch (e) {
    // Fail-safe
  }
};

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

const playHoverTick = () => {
  playSynthBeep(2200, 0.02, 'sine');
};

const InteractiveFaceScanLogo = ({ navigateOnClick = true, onClick }) => {
  const navigate = useNavigate();
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const containerRef = useRef(null);

  // Play audio triggers according to the load sequence
  useEffect(() => {
    // Stage 1: Load circle (0s)
    playSynthBeep(520, 0.15, 'triangle');
    
    // Stage 2: Corners (1.2s)
    const t2 = setTimeout(() => {
      playSynthBeep(680, 0.15, 'triangle');
    }, 1200);
    
    // Stage 3: Face trace (1.8s)
    const t3 = setTimeout(() => {
      playSynthBeep(840, 0.2, 'triangle');
    }, 1800);
    
    // Stage 4: Verified tick & rays (3.8s)
    const t4 = setTimeout(() => {
      playSuccessChime();
    }, 3800);

    return () => {
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  }, []);

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    // Calculate rotation vectors (+/- 12 degrees max)
    const x = (e.clientX - rect.left - rect.width / 2) / 12;
    const y = -(e.clientY - rect.top - rect.height / 2) / 12;
    setTilt({ x, y });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
    setIsHovered(false);
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
    playHoverTick();
  };

  const handleClick = (e) => {
    if (onClick) {
      onClick(e);
      return;
    }
    if (navigateOnClick) {
      playSynthBeep(880, 0.1, 'sine');
      // Navigate to dashboard
      navigate('/dashboard');
    }
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onMouseEnter={handleMouseEnter}
      onClick={handleClick}
      className="relative w-80 h-80 flex items-center justify-center cursor-pointer select-none group"
      style={{
        transform: `perspective(1000px) rotateX(${tilt.y}deg) rotateY(${tilt.x}deg)`,
        transition: 'transform 0.15s ease-out',
      }}
      title="Click to Access System Dashboard"
    >
      {/* Background radial soft blue glow */}
      <div className="absolute inset-0 bg-cyan-500/5 blur-3xl rounded-full pointer-events-none scale-75 group-hover:scale-90 group-hover:bg-cyan-500/10 transition-all duration-500"></div>

      <svg 
        viewBox="0 0 300 300" 
        className="w-full h-full filter drop-shadow-[0_0_20px_rgba(6,182,212,0.15)] group-hover:drop-shadow-[0_0_30px_rgba(6,182,212,0.3)] transition-all duration-500"
      >
        <defs>
          {/* Neon Glow Filters */}
          <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          
          <filter id="glow-purple" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Gradients */}
          <linearGradient id="metallic-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#475569" />
            <stop offset="30%" stopColor="#94a3b8" />
            <stop offset="50%" stopColor="#1e293b" />
            <stop offset="70%" stopColor="#cbd5e1" />
            <stop offset="100%" stopColor="#334155" />
          </linearGradient>

          <linearGradient id="neon-blue-purple" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="50%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>

          <radialGradient id="face-shading" cx="40%" cy="50%" r="60%">
            <stop offset="0%" stopColor="#0f172a" stopOpacity="0.8" />
            <stop offset="60%" stopColor="#1e293b" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#090d16" stopOpacity="0.95" />
          </radialGradient>
        </defs>

        {/* ========================================== */}
        {/* LAYER 1: OUTER CIRCLE & METALLIC ARCS      */}
        {/* ========================================== */}
        
        {/* Underlayer Shadow Circle */}
        <circle 
          cx="150" 
          cy="150" 
          r="115" 
          stroke="#05070c" 
          strokeWidth="8" 
          fill="none" 
          className="opacity-70"
        />

        {/* Large Outer Arc (Metallic Segment) */}
        <path 
          d="M 207.5 50.4 A 115 115 0 1 0 231.3 231.3" 
          stroke="url(#metallic-grad)" 
          strokeWidth="6" 
          fill="none" 
          strokeLinecap="round"
          className="anim-circle-large"
        />
        
        {/* Small Arc Segment at top right */}
        <path 
          d="M 231.3 68.7 A 115 115 0 0 1 261 120" 
          stroke="url(#neon-blue-purple)" 
          strokeWidth="5" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-circle-small"
        />

        {/* Small outer glowing orbit dot at top right */}
        <circle 
          cx="240" 
          cy="48" 
          r="5.5" 
          fill="#22d3ee" 
          filter="url(#glow-cyan)"
          className="anim-orbit-dot"
        />

        {/* Inner thin decorative ring */}
        <circle 
          cx="150" 
          cy="150" 
          r="105" 
          stroke="#1e293b" 
          strokeWidth="1.5" 
          fill="none" 
          strokeDasharray="6 8"
          className="opacity-60"
        />


        {/* ========================================== */}
        {/* LAYER 2: CORNER BRACKETS (L-SHAPES)        */}
        {/* ========================================== */}
        <g stroke="#22d3ee" strokeWidth="3" fill="none" strokeLinecap="round" filter="url(#glow-cyan)" className="anim-corners">
          {/* Top-Left Corner */}
          <path d="M 82 102 V 82 H 102" />
          {/* Top-Right Corner */}
          <path d="M 198 82 H 218 V 102" />
          {/* Bottom-Left Corner */}
          <path d="M 82 198 V 218 H 102" />
          {/* Bottom-Right Corner (slightly tucked behind badge) */}
          <path d="M 198 218 H 218 V 198" />
        </g>


        {/* ========================================== */}
        {/* LAYER 3: FACE OUTLINE & SHADING (LEFT SIDE) */}
        {/* ========================================== */}
        
        {/* Left Side Face Surface Fill (Shaded Silhouette) */}
        <path 
          d="M 150 90 C 118 90 108 120 108 150 C 108 160 110 170 115 175 C 113 182 116 190 123 197 C 132 207 140 215 150 215 Z" 
          fill="url(#face-shading)" 
          className="anim-face-shading"
        />

        {/* Left Side Face Outline (Glowing Cyan) */}
        <path 
          d="M 150 90 C 118 90 108 120 108 150 C 108 160 110 170 115 175 C 113 182 116 190 123 197 C 132 207 140 215 150 215" 
          stroke="url(#neon-blue-purple)" 
          strokeWidth="3.5" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-face-left"
        />

        {/* Left Ear */}
        <path 
          d="M 108 147 C 100 147 100 163 108 163" 
          stroke="#22d3ee" 
          strokeWidth="2.5" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-face-left"
        />

        {/* Left Neck Line */}
        <path 
          d="M 125 198 C 125 218 135 228 150 228" 
          stroke="#22d3ee" 
          strokeWidth="2" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-face-left"
        />

        {/* Left closed eye (Serene arc) */}
        <path 
          d="M 126 142 Q 134 147 142 142" 
          stroke="#22d3ee" 
          strokeWidth="3" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-face-features"
        />

        {/* Left half nose curve */}
        <path 
          d="M 150 130 V 164 C 145 164 144 160 150 156" 
          stroke="#22d3ee" 
          strokeWidth="2.5" 
          fill="none" 
          strokeLinejoin="round"
          filter="url(#glow-cyan)"
          className="anim-face-features"
        />

        {/* Left half mouth line */}
        <path 
          d="M 137 182 Q 143 184 150 182" 
          stroke="#22d3ee" 
          strokeWidth="2.5" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          className="anim-face-features"
        />


        {/* ========================================== */}
        {/* LAYER 4: FACE MAPPING MESH (RIGHT SIDE)    */}
        {/* ========================================== */}
        
        {/* Mesh Lines (Connect Nodes) */}
        <g stroke="url(#neon-blue-purple)" strokeWidth="1.2" opacity="0.85" filter="url(#glow-purple)" className="anim-mesh-lines">
          {/* Vertical Center Lines */}
          <line x1="150" y1="90" x2="150" y2="130" />
          <line x1="150" y1="130" x2="150" y2="164" />
          <line x1="150" y1="164" x2="150" y2="182" />
          <line x1="150" y1="182" x2="150" y2="215" />

          {/* Forehead mesh */}
          <line x1="150" y1="90" x2="168" y2="105" />
          <line x1="168" y1="105" x2="178" y2="120" />
          <line x1="150" y1="130" x2="168" y2="105" />

          {/* Temple / Eye area mesh */}
          <line x1="178" y1="120" x2="164" y2="142" />
          <line x1="168" y1="105" x2="164" y2="142" />
          <line x1="150" y1="130" x2="164" y2="142" />
          
          {/* Outer temple to outer cheek */}
          <line x1="178" y1="120" x2="192" y2="150" />
          <line x1="164" y1="142" x2="192" y2="150" />

          {/* Cheek mesh */}
          <line x1="164" y1="142" x2="172" y2="165" />
          <line x1="150" y1="164" x2="172" y2="165" />
          <line x1="192" y1="150" x2="172" y2="165" />
          
          {/* Jaw mesh */}
          <line x1="192" y1="150" x2="185" y2="185" />
          <line x1="172" y1="165" x2="185" y2="185" />
          <line x1="172" y1="165" x2="168" y2="195" />
          <line x1="150" y1="182" x2="162" y2="182" />
          <line x1="172" y1="165" x2="162" y2="182" />
          <line x1="162" y1="182" x2="168" y2="195" />
          
          {/* Chin & lower neck mesh */}
          <line x1="162" y1="182" x2="150" y2="215" />
          <line x1="168" y1="195" x2="150" y2="215" />
          <line x1="185" y1="185" x2="168" y2="195" />
          
          {/* Right neck */}
          <line x1="168" y1="195" x2="175" y2="210" />
          <line x1="175" y1="210" x2="150" y2="228" />

          {/* Right ear outline lines */}
          <line x1="192" y1="147" x2="199" y2="155" />
          <line x1="199" y1="155" x2="192" y2="163" />
        </g>

        {/* Right closed eye (Serene arc) */}
        <path 
          d="M 158 142 Q 166 147 174 142" 
          stroke="#8b5cf6" 
          strokeWidth="3" 
          fill="none" 
          strokeLinecap="round"
          filter="url(#glow-purple)"
          className="anim-face-features"
        />

        {/* Mesh Nodes (Key Facial Coordinates) */}
        <g fill="#22d3ee" filter="url(#glow-cyan)" className="anim-mesh-nodes">
          <circle cx="150" cy="90" r="3.5" />
          <circle cx="168" cy="105" r="3.5" />
          <circle cx="178" cy="120" r="3.5" />
          <circle cx="192" cy="150" r="3.5" />
          <circle cx="164" cy="142" r="3" />
          <circle cx="172" cy="165" r="3.5" />
          <circle cx="150" cy="164" r="3.5" />
          <circle cx="185" cy="185" r="3.5" />
          <circle cx="168" cy="195" r="3.5" />
          <circle cx="162" cy="182" r="3" />
          <circle cx="150" cy="215" r="3.5" />
          
          {/* Extra violet node on right cheek edge for premium accent */}
          <circle cx="199" cy="155" r="3" fill="#a855f7" filter="url(#glow-purple)" />
        </g>


        {/* ========================================== */}
        {/* LAYER 5: CIRCUIT RAYS ON THE LEFT          */}
        {/* ========================================== */}
        <g stroke="#22d3ee" strokeWidth="2.5" fill="none" strokeLinecap="round" filter="url(#glow-cyan)" className="anim-rays">
          {/* Ray 1 (Top Left) */}
          <path d="M 108 120 H 80 L 60 100 H 42" />
          {/* Ray 2 (Mid-Top Left) */}
          <path d="M 108 138 H 75 L 55 118 H 22" />
          {/* Ray 3 (Middle Left) */}
          <path d="M 110 152 H 70 L 50 172 H 28" />
          {/* Ray 4 (Mid-Bottom Left) */}
          <path d="M 112 168 H 65 L 45 188 H 18" />
          {/* Ray 5 (Bottom Left) */}
          <path d="M 118 184 H 60 L 40 204 H 32" />
        </g>
        
        {/* Circuit Ray Terminal Pads (Circles) */}
        <g fill="#22d3ee" filter="url(#glow-cyan)" className="anim-rays">
          <circle cx="42" cy="100" r="3" />
          <circle cx="22" cy="118" r="3" />
          <circle cx="28" cy="172" r="3" />
          <circle cx="18" cy="188" r="3" />
          <circle cx="32" cy="204" r="3" />
        </g>


        {/* ========================================== */}
        {/* LAYER 6: VERIFIED BADGE (BOTTOM-RIGHT)     */}
        {/* ========================================== */}
        
        {/* Badge Outer Shadow & Metallic Ring */}
        <g className="anim-badge">
          <circle cx="230" cy="220" r="25" fill="#070c14" />
          <circle cx="230" cy="220" r="23" stroke="url(#metallic-grad)" strokeWidth="4" fill="none" />
          {/* Inner Glowing Badge Ring */}
          <circle cx="230" cy="220" r="19" stroke="#22d3ee" strokeWidth="2.2" fill="#040810" filter="url(#glow-cyan)" />
        </g>

        {/* Checkmark Tick inside badge */}
        <path 
          d="M 221 220 L 227 226 L 240 213" 
          stroke="#00ffff" 
          strokeWidth="4" 
          fill="none" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          filter="url(#glow-cyan)"
          className="anim-tick"
        />


        {/* ========================================== */}
        {/* LAYER 7: HOVER EFFECTS (LASER SCAN SWEEP)   */}
        {/* ========================================== */}
        {/* Horizontal scan line, only visible when hovered */}
        <line 
          x1="80" 
          y1="90" 
          x2="220" 
          y2="90" 
          stroke="#00ffff" 
          strokeWidth="2.5" 
          opacity="0" 
          filter="url(#glow-cyan)"
          className="laser-scanner"
        />
      </svg>

      {/* Styled animation keyframes embedded locally */}
      <style>
        {`
        /* Load Animation Timings & Controls */
        
        /* 1. Circle Animation */
        .anim-circle-large {
          stroke-dasharray: 750;
          stroke-dashoffset: 750;
          animation: drawPath 1.2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        
        .anim-circle-small {
          stroke-dasharray: 100;
          stroke-dashoffset: 100;
          animation: drawPath 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.4s forwards;
        }

        .anim-orbit-dot {
          opacity: 0;
          transform: scale(0);
          transform-origin: 240px 48px;
          animation: popScale 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 1.2s forwards, orbitPulse 2s infinite ease-in-out 1.7s;
        }

        /* 2. Corner Brackets Animation */
        .anim-corners {
          opacity: 0;
          animation: fadeIn 0.6s ease-out 1.2s forwards;
        }

        /* 3. Face Left Outline and Features Trace */
        .anim-face-shading {
          opacity: 0;
          animation: fadeIn 1.2s ease-in-out 2.4s forwards;
        }

        .anim-face-left {
          stroke-dasharray: 400;
          stroke-dashoffset: 400;
          animation: drawPath 1.6s cubic-bezier(0.25, 1, 0.5, 1) 1.8s forwards;
        }

        .anim-face-features {
          stroke-dasharray: 100;
          stroke-dashoffset: 100;
          animation: drawPath 1.0s ease-out 2.2s forwards;
        }

        /* Face Mesh Lines & Nodes */
        .anim-mesh-lines {
          opacity: 0;
          animation: fadeIn 1.2s ease-out 2.2s forwards;
        }

        .anim-mesh-nodes circle {
          transform: scale(0);
          transform-origin: 150px 150px;
          animation: popScale 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        
        /* Node specific stagger delays */
        .anim-mesh-nodes circle:nth-child(1) { animation-delay: 2.5s; transform-origin: 150px 90px; }
        .anim-mesh-nodes circle:nth-child(2) { animation-delay: 2.6s; transform-origin: 168px 105px; }
        .anim-mesh-nodes circle:nth-child(3) { animation-delay: 2.7s; transform-origin: 178px 120px; }
        .anim-mesh-nodes circle:nth-child(4) { animation-delay: 2.8s; transform-origin: 192px 150px; }
        .anim-mesh-nodes circle:nth-child(5) { animation-delay: 2.9s; transform-origin: 164px 142px; }
        .anim-mesh-nodes circle:nth-child(6) { animation-delay: 3.0s; transform-origin: 172px 165px; }
        .anim-mesh-nodes circle:nth-child(7) { animation-delay: 3.1s; transform-origin: 150px 164px; }
        .anim-mesh-nodes circle:nth-child(8) { animation-delay: 3.2s; transform-origin: 185px 185px; }
        .anim-mesh-nodes circle:nth-child(9) { animation-delay: 3.3s; transform-origin: 168px 195px; }
        .anim-mesh-nodes circle:nth-child(10) { animation-delay: 3.4s; transform-origin: 162px 182px; }
        .anim-mesh-nodes circle:nth-child(11) { animation-delay: 3.5s; transform-origin: 150px 215px; }
        .anim-mesh-nodes circle:nth-child(12) { animation-delay: 3.5s; transform-origin: 199px 155px; }

        /* 4. Left Circuit Rays & Checked Badge */
        .anim-rays {
          stroke-dasharray: 120;
          stroke-dashoffset: 120;
          animation: drawPath 1.2s cubic-bezier(0.16, 1, 0.3, 1) 3.5s forwards;
        }
        
        .anim-badge {
          transform: scale(0);
          transform-origin: 230px 220px;
          animation: popScale 0.8s cubic-bezier(0.34, 1.7, 0.64, 1) 3.8s forwards;
        }

        .anim-tick {
          stroke-dasharray: 40;
          stroke-dashoffset: 40;
          animation: drawPath 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 4.4s forwards;
        }

        /* Interactive Hover Effects */
        .group:hover .laser-scanner {
          opacity: 1;
          animation: laserSweep 2.5s ease-in-out infinite;
        }

        .group:hover .anim-mesh-nodes circle {
          animation: nodePulse 1.2s infinite ease-in-out alternate;
        }
        
        /* Node pulse staggered animations */
        .group:hover .anim-mesh-nodes circle:nth-child(2n) {
          animation-delay: 0.3s;
        }
        .group:hover .anim-mesh-nodes circle:nth-child(3n) {
          animation-delay: 0.6s;
        }

        /* KEYFRAMES */
        @keyframes drawPath {
          to { stroke-dashoffset: 0; }
        }

        @keyframes fadeIn {
          to { opacity: 1; }
        }

        @keyframes popScale {
          to { transform: scale(1); opacity: 1; }
        }

        @keyframes orbitPulse {
          0%, 100% { transform: scale(1); filter: drop-shadow(0 0 4px #22d3ee); }
          50% { transform: scale(1.3); filter: drop-shadow(0 0 10px #22d3ee); }
        }

        @keyframes laserSweep {
          0% { transform: translateY(0px); opacity: 0; }
          10% { opacity: 0.85; }
          90% { opacity: 0.85; }
          100% { transform: translateY(130px); opacity: 0; }
        }

        @keyframes nodePulse {
          0% { transform: scale(1); filter: drop-shadow(0 0 1px #22d3ee); }
          100% { transform: scale(1.3); filter: drop-shadow(0 0 6px #00ffff); }
        }
        `}
      </style>
    </div>
  );
};

export default InteractiveFaceScanLogo;
