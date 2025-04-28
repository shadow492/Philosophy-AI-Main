import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  AppBar,
  Toolbar,
  CircularProgress,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  Alert
} from '@mui/material';
import { AccountCircle, Logout, Add, Search } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { getPhilosophers, createChatSession, getChatSessions } from '../api/api';

// Placeholder images for philosophers
const getPhilosopherImage = (id) => {
  const images = {
    'marcus_aurelius': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Marcus_Aurelius_Metropolitan_Museum.png/440px-Marcus_Aurelius_Metropolitan_Museum.png',
    'nietzsche': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Nietzsche187a.jpg/440px-Nietzsche187a.jpg',
    'kafka': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Kafka1906_cropped.jpg/440px-Kafka1906_cropped.jpg',
    'default': 'https://via.placeholder.com/150'
  };
  return images[id] || images.default;
};

const Dashboard = () => {
  const [philosophers, setPhilosophers] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // Fetch philosophers and chat sessions on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [philosophersResponse, sessionsResponse] = await Promise.all([
          getPhilosophers(),
          getChatSessions()
        ]);
        
        setPhilosophers(philosophersResponse.data);
        setChatSessions(sessionsResponse.data);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  const startNewChat = async (philosopherId) => {
    try {
      setLoading(true);
      const response = await createChatSession(philosopherId);
      navigate(`/chat/${response.data.id}`);
    } catch (err) {
      console.error('Error creating chat session:', err);
      setError('Failed to create chat session. Please try again.');
      setLoading(false);
    }
  };
  
  const continueChat = (sessionId) => {
    navigate(`/chat/${sessionId}`);
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" color="transparent" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Philosophy AI
          </Typography>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleProfileMenuOpen}
          >
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem disabled>
              <Typography variant="body2">{user?.username}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout fontSize="small" sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.username}
        </Typography>
        
        <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>
          For you
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {philosophers.map((philosopher) => (
              <Grid item xs={12} sm={6} md={3} key={philosopher.id}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 },
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  }}
                >
                  <CardMedia
                    component="img"
                    height="200"
                    image={getPhilosopherImage(philosopher.id)}
                    alt={philosopher.name}
                  />
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h6" component="div">
                      {philosopher.name}
                    </Typography>
                    <Button 
                      variant="contained" 
                      fullWidth 
                      onClick={() => startNewChat(philosopher.id)}
                      startIcon={<Add />}
                    >
                      Start Chat
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        
        {chatSessions.length > 0 && (
          <>
            <Typography variant="h5" sx={{ mt: 6, mb: 2 }}>
              Recent Conversations
            </Typography>
            
            <Grid container spacing={3}>
              {chatSessions.map((session) => {
                const philosopher = philosophers.find(p => p.id === session.philosopher) || {};
                return (
                  <Grid item xs={12} sm={6} md={4} key={session.id}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 },
                        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                      }}
                      onClick={() => continueChat(session.id)}
                    >
                      <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar 
                          src={getPhilosopherImage(session.philosopher)}
                          sx={{ width: 60, height: 60, mr: 2 }}
                        />
                        <Box>
                          <Typography variant="h6">{philosopher.name || session.philosopher}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(session.updated_at).toLocaleString()}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;