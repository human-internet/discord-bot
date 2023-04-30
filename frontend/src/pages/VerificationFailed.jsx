import React from 'react';
import {useSearchParams} from "react-router-dom";
import './Verification.css';

function VerificationFailed() {
  const [searchParams] = useSearchParams();

  const message = searchParams.get('message');

  return (
    <header className="App-header">
      <div>
        <h4 className='instructions'>
          Oops! Sorry, we could not verify you.
        </h4>
        <h6 className='status'>
          {message}
          <p>
            You can close this window.
          </p>
        </h6>
      </div>
      <br/>
    </header>
  );
}

export default VerificationFailed;
