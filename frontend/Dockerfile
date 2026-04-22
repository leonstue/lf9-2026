FROM node:latest

WORKDIR /app

COPY frontend /app

RUN npm install

RUN npm run build

EXPOSE 4173

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]