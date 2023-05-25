import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import './Verification.css';

function VerificationSuccessful() {
  const [searchParams] = useSearchParams();
  const [verificationStatus, setVerificationStatus] = useState('pending');
  const [verificationSent, setVerificationSent] = useState(false);
  const [errorMessage, setErrorMessage] = useState('')

  const exchangeToken = searchParams.get('et');
  const server = localStorage.getItem("server");
  const BACKEN_URL = process.env.REACT_APP_BACKEND_URL;


  const continueVerification = async (exchangeToken) => {
    setVerificationStatus('pending');
    try {
      if (verificationSent) {
        return;
      }
      const resp = await fetch(BACKEN_URL + `/api/verification_successful/?&serverId=${server}&et=${exchangeToken}`);
      if (resp.status >= 400) {
        setVerificationStatus('failed');
        resp.json().then((e) => {
          setErrorMessage(JSON.stringify(e) + `\nserverId=${server}`);
        }).catch((e) => setErrorMessage("An error occurred."));
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

export default VerificationSuccessful;
