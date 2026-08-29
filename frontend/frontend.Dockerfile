FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build the static bundle
COPY . .
RUN npm run build

# Install lightweight web server
RUN npm install -g serve

EXPOSE 8501

# Serve the application
CMD ["serve", "-s", "dist", "-l", "8501"]
