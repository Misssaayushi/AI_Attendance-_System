import React, { useRef, useState, useEffect } from 'react';
import { Camera, CameraOff, Scissors, RefreshCw } from 'lucide-react';
import Button from '../Button';

const WebcamFeed = ({ onCapture, onStreamStart, onStreamStop, onError, autoStart = false, autoInterval = 0, onLiveFrame }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [isCaptured, setIsCaptured] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureProgress, setCaptureProgress] = useState(0);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720, facingMode: 'user' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsActive(true);
        if (onStreamStart) onStreamStart(stream);
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      if (onError) onError(err.name === 'NotAllowedError' ? 'Permission Denied' : 'Camera Unavailable');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsActive(false);
      if (onStreamStop) onStreamStop();
    }
  };

  const captureFrame = async () => {
    if (videoRef.current) {
      setIsCapturing(true);
      const frames = [];
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const ctx = canvas.getContext('2d');

      for (let i = 0; i < 5; i++) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        frames.push(canvas.toDataURL('image/jpeg'));
        setCaptureProgress(i + 1);
        if (i < 4) await new Promise(r => setTimeout(r, 500));
      }
      
      setIsCapturing(false);
      setIsCaptured(true);
      if (onCapture) onCapture(frames);

      // Draw the first frame to the DOM canvas once it's mounted
      setTimeout(() => {
        if (canvasRef.current) {
          const domCanvas = canvasRef.current;
          domCanvas.width = canvas.width;
          domCanvas.height = canvas.height;
          const domCtx = domCanvas.getContext('2d');
          const img = new Image();
          img.onload = () => {
            domCtx.drawImage(img, 0, 0, domCanvas.width, domCanvas.height);
          };
          img.src = frames[0];
        }
      }, 100);
    }
  };

  const retake = () => {
    setIsCaptured(false);
    setCaptureProgress(0);
    if (onCapture) onCapture(null);
  };

  const captureSingleFrame = () => {
    if (videoRef.current && isActive && !isCapturing) {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/jpeg', 0.8);
    }
    return null;
  };

  useEffect(() => {
    if (autoStart) {
      startCamera();
    }
    return () => stopCamera();
  }, []);

  useEffect(() => {
    let interval;
    if (isActive && autoInterval && onLiveFrame) {
      interval = setInterval(() => {
        const frame = captureSingleFrame();
        if (frame) {
          onLiveFrame(frame);
        }
      }, autoInterval);
    }
    return () => clearInterval(interval);
  }, [isActive, autoInterval, onLiveFrame]);

  return (
    <div className="space-y-4">
      <div className={`relative aspect-video bg-black rounded-xl overflow-hidden border-2 border-gray-700 shadow-2xl group ${isCaptured ? 'ring-4 ring-green-500/50' : ''}`}>
        {!isActive && !isCaptured && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 space-y-4">
            <div className="p-6 bg-gray-800 rounded-full">
              <CameraOff size={48} />
            </div>
            <p className="font-medium">Camera is currently inactive</p>
          </div>
        )}

        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          className={`w-full h-full object-cover ${isActive && !isCaptured ? 'block' : 'hidden'}`}
        />

        {isCaptured && (
          <canvas ref={canvasRef} className="w-full h-full object-cover block animate-in fade-in zoom-in-95 duration-300" />
        )}

        {/* Face Guide Overlay */}
        {isActive && !isCaptured && (
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div className="w-64 h-80 border-2 border-blue-500/30 border-dashed rounded-[100px] relative">
               <div className="absolute inset-0 bg-blue-500/5 rounded-[100px]"></div>
            </div>
          </div>
        )}

        {/* Status Badge */}
        {isActive && !isCapturing && (
          <div className="absolute top-4 right-4 bg-gray-900/80 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-2 border border-gray-700">
            <span className={`w-2 h-2 rounded-full ${isCaptured ? 'bg-green-500' : 'bg-blue-500 animate-pulse'}`}></span>
            <span className="text-gray-200">{isCaptured ? 'Face Captured' : 'Live Feed'}</span>
          </div>
        )}

        {isCapturing && (
          <div className="absolute top-4 right-4 bg-yellow-900/80 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-2 border border-yellow-700">
            <span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
            <span className="text-yellow-200">Capturing {captureProgress}/5...</span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-3 justify-center">
        {!isActive && !isCaptured && !isCapturing && (
          <Button onClick={startCamera} className="flex items-center space-x-2">
            <Camera size={20} />
            <span>Start Camera</span>
          </Button>
        )}

        {isActive && !isCaptured && !isCapturing && (
          <>
            <Button variant="secondary" onClick={stopCamera} className="flex items-center space-x-2">
              <CameraOff size={20} />
              <span>Stop Camera</span>
            </Button>
            <Button onClick={captureFrame} className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white">
              <Scissors size={20} />
              <span>Capture Faces</span>
            </Button>
          </>
        )}

        {isCaptured && (
          <Button variant="outline" onClick={retake} className="flex items-center space-x-2 border-blue-500 text-blue-400 hover:bg-blue-500/10">
            <RefreshCw size={20} />
            <span>Retake Photo</span>
          </Button>
        )}
      </div>
    </div>
  );
};

export default WebcamFeed;
