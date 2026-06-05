class AttendanceWebSocket {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 2000;
    this.pingInterval = null;
  }

  connect() {
    // Avoid multiple connections
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/attendance';
    
    try {
      this.ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      this.attemptReconnect();
      return;
    }

    this.ws.onopen = () => {
      console.log('🔗 WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Ping every 30 seconds to keep alive
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000);
    };

    this.ws.onmessage = (event) => {
      if (event.data === 'pong') return;
      
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach(listener => listener(data));
      } catch (err) {
        console.warn('WebSocket message parse error:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      clearInterval(this.pingInterval);
      this.attemptReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
      setTimeout(() => this.connect(), delay);
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  disconnect() {
    clearInterval(this.pingInterval);
    if (this.ws) {
      // Clear handlers to prevent reconnect attempt on manual disconnect
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
  }
}

// Singleton instance
export const attendanceWS = new AttendanceWebSocket();
