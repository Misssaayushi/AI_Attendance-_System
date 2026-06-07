import { useState, useEffect } from 'react';
import { attendanceWS } from '../services/websocket';

export function useAttendanceFeed() {
  const [latestEvent, setLatestEvent] = useState(null);
  const [eventHistory, setEventHistory] = useState([]);

  useEffect(() => {
    attendanceWS.connect();

    const unsubscribe = attendanceWS.subscribe((event) => {
      if (event.type === 'attendance_marked') {
        setLatestEvent(event);
        setEventHistory(prev => [event, ...prev].slice(0, 50)); // Keep last 50
      }
    });

    return () => {
      unsubscribe();
      attendanceWS.disconnect();
    };
  }, []);

  return { latestEvent, eventHistory };
}
