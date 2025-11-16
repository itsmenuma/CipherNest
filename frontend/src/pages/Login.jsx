import React, { useState } from 'react'

const API = 'http://127.0.0.1:5000'

export default function Login({ onAuth }) {
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const setup = async () => {
    try {
      const res = await fetch(API + '/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      })
      const j = await res.json()
      setMessage(res.ok ? 'Setup complete. You can log in now.' : j.error)
    } catch (err) {
      setMessage('Server error: ' + err.message)
    }
  }

  const login = async () => {
    try {
      const res = await fetch(API + '/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      })
      const j = await res.json()
      if (res.ok && j.ok) {
        onAuth()
      } else {
        setMessage('Invalid password')
      }
    } catch (err) {
      setMessage('Server error: ' + err.message)
    }
  }

  return (
    <div className="login-page">

      {/* -------- INTRO SECTION ADDED HERE -------- */}
      <div className="intro-text">
        <h1 className="title">🔐 Welcome to CipherNest</h1>
        <p className="subtitle">
          Your private, encrypted sanctuary where your files stay locked,
          protected, and untouchable.  
          CipherNest gives you a personal vault —  
          encrypt, decrypt, and guard your sensitive data with ease.
        </p>
        <p className="subtitle2">
          Built for security. Designed for simplicity.  
          Your digital safe space starts here.
        </p>
      </div>
      {/* -------- INTRO END -------- */}

      <div className="card auth-card">
        <div className="brand">CipherNest</div>
        <h2>Secure Vault Login</h2>

        <div className="row">
          <input
            type="password"
            placeholder="Enter Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>

        <div className="row">
          <button onClick={login}>Log In</button>
          <button onClick={setup}>First-Time Setup</button>
        </div>

        <div className="message">{message}</div>
      </div>
    </div>
  )
}
