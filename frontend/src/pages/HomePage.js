import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function HomePage() {
  const [username, setUsername] = useState('');
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // 페이지 로드 시 세션 스토리지의 유저 정보 삭제
    sessionStorage.removeItem('userId');
    sessionStorage.removeItem('username');
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (username.trim()) {
      try {
        const response = await axios.post('http://192.168.219.103:8000/v1/user/', {
          username: username
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        setUser(response.data);
        sessionStorage.setItem('userId', response.data.id);
        sessionStorage.setItem('username', response.data.username);
      } catch (err) {
        if (err.response && err.response.data && err.response.data.username) {
          setError(`Username error: ${err.response.data.username[0]}`);
        } else {
          setError('Failed to create user. Please try again.');
        }
        console.error(err);
      }
    }
  };

  const goToChatList = () => {
    navigate('/chat-list');
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Welcome to Chat App</h1>
        {!user ? (
          <form onSubmit={handleSubmit} style={styles.form}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              style={styles.input}
            />
            <button type="submit" style={styles.button}>
              Create User
            </button>
            {error && <p style={styles.error}>{error}</p>}
          </form>
        ) : (
          <div style={styles.userInfo}>
            <h2>Welcome, {user.username}!</h2>
            <p>Your ID: {user.id}</p>
            <p>Connected at: {new Date(user.connected_at).toLocaleString()}</p>
            <button onClick={goToChatList} style={styles.button}>
              Go to Chat List
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#f0f2f5',
  },
  card: {
    background: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
    maxWidth: '400px',
    width: '100%',
  },
  title: {
    color: '#1a73e8',
    marginBottom: '1.5rem',
    fontSize: '2rem',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
  },
  input: {
    padding: '0.75rem',
    marginBottom: '1rem',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '1rem',
  },
  button: {
    padding: '0.75rem',
    backgroundColor: '#1a73e8',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  error: {
    color: 'red',
    marginTop: '1rem',
  },
  userInfo: {
    textAlign: 'left',
    marginTop: '1rem',
  },
};

export default HomePage;