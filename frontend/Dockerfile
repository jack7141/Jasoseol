FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

RUN npm install -g serve

ENV REACT_APP_BASE_URL=${REACT_APP_BASE_URL}

EXPOSE 80

# Serve the build output on port 80
CMD ["serve", "-s", "build", "-l", "80"]
