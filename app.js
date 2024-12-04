const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;

// Parse JSON bodies
app.use(bodyParser.json());

// Test GET route
app.get('/', (req, res) => {
  res.send('Webhook Service is Running');
});

// Webhook endpoint
app.post('/webhook', (req, res) => {
  const event = req.body;

  console.log('Webhook received:', event);

  // Only handle 'push' events
  if (event.action === 'push') {
    console.log('New code pushed. Deploying...');

    // Run deployment script
    exec('./deploy.sh', (err, stdout, stderr) => {
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

app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});



