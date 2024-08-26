import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function ChatRoomPage() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [connectedUsers, setConnectedUsers] = useState(0);
  const [activeUsers, setActiveUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [roomName, setRoomName] = useState('');
  const { id } = useParams();
  const navigate = useNavigate();
  const userId = sessionStorage.getItem('userId');
  const username = sessionStorage.getItem('username');
  const websocket = useRef(null);
  const messagesEndRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const isInitialMount = useRef(true);

  const fetchRoomInfo = useCallback(async () => {
    try {
      const response = await axios.get(`http://192.168.219.103:8000/v1/chat/${id}`);
      setRoomName(response.data.title);
    } catch (error) {
      console.error('Error fetching room info:', error);
      setRoomName('Unknown Room');
    }
  }, [id]);

  const fetchActiveUsers = useCallback(async () => {
    try {
      const response = await axios.get(`http://192.168.219.103:8000/v1/chat/${id}/users`);
      setActiveUsers(response.data);
    } catch (error) {
      console.error('Error fetching active users:', error);
    }
  }, [id]);

  const disconnectWebSocket = useCallback(() => {
    if (websocket.current) {
      websocket.current.close();
      websocket.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const connectWebSocket = useCallback(() => {
    if (websocket.current?.readyState === WebSocket.OPEN) {
      return;
    }

    websocket.current = new WebSocket(`ws://192.168.219.103:8000/ws/room/${id}/messages/${userId}`);

    websocket.current.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
      fetchActiveUsers();
    };

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    websocket.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    websocket.current.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        connectWebSocket();
      }, 3000);
    };
  }, [id, userId, fetchActiveUsers]);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      if (userId && username) {
        fetchRoomInfo();
        connectWebSocket();
      } else {
        navigate('/');
      }
    }

    return () => {
      console.log('Cleaning up WebSocket connection');
      disconnectWebSocket();
    };
  }, [userId, username, navigate, connectWebSocket, fetchRoomInfo, disconnectWebSocket]);

  const handleWebSocketMessage = useCallback((data) => {
    if (isMessageDuplicate(data)) {
      return;
    }

    switch(data.type) {
      case 'user_join':
      case 'user_leave':
        setConnectedUsers(data.connected_users_count);
        setMessages(prevMessages => [...prevMessages, { type: 'system', content: data.message, id: Date.now() }]);
        fetchActiveUsers();
        break;
      default:
        if (data.message) {
          setMessages(prevMessages => [...prevMessages, {
            type: 'message',
            content: data.message,
            sender_name: data.sender_name,
            is_self: data.sender_name === username,
            id: Date.now()
          }]);
        }
    }
  }, [username, fetchActiveUsers]);

  const isMessageDuplicate = useCallback((data) => {
    return messages.some(msg => 
      msg.type === data.type && 
      msg.content === data.message && 
      Date.now() - msg.id < 1000
    );
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() && websocket.current?.readyState === WebSocket.OPEN) {
      const message = {
        message: newMessage
      };
      websocket.current.send(JSON.stringify(message));
      setNewMessage('');
    }
  };

  const leaveChatRoom = useCallback(() => {
    disconnectWebSocket();
    navigate('/chat-list');
  }, [disconnectWebSocket, navigate]);

  return (
    <div style={styles.container}>
      <div style={styles.chatArea}>
        <div style={styles.header}>
          <h2 style={styles.title}>{`${roomName} Room` || `Chat Room `}</h2>
          <button onClick={leaveChatRoom} style={styles.leaveButton}>Leave Room</button>
        </div>
        <div style={styles.messageContainer}>
          {messages.map((message, index) => (
            <div 
              key={message.id || index} 
              style={
                message.type === 'system' 
                  ? styles.systemMessage 
                  : (message.is_self ? styles.myMessage : styles.otherMessage)
              }
            >
              {message.type !== 'system' && (
                <div style={styles.messageHeader}>
                  <span style={styles.username}>{message.sender_name}</span>
                </div>
              )}
              <div style={styles.messageContent}>{message.content}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={sendMessage} style={styles.form}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            style={styles.input}
          />
          <button type="submit" style={styles.button} disabled={!isConnected}>Send</button>
        </form>
      </div>
      <div style={styles.userPanel}>
        <h3>Chat Information</h3>
        <p style={styles.username}>User: {username}</p>
        <p style={styles.connectedUsersCount}>Connected Users: {connectedUsers}</p>
        <p style={styles.connectionStatus}>
          Status: {isConnected ? 'Connected' : 'Disconnected'}
        </p>
        <h4>Active Users:</h4>
        <ul style={styles.userList}>
          {activeUsers.map(user => (
            <li key={user.id} style={styles.userItem}>{user.username}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '1rem',
    backgroundColor: '#f0f2f5',
  },
  chatArea: {
    flex: 3,
    display: 'flex',
    flexDirection: 'column',
    marginRight: '1rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  title: {
    color: '#1a73e8',
    margin: 0,
  },
  messageContainer: {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '1rem',
    padding: '1rem',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  systemMessage: {
    textAlign: 'center',
    backgroundColor: '#e1e1e1',
    borderRadius: '8px',
    padding: '0.5rem',
    marginBottom: '0.5rem',
    fontSize: '0.9rem',
    color: '#555',
  },
  myMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#dcf8c6',
    borderRadius: '8px',
    padding: '0.5rem',
    marginBottom: '0.5rem',
    maxWidth: '70%',
    marginLeft: 'auto',
  },
  otherMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#f0f0f0',
    borderRadius: '8px',
    padding: '0.5rem',
    marginBottom: '0.5rem',
    maxWidth: '70%',
  },
  messageHeader: {
    marginBottom: '0.25rem',
  },
  username: {
    fontWeight: 'bold',
    fontSize: '1rem',
    color: '#1a73e8',
    margin: '0.5rem 0',
  },
  messageContent: {
    wordBreak: 'break-word',
  },
  form: {
    display: 'flex',
    marginTop: '1rem',
  },
  input: {
    flex: 1,
    padding: '0.75rem',
    marginRight: '1rem',
    borderRadius: '20px',
    border: '1px solid #ccc',
    fontSize: '1rem',
  },
  button: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#1a73e8',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  leaveButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#ff4d4f',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  userPanel: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '1rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'flex-start',
  },
  connectedUsersCount: {
    fontSize: '1rem',
    color: '#666',
    margin: '0.5rem 0',
  },
  connectionStatus: {
    fontSize: '1rem',
    color: '#666',
    margin: '0.5rem 0',
  },
  userList: {
    listStyleType: 'none',
    padding: 0,
    margin: '0.5rem 0',
    maxHeight: '150px',
    overflowY: 'auto',
    width: '100%',
  },
  userItem: {
    padding: '0.25rem 0',
    borderBottom: '1px solid #eee',
  },
};

export default ChatRoomPage;