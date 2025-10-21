import { PrismaClient } from './generated/prisma';
import home from './index.html';

const prisma = new PrismaClient();

if (
  !(await prisma.user.findUnique({
    where: {
      username: 'admin',
    },
  }))
) {
  await prisma.user.create({
    data: {
      username: 'admin',
      password: Bun.randomUUIDv7(),
      role: 'Admin',
    },
  });
}

const s = Bun.serve({
  routes: {
    '/': home,
    '/login': async (req) => {
      const c = (await req.json()) as { username: string; password: string };

      const u = await prisma.user.findUnique({
        where: {
          username: c.username,
          password: c.password,
        },
      });

      if (!u) {
        return new Response('UNAUTHORIZED', { status: 401 });
      }

      if (u.role === 'User') {
        return new Response('NO FLAG', { status: 204 });
      }

      return new Response('Flag is ' + (process.env.FLAG || 'NNS{fake-flag}'));
    },
    '/reg': async (req) => {
      const c = (await req.json()) as { username: string; password: string };

      if (
        await prisma.user.findUnique({
          where: {
            username: c.username,
          },
        })
      ) {
        return new Response('Username taken', { status: 400 });
      }

      await prisma.user.create({
        data: {
          username: c.username,
          password: c.password,
        },
      });

      return new Response('OK', { status: 200 });
    },
  },
});

console.log('Running on ' + s.port);
