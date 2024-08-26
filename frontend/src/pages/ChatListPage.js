import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function ChatListPage() {
  const [chats, setChats] = useState([]);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [activeUsers, setActiveUsers] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const userId = sessionStorage.getItem('userId');
  const username = sessionStorage.getItem('username');

  useEffect(() => {
    if (!userId) {
      navigate('/');
    } else {
      fetchChats();
      fetchActiveUsers();
    }
  }, [userId, navigate]);

  const fetchChats = async () => {
    try {
      const response = await axios.get('${process.env.REACT_APP_API_URL}/v1/chat/', {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setChats(response.data);
    } catch (err) {
      setError('Failed to fetch chat rooms. Please try again.');
      console.error(err);
    }
  };

  const fetchActiveUsers = async () => {
    try {
      const response = await axios.get('${process.env.REACT_APP_API_URL}/v1/user/active', {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setActiveUsers(response.data);
    } catch (err) {
      setError('Failed to fetch active users. Please try again.');
      console.error(err);
    }
  };

  const createNewChat = async (e) => {
    e.preventDefault();
    if (newChatTitle.trim()) {
      try {
        const response = await axios.post('${process.env.REACT_APP_API_URL}/v1/chat/', {
          title: newChatTitle
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        setChats([...chats, response.data]);
        setNewChatTitle('');
      } catch (err) {
        setError('Failed to create new chat room. Please try again.');
        console.error(err);
      }
    }
  };

  const deleteChat = async (chatId) => {
    try {
      await axios.delete(`${process.env.REACT_APP_API_URL}/v1/chat/${chatId}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setChats(chats.filter(chat => chat.id !== chatId));
    } catch (err) {
      setError('Failed to delete chat room. Please try again.');
      console.error(err);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <h2 style={styles.sidebarTitle}>채팅방 생성하기</h2>
        <form onSubmit={createNewChat} style={styles.form}>
          <input
            type="text"
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
            placeholder="Enter chat title"
            style={styles.input}
          />
          <button type="submit" style={styles.button}>Create Chat</button>
        </form>
        <h2 style={styles.sidebarTitle}>최근 활동한 유저</h2>
        <ul style={styles.activeUsersList}>
          {activeUsers.map(user => (
            <li key={user.id} style={styles.activeUserItem}>
              <i className="fas fa-user" style={styles.userIcon}></i>
              {user.username} {user.last_active}
            </li>
          ))}
        </ul>
      </div>
      <div style={styles.main}>
        <h1 style={styles.mainTitle}>Welcome, {username}</h1>
        <h2 style={styles.mainSubtitle}>Chat Rooms</h2>
        {error && <p style={styles.error}>{error}</p>}
        <ul style={styles.chatList}>
          {chats.map(chat => (
            <li key={chat.id} style={styles.chatItem}>
              <Link to={`/chat/${chat.id}`} style={styles.chatLink}>
                <h3 style={styles.chatTitle}>{chat.title}</h3>
                <p style={styles.chatMeta}>Created at: {new Date(chat.created_at).toLocaleString()}</p>
              </Link>
              <button 
                onClick={() => deleteChat(chat.id)} 
                style={styles.deleteButton}
              >
                Delete
              </button>
            </li>
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
    backgroundColor: '#f4f4f9',
    fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
  },
  sidebar: {
    width: '300px',
    padding: '1.5rem',
    backgroundColor: '#fff',
    boxShadow: '2px 0 5px rgba(0, 0, 0, 0.1)',
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  sidebarTitle: {
    fontSize: '1.25rem',
    color: '#333',
    marginBottom: '0.75rem',
    borderBottom: '2px solid #1a73e8',
    paddingBottom: '0.5rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '5px',
    border: '1px solid #ddd',
    fontSize: '1rem',
    marginBottom: '1rem',
  },
  button: {
    padding: '0.75rem',
    backgroundColor: '#1a73e8',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
activeUsersList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  activeUserItem: {
    padding: '0.5rem',
    borderBottom: '1px solid #eee',
    display: 'flex',
    alignItems: 'center',
  },
  userIcon: {
    marginRight: '0.5rem',
    color: '#1a73e8',
  },
  main: {
    flex: 1,
    padding: '2rem',
    overflowY: 'auto',
  },
  mainTitle: {
    fontSize: '2rem',
    color: '#1a73e8',
    marginBottom: '1rem',
  },
  mainSubtitle: {
    fontSize: '1.5rem',
    color: '#333',
    marginBottom: '1rem',
    borderBottom: '2px solid #1a73e8',
    paddingBottom: '0.5rem',
  },
  error: {
    color: 'red',
    marginBottom: '1rem',
  },
  chatList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  chatItem: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
  },
  chatLink: {
    flex: 1,
    textDecoration: 'none',
    color: 'inherit',
  },
  chatTitle: {
    fontSize: '1.25rem',
    color: '#1a73e8',
  },
  chatMeta: {
    color: '#666',
    fontSize: '0.875rem',
  },
  deleteButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#ff4d4f',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
    marginLeft: '1rem',
  },
};

export default ChatListPage;
