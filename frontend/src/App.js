import React from 'react';
import logo from './logo.svg';
import './App.css';

function test(uid) {
    fetch('http://localhost:8000/api/fin/?userId=' + uid, {
        method: 'GET',
        headers: new Headers({
            'Content-Type': 'application/x-www-form-urlencoded',
        })
    })
}

function App() { 
  const [uid, setuid] = React.useState('');

  const type = (event) => {
    const {value} = event.target;
    setuid(value);
  }

  return (
    <div className="App">
      <header className="App-header">
          <button onClick={() => test(uid)}>
            click me
          </button>
        <input value={uid} onChange={type}/>
      </header>
    </div>
  );
}

export default App;
