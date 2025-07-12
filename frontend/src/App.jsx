import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter,Routes,Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LoginSignUp from './pages/LoginSignUp'
function App() {
  const [count, setCount] = useState(0)

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element = {<LandingPage/>}/>
        <Route path='/login' element = {<LoginSignUp/>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
