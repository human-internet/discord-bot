import React, {useEffect} from 'react';
import {useSearchParams} from "react-router-dom";
import './Verification.css';

function startLoginProcess(verificationLink) {
  window.location.href = verificationLink;
}

function Home() {
  const [searchParams] = useSearchParams();

  const loginURL = searchParams.get('url');
  const server = searchParams.get('server');    

  useEffect(()=> {
    localStorage.setItem("server", server);
    startLoginProcess(loginURL);
  },[loginURL, server]);

  return (
    <header className="App-header">
      <h4 className='instructions'>
        Please verify via humanID
      </h4>
    </header>
  );
}

export default Home;
