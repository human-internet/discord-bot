import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import './Verification.css';

function VerificationSuccessful() {
  const [searchParams] = useSearchParams();
  const [verificationStatus, setVerificationStatus] = useState('pending');
  const [verificationSent, setVerificationSent] = useState(false);
  const [errorMessage, setErrorMessage] = useState('')

  const exchangeToken = searchParams.get('et');
  // const discordServer = searchParams.get('serverId');
  const server = localStorage.getItem("server");
  const BACKEN_URL = process.env.REACT_APP_BACKEND_URL;

  /* The code above does the following, explained in English:
  1. It creates a function called continueVerification that takes in a parameter called exchangeToken
  2. It sets the verificationStatus state to pending
  3. It tries to send a request to the backend with the exchange token and the server ID
  4. If the request returns a response code of 400 or above, it sets the verificationStatus state to failed and then displays the error response
  5. If the request returns a response code of 200, it sets the verificationStatus state to verified and then redirects to the Discord server
  6. If the request fails, it sets the verificationStatus state to failed and then displays an error message */
  const continueVerification = async (exchangeToken) => {
    console.log('The server variable: ' + server)
    setVerificationStatus('pending');
    try {
      if (verificationSent) {
        return;
      }
      const resp = await fetch(BACKEN_URL + `/api/verification_successful/?&serverId=${server}&et=${exchangeToken}`);
      // const data = await resp.json();
      // console.log(data.message);
      if (resp.status >= 400) {
        setVerificationStatus('failed');
        resp.json().then((e) => {
          setErrorMessage(e.message + `\nserverId=${server}`);
        }).catch(() => {
          if (!errorMessage) {
            setErrorMessage('An Error Occurred');
          }
        });
      } else {
        setVerificationStatus('verified');
        localStorage.removeItem("server");
        //window.close() TODO
        window.location.replace('https://discord.com/channels/' + server);
      }
      setVerificationSent(true);
    } catch (e) {
      setVerificationStatus('failed');
      setErrorMessage("An error occurred.");
    }
  }

  useEffect(() => {
    continueVerification(exchangeToken);
  });

  return (
    <header className="App-header">
      <div>
        {
          verificationStatus === 'pending' &&
          <h4 className='instructions'>
            One more step! Please wait while we complete the verification.
          </h4>
        }
        {
          verificationStatus === 'failed' &&
          <div>
            <h4 className='instructions'>
              Oops! An error occurred while completing the verification.
            </h4>
            <h6 className='status'>
              {errorMessage}
              <br/>
              <button
                onClick={() => continueVerification(exchangeToken)}
              >
                Please try again
              </button>
            </h6>
          </div>
        }
        {
          verificationStatus === 'verified' &&
          <div>
            <h4 className='instructions'>
              Hurray! You have been successfully verified.
            </h4>
            <h6 className='status'>
              You can close this window.
            </h6>
          </div>
        }
      </div>
    </header>
  );
}

export default VerificationSuccessful;
