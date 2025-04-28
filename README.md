# Philosophy AI Frontend

This is the frontend application for the Philosophy AI project, a web application that allows users to chat with AI-powered philosophical characters.

## Features

- User authentication (login/register)
- Dashboard with philosopher selection
- Chat interface with AI philosophers
- Chat history management
- Responsive design for mobile and desktop

## Tech Stack

- React.js
- Material UI for components and styling
- React Router for navigation
- Axios for API requests
- JWT for authentication

## Project Structure

```
src/
  ├── api/          # API service functions
  ├── assets/       # Static assets like images
  ├── components/   # Reusable UI components
  ├── contexts/     # React contexts for state management
  ├── pages/        # Page components
  ├── theme/        # Theme configuration
  ├── utils/        # Utility functions
  ├── App.js        # Main App component
  └── index.js      # Entry point
```

## Setup Instructions

1. Make sure you have Node.js and npm installed
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```
4. The application will be available at http://localhost:3000

## Backend API

The frontend connects to a Django REST API running at http://localhost:8000/api/. Make sure the backend server is running before using the frontend application.

## Building for Production

To create a production build:

```
npm run build
```

The build artifacts will be stored in the `build/` directory.