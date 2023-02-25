import React from 'react';
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
    
  const clicked = () => {
    if (!uid) {
      alert('Please enter your user id');
    } else {
      test(uid);
    }
  }

  return (
    <div className="App">
      <header className="App-header">
          <div>
            <h4 style={{margin: '25px'}}>
              Please input your discord user Id into the
              text box below before clicking the verify button
            </h4>
            <h6 style={{margin: '0'}}>
              {"Your discord user Id is given in the url of this page in the format ?userId=<id>. " +
                "Please copy the <id> portion of the url and input it into the text box"}
            </h6>
            <input value={uid} onChange={type} placeholder='UserId'/>
          </div>
          <br/> 
          <button onClick={clicked}>
            Verify
          </button>
      </header>
    </div>
  );
}

export default App;
