import React, {useEffect} from 'react';
import { useSearchParams } from "react-router-dom";

function startLoginProcess(verificationLink) {
    window.location.href = verificationLink;
    console.log(222)
}

function Home() {
  const [searchParams] = useSearchParams();

  const loginURL = searchParams.get('url');
  const user = searchParams.get('user');
  const server = searchParams.get('server');

  useEffect(()=> {
        localStorage.setItem("uId", user)
        localStorage.setItem("server", server)
        startLoginProcess(loginURL);

  },[])

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

export default Home;
