import React from 'react';
import Home from './pages/Home.jsx';
import {Routes, Route, BrowserRouter}  from "react-router-dom";
import './App.css';
import VerificationSuccessful from "./pages/VerificationSuccessful";
import VerificationFailed from "./pages/VerificationFailed";


function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path={"/"} element={<Home/>}/>
      <Route path={"/verification_successful"} element={<VerificationSuccessful/>}/>
      <Route path={"/verification_failed"} element={<VerificationFailed/>}/>
    </Routes>
    </BrowserRouter>
  );
}

export default App;
