FROM node:23-slim
WORKDIR app/
COPY package* ./
RUN npm ci
COPY . ./
CMD ["npm", "run", "start"]
