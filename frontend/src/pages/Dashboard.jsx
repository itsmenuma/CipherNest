import React, { useState } from 'react'

const API = 'http://127.0.0.1:5000'

export default function Dashboard({ onLogout }) {
  const [file, setFile] = useState(null)
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const uploadAndDownload = async (endpoint) => {
    if (!file) return setMessage('Select a file first')
    if (!password) return setMessage('Enter password')

    setLoading(true)
    setMessage('')

    const form = new FormData()
    form.append('file', file)
    form.append('password', password)

    try {
      const res = await fetch(API + endpoint, {
        method: 'POST',
        body: form
      })

      if (!res.ok) {
        const j = await res.json().catch(() => ({ error: 'Server error' }))
        setMessage(j.error)
        return
      }

      const blob = await res.blob()
      const disposition = res.headers.get('content-disposition')
      let filename = 'download'

      if (disposition) {
        const match = disposition.match(/filename="?(.+)"?/)
        if (match) filename = match[1]
      } else {
        filename = file.name + (endpoint === '/encrypt' ? '.enc' : '')
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)

      setMessage('Downloaded ' + filename)
    } catch (err) {
      setMessage('Network error: ' + err.message)
    } finally {
      setPassword('')   // 🔥 resets password every time
      setLoading(false)
    }
  }

  return (
    <div className="card dash-card">
      <div className="brand">CipherNest</div>
      <h2>File Encryption Panel</h2>

      <div className="row">
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
      </div>

      <div className="row">
        <button disabled={loading} onClick={() => uploadAndDownload('/encrypt')}>
          Encrypt
        </button>
        <button disabled={loading} onClick={() => uploadAndDownload('/decrypt')}>
          Decrypt
        </button>
        <button className="logout-btn" onClick={onLogout}>
          Logout
        </button>
      </div>

      <div className="message">{message}</div>
    </div>
  )
}
