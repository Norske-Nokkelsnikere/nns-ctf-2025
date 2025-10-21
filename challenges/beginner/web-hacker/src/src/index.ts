/*
 * Copyright 2025 Norske Nøkkelsnikere
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import type { ServerWebSocket } from 'bun';
import puppeteer from 'puppeteer';

let browserInUse = false;

Bun.serve({
  routes: {
    '/ws': (req, server) => {
      if (server.upgrade(req)) {
        return;
      }
      return new Response('Upgrade failed', { status: 500 });
    },

    '/': new Response(await Bun.file('./src/index.html').bytes(), {
      headers: {
        'Content-Type': 'text/html',
      },
    }),
    '/part1': new Response(await Bun.file('./src/part1.html').bytes(), {
      headers: {
        'Content-Type': 'text/html',
      },
    }),
    '/part2': new Response(await Bun.file('./src/part2.html').bytes(), {
      headers: {
        'Content-Type': 'text/html',
      },
    }),
    '/finished': new Response(await Bun.file('./src/finished.html').bytes(), {
      headers: {
        'Content-Type': 'text/html',
      },
    }),
    '/styles.css': new Response(await Bun.file('./src/styles.css').bytes(), {
      headers: {
        'Content-Type': 'text/css',
      },
    }),
  },
  websocket: {
    message(ws, message) {
      const msg = message.toString();
      if (msg.startsWith('VISIT')) {
        visit(msg.replaceAll('VISIT ', ''), ws)
          .then(() => {
            ws.send('DONE');
          })
          .catch(() => {
            ws.send('ERR');
          });
        ws.send('VISITING');
      }
    },
  },
});

async function visit(b64: string, ws: ServerWebSocket<unknown>) {
  console.log('Starting XSS bot');

  try {
    browserInUse = true;
    const browser = await puppeteer.launch({
      args: ['--no-sandbox'],
    });
    await browser.setCookie({
      name: 'flag',
      value: process.env.FLAG || 'NNS{EXAMPLE_FLAG}',
      domain: 'localhost',
    });
    const page = await browser.newPage();
    ws.send('OPENED');
    await page.goto('http://localhost:3000');
    await page.setContent(atob(b64));
    ws.send('WAITING');
    await Bun.sleep(5000);
    await browser.close();
  } catch (e) {
    console.error(e);
  } finally {
    browserInUse = false;
  }
}

console.log('Startet at http://localhost:3000');
