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

// Replace with your webhook secret
const WEBHOOK_SECRET = 'secretpswd';

// Parse raw body for signature verification
app.use(bodyParser.raw({ type: 'application/json' }));

// Verify GitHub webhook signature
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

  next();
}

// Test GET route
app.get('/', (req, res) => {
  res.send('Webhook Service is Running');
});

// Webhook endpoint with signature verification
app.post('/webhook', verifySignature, (req, res) => {
  const event = JSON.parse(req.body);

  console.log('Webhook received:', event);

  if (event.ref && event.ref === 'refs/heads/main') {
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
