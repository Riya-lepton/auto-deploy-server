// const express = require('express');
// const bodyParser = require('body-parser');
// const { exec } = require('child_process');

// const app = express();
// const PORT = 8080;

// // Parse JSON bodies
// app.use(bodyParser.json());

// // Test GET route
// app.get('/', (req, res) => {
//   res.send('Webhook Service is Running');
// });

// // Webhook endpoint
// app.post('/webhook', (req, res) => {
//   const event = req.body;

//   console.log('Webhook received:', event);

//   // Only handle 'push' events
//   // if (event.action === 'push') {

// if (req.body.ref && req.body.ref === 'refs/heads/main') {
//     console.log('New code pushed. Deploying...');

//     // Run deployment script
//     exec('/home/lepton/riya_space/deploy.sh', (err, stdout, stderr) => {
//       if (err) {
//         console.error('Deployment failed:', stderr);
//         return res.status(500).send('Deployment failed');
//       }

//       console.log('Deployment successful:', stdout);
//       res.status(200).send('Deployed');
//     });
//   } 
  
// else {
//     res.status(200).send('Ignored');
//   }
// });

// console.log("Starting server...");
// app.listen(PORT, () => {
//   console.log(`Server is listening on port ${PORT}`);
// });
// console.log("After app.listen()");















const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;

// Replace with your webhook secret and password
const WEBHOOK_SECRET = 'secretpswd'; 
const WEBHOOK_PASSWORD = 'password123'; // The expected password sent with the request

// Parse raw body for signature verification
app.use(bodyParser.raw({ type: 'application/json' }));

// Function to verify GitHub webhook signature
function verifySignature(req, res, next) {
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) {
    return res.status(403).send('Signature is missing');
  }

  const hash = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(req.body)
    .digest('hex');

  const expectedSignature = `sha256=${hash}`;

  if (signature !== expectedSignature) {
    return res.status(403).send('Invalid signature');
  }

  next();  // If the signature is valid, move to the next middleware
}

// Password verification middleware
function verifyPassword(req, res, next) {
  const password = req.body.password; // Assuming the password is sent in the body as `password`

  if (!password || password !== WEBHOOK_PASSWORD) {
    return res.status(403).send('Invalid password');
  }

  next();  // If the password matches, proceed with the request
}

// Test GET route
app.get('/', (req, res) => {
  res.send('Webhook Service is Running');
});

// Webhook POST route with both signature and password verification
app.post('/webhook', verifySignature, verifyPassword, (req, res) => {
  const event = JSON.parse(req.body);

  console.log('Webhook received:', event);

  if (req.body.ref === 'refs/heads/main') {
    console.log('New code pushed. Deploying...');

    exec('/home/lepton/riya_space/deploy.sh', (err, stdout, stderr) => {
      if (err) {
        console.error('Deployment failed:', stderr);
        return res.status(500).send('Deployment failed');
      }

      console.log('Deployment successful:', stdout);
      res.status(200).send('Deployed');
    });
  } else {
    res.status(200).send('Ignored');
  }
});

console.log('Starting server...');
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});
console.log('After app.listen()');
