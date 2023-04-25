import React from 'react';
import RequestProcessor from './components/RequestProcessor.jsx';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import './App.css';


function App() { 
  const [uid, setuid] = React.useState('');

  const type = (event) => {
    const {value} = event.target;
    setuid(value);
  }
    
  const clicked = () => {
    if (!uid) {
      alert('Please enter your user id');
    } else {
      test(uid);
    }
  }

  return (
    <BrowserRouter>
    <Routes>
      <Route path={"/"} element={<RequestProcessor/>}/>
    </Routes>
    </BrowserRouter>
  );
}

export default App;
