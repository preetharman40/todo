FROM node:18-alpine
WORKDIR /app
COPY . .
RUN echo "Building the production container..."
CMD [ "node", '-v' ]