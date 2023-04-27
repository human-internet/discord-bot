import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";

function VerificationSuccessful() {
    const [searchParams] = useSearchParams();
    const [verificationStatus, setVerificationStatus] = useState('pending')
    const [errorMessage, setErrorMessage] = useState('')

    const exchangeToken = searchParams.get('et');
    const userId = localStorage.getItem("uId")
    const server = localStorage.getItem("server")
    const BACKEN_URL = process.env.REACT_APP_BACKEND_URL


    const continueVerification = async (exchangeToken) => {
        setVerificationStatus('pending')
        console.log(111)
        try {
            const resp = await fetch(BACKEN_URL + `/api/verification_successful/?userId=${userId}&serverId=${server}&et=${exchangeToken}`)
            if (resp.status >= 400) {
                setVerificationStatus('failed');
                resp.json().then((e) => {
                    setErrorMessage(JSON.stringify(e))
                }).catch((e) => setErrorMessage("An error occurred."))
            } else {
                setVerificationStatus('verified')
                localStorage.removeItem("uId")
                localStorage.removeItem("server")
            }
        } catch (e) {
            setVerificationStatus('failed');
            setErrorMessage("An error occurred.")
        }
    }
    useEffect(() => {
        continueVerification(exchangeToken)
    }, [])

    return (
        <header className="App-header">
            <div>
                {
                    verificationStatus === 'pending' &&
                    <h4 style={{margin: '25px'}}>
                        One more step! Please wait while we complete the verification.
                    </h4>
                }
                {
                    verificationStatus === 'failed' &&
                    <>
                        <h4 style={{margin: '25px'}}>
                            Oops! An error occurred while completing the verification.
                        </h4>
                        <h6 style={{margin: '0', textAlign: "center"}}>
                            {errorMessage} <br/>
                            <button onClick={() => continueVerification(exchangeToken)}>Please try again</button>
                        </h6>
                    </>
                }
                {
                    verificationStatus === 'verified' &&
                    <>
                        <h4 style={{margin: '25px'}}>
                            Hurray! You have been successfully verified.
                        </h4>
                        <h6 style={{margin: '0', textAlign: "center"}}>
                            You can close this window
                        </h6>
                    </>}
            </div>
        </header>
    );
}

export default VerificationSuccessful;
