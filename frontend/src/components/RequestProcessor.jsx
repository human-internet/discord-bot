import React from 'react';
import { useSearchParams } from "react-router-dom";


let user;


/*
function showErrorMessage(message) {

    jQuery(function ($) {
        $("#hid-verification-error-message").html(message)
        $("#hid-verification-error-message").show()
        $("#start-human-id-verification").show()
        $("#hid-verification-pending").hide()
    });
}
*/
function verificationFailed(message) {
    //showErrorMessage(message);
}

function startLoginProcess(e) {
    const handle = window.open(e, "Human_ID_Verification", 'width=900,height=650');
    console.log(222)
    if (handle) {
        if (window.focus) {
            handle.focus()
        }
    } else {
        // TODO
        // showErrorMessage("Please allow popups for this site");
    }
}

function verificationSuccess(token) {
    console.log(111)
    fetch(`http://localhost:8000/api/success/?user=${user}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/x-www-form-urlencoded',
        })
    })
}

function RequestProcessor() { 
  const [searchParams] = useSearchParams();

  const loginURL = searchParams.get('url');
  user = searchParams.get('user');

  startLoginProcess(loginURL);

  return (
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
          </div>
          <br/> 
      </header>
  );
}

export default RequestProcessor;
