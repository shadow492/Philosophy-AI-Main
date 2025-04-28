import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Avatar,
  IconButton,
  Divider,
  CircularProgress,
  AppBar,
  Toolbar,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Drawer,
  useMediaQuery,
  useTheme,
  Alert
} from '@mui/material';
import {
  Send,
  ArrowBack,
  Menu as MenuIcon,
  MoreVert,
  History,
  Refresh,
  Settings,
  Logout
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { getChatSession, sendMessage, getChatSessions, getPhilosopher } from '../api/api';

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

const Chat = () => {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [philosopher, setPhilosopher] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [chatSessions, setChatSessions] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  
  const messagesEndRef = useRef(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Fetch chat session data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [sessionResponse, sessionsResponse] = await Promise.all([
          getChatSession(sessionId),
          getChatSessions()
        ]);
        
        setSession(sessionResponse.data);
        setChatSessions(sessionsResponse.data);
        
        // Get philosopher details
        const philosopherResponse = await getPhilosopher(sessionResponse.data.philosopher);
        setPhilosopher(philosopherResponse.data);
        
        // Extract messages from session
        if (sessionResponse.data.messages) {
          setMessages(sessionResponse.data.messages);
        }
      } catch (err) {
        console.error('Error fetching chat data:', err);
        setError('Failed to load chat. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [sessionId]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    try {
      setSending(true);
      setError('');
      
      // Add user message to UI immediately
      const userMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: input,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      
      // Send message to API
      const response = await sendMessage(sessionId, input);
      
      // Add AI response to messages
      if (response.data && response.data.response) {
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleMenuOpen = (event) => {
    setMenuAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };
  
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };
  
  const switchToSession = (id) => {
    navigate(`/chat/${id}`);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };
  
  // Render message bubbles
  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    const isSystem = message.role === 'system';
    
    if (isSystem) {
      return (
        <Box sx={{ textAlign: 'center', my: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {message.content}
          </Typography>
        </Box>
      );
    }
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        {!isUser && (
          <Avatar
            src={philosopher ? getPhilosopherImage(philosopher.id) : ''}
            sx={{ mr: 1, alignSelf: 'flex-end' }}
          />
        )}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            borderRadius: 2,
            backgroundColor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
          }}
        >
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.content}
          </Typography>
          <Typography variant="caption" color={isUser ? 'rgba(255,255,255,0.7)' : 'text.secondary'} sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>
        </Paper>
        {isUser && (
          <Avatar
            sx={{ ml: 1, alignSelf: 'flex-end', bgcolor: 'primary.dark' }}
          >
            {user?.username?.charAt(0).toUpperCase()}
          </Avatar>
        )}
      </Box>
    );
  };
  
  // Render chat sessions sidebar
  const chatSessionsList = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">Chat History</Typography>
        {isMobile && (
          <IconButton onClick={handleDrawerToggle}>
            <ArrowBack />
          </IconButton>
        )}
      </Box>
      <Divider />
      <List>
        {chatSessions.map((chatSession) => (
          <ListItem
            button
            key={chatSession.id}
            selected={chatSession.id === sessionId}
            onClick={() => switchToSession(chatSession.id)}
          >
            <ListItemAvatar>
              <Avatar src={getPhilosopherImage(chatSession.philosopher)} />
            </ListItemAvatar>
            <ListItemText
              primary={chatSession.summary || 'Chat with ' + chatSession.philosopher}
              secondary={new Date(chatSession.updated_at).toLocaleDateString()}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
  
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Chat sessions sidebar - persistent on desktop, drawer on mobile */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
        >
          {chatSessionsList}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            width: 250,
            flexShrink: 0,
            '& .MuiDrawer-paper': { width: 250, boxSizing: 'border-box' },
          }}
          open
        >
          {chatSessionsList}
        </Drawer>
      )}
      
      {/* Main chat area */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* App bar */}
        <AppBar position="static" color="transparent" elevation={1}>
          <Toolbar>
            {isMobile && (
              <IconButton
                edge="start"
                color="inherit"
                onClick={handleDrawerToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            
            <IconButton color="inherit" onClick={handleBackToDashboard} sx={{ mr: 1 }}>
              <ArrowBack />
            </IconButton>
            
            {philosopher && (
              <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
                <Avatar src={getPhilosopherImage(philosopher.id)} sx={{ mr: 1 }} />
                <Typography variant="h6">{philosopher.name}</Typography>
              </Box>
            )}
            
            <IconButton color="inherit" onClick={handleMenuOpen}>
              <MoreVert />
            </IconButton>
            
            <Menu
              anchorEl={menuAnchorEl}
              open={Boolean(menuAnchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem onClick={handleBackToDashboard}>
                Dashboard
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                <Logout fontSize="small" sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        
        {/* Chat messages */}
        <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto', bgcolor: 'background.default' }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : (
            <>
              {messages.map((message) => (
                <Box key={message.id}>
                  {renderMessage(message)}
                </Box>
              ))}
              {sending && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>
        
        {/* Message input */}
        <Box sx={{ p: 2, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Type your message..."
              variant="outlined"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sending || loading}
              multiline
              maxRows={4}
              sx={{ mr: 1 }}
            />
            <Button
              variant="contained"
              color="primary"
              endIcon={<Send />}
              onClick={handleSendMessage}
              disabled={!input.trim() || sending || loading}
            >
              Send
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
            This is AI and not a real person. Treat everything it says as fiction.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Chat;