import React from 'react'
import ReactDOM from 'react-dom/client'

import './styles/global.css'
import { App } from './App' // 後で作成するメインコンポーネント

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
