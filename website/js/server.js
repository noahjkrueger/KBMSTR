import express from 'express';
import logger from 'morgan';
import fs from 'fs';

class KBMSTRServer {
  constructor() {
    this.app = express();
    this.app.use(logger('dev'));
    this.app.use(express.json({extended: true, limit: '1mb'}));
    this.app.use(express.static('./'));
  }
  
  async initRoutes() {
    // not implimented
  }

  async start() {
    const port = 8080;
    this.app.listen(port, () => {
      console.log(`KBMSTRServer listening on port ${port}!`);
    });
  }
}

const server = new KBMSTRServer();
server.initRoutes();
server.start();