import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import './Verification.css';

function VerificationSuccessful() {
  const [searchParams] = useSearchParams();
  const [verificationStatus, setVerificationStatus] = useState('pending');
  let verificationSent = false;
  const [errorMessage, setErrorMessage] = useState('Error: ')

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
    
    if (!verificationSent) {
      setVerificationStatus('pending');
      verificationSent = true;
      try {
        const resp = await fetch(BACKEN_URL + `/api/verification_successful/?&serverId=${server}&et=${exchangeToken}`);
        if (resp.status >= 400) {
          
          resp.json()
          .then((e) => {
            const errString = JSON.stringify(e);
            setErrorMessage(oldMessageObj => errString);
            setVerificationStatus('failed');
          }).catch(() => {
            if (!errorMessage) {
              setErrorMessage('An Error Occurred');
            }
          });
        } else {
          setVerificationStatus('verified');
          localStorage.removeItem("server");
          const isDiscordInstalled = isDiscordAppInstalled();
          if (isDiscordInstalled) {
            // Attempt to open Discord with custom URL scheme
            const discordServerUrl = `discord://discord.com/channels/${server}`;
            window.location.replace(discordServerUrl);
          } else {
            // Fallback to your previous code for redirection
            window.location.replace('https://discord.com/channels/' + server);
          }
        }
      } catch (e) {
        setVerificationStatus('failed');
        setErrorMessage("An error occurred.");
      }
    } else {
      return;
    }
  }

  useEffect(() => {
    continueVerification(exchangeToken);
  }, []);

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

/* The code below is using to check if discord is installed on local system
 1. Creating a promise to handle asynchronous operation 
 2. Create an iframe element, make it unseen, use 'load' event to determine whether it's has been load
 3. Attach the 'onload' (succeed) and 'timeout' (fail) event to resolve */
function isDiscordAppInstalled() {
  return new Promise((resolve) => {

    let appDetected = false;

    const iframe = document.createElement('iframe');
    iframe.style.display = "none";
    
    iframe.onload = function() {
      appDetected = true;
      resolve(true);
    };
    
    iframe.src = "discord://";
    document.body.appendChild(iframe);

    setTimeout(() => {
      document.body.removeChild(iframe);
      if (!appDetected) {
        resolve(false);
      }
    }, 1000);
  });
}

export default VerificationSuccessful;
