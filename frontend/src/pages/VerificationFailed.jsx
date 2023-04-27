import React from 'react';
import {useSearchParams} from "react-router-dom";

function VerificationFailed() {
    const [searchParams] = useSearchParams();

    const message = searchParams.get('message');

    return (
        <header className="App-header">
            <div>
                <h4 style={{margin: '25px'}}>
                    Opps! Sorry we could not verify you.
                </h4>
                <h6 style={{margin: '0', textAlign: "center"}}>
                    {message}
                    <p>
                        You can close this window
                    </p>
                </h6>
            </div>
            <br/>
        </header>
    );
}

export default VerificationFailed;
