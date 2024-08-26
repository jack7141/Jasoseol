# Use the official Node.js image as a base image
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application to the container
COPY . .

# Build the React app
RUN npm run build

# Install a simple web server to serve static files
RUN npm install -g serve

# Set environment variables for the base URL and port
ENV REACT_APP_BASE_URL=${REACT_APP_BASE_URL}

# Expose port 80 to the outside world
EXPOSE 80

# Serve the build output on port 80
CMD ["serve", "-s", "build", "-l", "80"]
