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

const server = Bun.serve({
  routes: {
    '/': new Response(await Bun.file('./src/index.html').bytes()),
    '/man': {
      POST: async (req) => {
        const body = ((await req.json()) as { program?: string }) || undefined;

        if (!body || !body.program) {
          return Response.json({
            result: 'Bad request',
          });
        }

        const programName = body.program;
        try {
          const output = await Bun.$`man ${programName}`;
          return Response.json({
            result: output.text(),
          });
        } catch (e) {
          console.warn(e);

          return Response.json({
            result: 'Failure to get manuals',
          });
        }
      },
    },
  },
});

console.log(`Server started on http://${server.hostname}:${server.port}`);
