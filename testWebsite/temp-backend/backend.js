const express= require('express');
 
var app= express();

const timeout = async ms => new Promise(res => setTimeout(res, ms));

let verify = {

}
 
app.get('/',function(req,res){
  // Redirect the user to the main page
  verify['channel'] = req.query.channel;
  verify['guild'] = req.query.guild;
  res.redirect('http://localhost:3000/');
});

app.get('/verify',function(req,res){
  // Veridy the user (should do a post request to the db)
  verify['verify'] = true;
  res.redirect(`https://discord.com/channels/${verify['guild']}/${verify['channel']}`) ;
})

app.get('/data',async function(req,res){
  let invalid = 0;
  while (!verify['verify']) {
    if (invalid === 30) {
      // Gives them 30 seconds to verify (click the button) before canceling
      res.status(400).json({'verify': false})
    }

    await timeout(1000);
    invalid += 1
  }
  // Verified, so it tells the bot to add the role
  res.status(200).json(verify)
})

 
app.listen(3010,function(req,res){
  console.log("Server is running at port 3010");
});
