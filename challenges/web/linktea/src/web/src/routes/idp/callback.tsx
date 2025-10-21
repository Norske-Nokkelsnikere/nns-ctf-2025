import { Content } from '@/components/Content';
import { Avatar, Heading } from '@digdir/designsystemet-react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import Cookies from 'js-cookie';
import { DateTime } from 'luxon';
import * as z from 'zod/v4';

const queryParams = z.object({
  redirectUrl: z
    .string()
    .transform((v) => decodeURIComponent(v))
    .optional(),
  code: z.string(),
});

export const Route = createFileRoute('/idp/callback')({
  component: RouteComponent,
  validateSearch: queryParams,
  loaderDeps: ({ search: { redirectUrl } }) => ({ redirectUrl }),
  loader: async ({ deps }) => {
    if (deps.redirectUrl) {
      const url = new URL(deps.redirectUrl);

      if (url.pathname.startsWith('/profile/')) {
        const username = url.pathname.replace('/profile/', '');
        const res = await fetch(`/api/profile/${username}/preview`);
        const json = await res.json();
        return json.avatar_url;
      }
    }
  },
});

function RouteComponent() {
  const { redirectUrl, code } = Route.useSearch();
  const avatar_url = Route.useLoaderData();
  const navigator = useNavigate();

  setTimeout(async () => {
    if (!avatar_url) {
      await exchangeCode(code);
      navigator({
        to: '/manage',
      });
    }
  }, 500);

  return (
    <Content className="flex items-center justify-center gap-10">
      <Heading level={1} data-size="md">
        Redirecting...
      </Heading>

      <Avatar aria-label="Profile picture of user" data-size="xl">
        {avatar_url ? (
          <img
            src={avatar_url}
            onLoad={async () => {
              await exchangeCode(code);
              if (redirectUrl) {
                location.href = redirectUrl;
              }
            }}
            onError={async () => {
              await exchangeCode(code);
              if (redirectUrl) {
                location.href = redirectUrl;
              }
            }}
          />
        ) : (
          <></>
        )}
      </Avatar>
    </Content>
  );
}

async function exchangeCode(code: string): Promise<string> {
  const res = await fetch('/api/auth/exchange', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code,
    }),
  });
  const json = await res.json();

  if (!json.jwt) {
    throw new Error('No JWT given');
  }

  Cookies.set('linktea-jwt', json.jwt, {
    sameSite: 'Strict',
    expires: DateTime.now().plus({ hours: 3 }).toJSDate(),
  });

  return json.jwt;
}
