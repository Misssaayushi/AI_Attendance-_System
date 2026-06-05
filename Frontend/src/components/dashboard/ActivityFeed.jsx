import React, { useState, useEffect, useMemo } from 'react';
import { UserCheck, Clock, UserPlus, AlertTriangle, Activity } from 'lucide-react';
import { listAttendance } from '../../services/api';
import { extractData } from '../../services/apiHelpers';
import Card from '../Card';
import { useAttendanceFeed } from '../../hooks/useAttendanceFeed';

const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const { latestEvent, eventHistory } = useAttendanceFeed();
  const [toast, setToast] = useState(null);

  const fetchActivities = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await listAttendance({ 
        page: 1, 
        page_size: 10, 
        from_date: today 
      });
      const data = extractData(response);
      setActivities(data?.items || data || []);
    } catch (error) {
      console.error('Failed to load activity feed:', error);
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
    // Removed polling since we now use WebSocket
  }, []);

  useEffect(() => {
    if (latestEvent) {
      setToast(`✅ ${latestEvent.student_name} marked ${latestEvent.status}`);
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [latestEvent]);

  const allActivities = useMemo(() => {
    // Format WebSocket events to match the API data structure
    const wsActivities = eventHistory.map(e => ({
      status: e.status,
      student_id: e.student_id,
      name: e.student_name,
      timestamp: e.time || new Date().toISOString(),
      confidence: e.confidence,
    }));
    
    // Combine WS activities with fetched activities
    // (In a production app, we'd want to deduplicate by ID)
    const combined = [...wsActivities, ...activities];
    return combined.slice(0, 50); 
  }, [eventHistory, activities]);

  const getStatusConfig = (status) => {
    switch (status) {
      case 'Present':
        return {
          icon: <UserCheck size={16} />,
          badgeColor: 'bg-green-500/10 text-green-400 border border-green-500/20',
          desc: 'Attendance Marked'
        };
      case 'Late':
        return {
          icon: <Clock size={16} />,
          badgeColor: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
          desc: 'Late Arrival'
        };
      case 'Registered':
        return {
          icon: <UserPlus size={16} />,
          badgeColor: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
          desc: 'New Student Enrolled'
        };
      case 'Alert':
        return {
          icon: <AlertTriangle size={16} />,
          badgeColor: 'bg-red-500/10 text-red-400 border border-red-500/20',
          desc: 'Unknown Face Flagged'
        };
      default:
        return {
          icon: <Activity size={16} />,
          badgeColor: 'bg-gray-500/10 text-gray-400 border border-gray-500/20',
          desc: 'System Log'
        };
    }
  };

  if (loading && allActivities.length === 0) {
    return (
      <Card className="animate-pulse bg-gray-900/40 border border-gray-800/80">
        <div className="h-4 bg-gray-700 rounded w-1/4 mb-4"></div>
        <div className="space-y-3">
          <div className="h-10 bg-gray-700 rounded"></div>
          <div className="h-10 bg-gray-700 rounded"></div>
          <div className="h-10 bg-gray-700 rounded"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-full overflow-hidden border border-gray-800/80 bg-gray-900/40 p-0 relative">
      {/* Toast Notification */}
      {toast && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-gray-800 border border-gray-700 text-white text-xs px-4 py-2 rounded-lg shadow-lg animate-in slide-in-from-top-2 duration-300">
          {toast}
        </div>
      )}

      <div className="p-5 border-b border-gray-800/80 bg-gray-900/20 flex items-center justify-between">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Live Activity Feed</h3>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
        </span>
      </div>

      <div className="p-5 space-y-4 overflow-y-auto max-h-[420px] custom-scrollbar">
        {allActivities.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-gray-500 text-sm">No activity recorded yet today.</p>
          </div>
        ) : (
          allActivities.map((activity, index) => {
            const config = getStatusConfig(activity.status);
            return (
              <div 
                key={index} 
                className="flex items-start space-x-3.5 p-3.5 rounded-xl bg-gray-850/20 border border-gray-800 hover:border-gray-700 transition-colors animate-in slide-in-from-right-4 duration-300"
              >
                <div className={`p-2.5 rounded-xl ${config.badgeColor.split(' ')[0]} ${config.badgeColor.split(' ')[1]}`}>
                  {config.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start">
                    <p className="text-xs font-bold text-white truncate leading-none">
                      {activity.student ? `${activity.student.first_name} ${activity.student.last_name}` : activity.name || 'Unknown'}
                    </p>
                    <span className="text-[9px] text-gray-500 flex items-center leading-none">
                      {new Date(activity.timestamp || activity.marked_at || activity.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1 font-semibold">{config.desc}</p>
                  <div className="flex items-center mt-2.5 space-x-2">
                    <p className="text-[9px] text-gray-500 font-mono">ID: {activity.student?.roll_number || activity.student_id}</p>
                    {activity.confidence > 0 && (
                      <>
                        <span className="text-[9px] text-gray-600 font-bold">•</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold font-mono">
                          {Number(activity.confidence).toFixed(1)}% match
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};

export default ActivityFeed;
