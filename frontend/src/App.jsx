import React, { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  const [authenticated, setAuthenticated] = useState(false)

  useEffect(() => {
    const t = sessionStorage.getItem('auth')
    if (t === 'true') setAuthenticated(true)
  }, [])

  return (
    <div className="app">
      {!authenticated ? (
        <Login
          onAuth={() => {
            sessionStorage.setItem('auth', 'true')
            setAuthenticated(true)
          }}
        />
      ) : (
        <Dashboard
          onLogout={() => {
            sessionStorage.removeItem('auth')
            setAuthenticated(false)
          }}
        />
      )}
    </div>
  )
}

export default App
