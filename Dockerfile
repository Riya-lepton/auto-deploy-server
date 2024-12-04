# Use the official Node.js image
FROM node:18

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the webhook handling code
COPY . .

# Expose the port your webhook app listens to
EXPOSE 8080

# Command to start your app
CMD ["node", "app.js"]

