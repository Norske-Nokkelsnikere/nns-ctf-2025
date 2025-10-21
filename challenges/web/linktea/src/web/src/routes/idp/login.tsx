import { Content } from '@/components/Content';
import { Button, Heading, Textfield } from '@digdir/designsystemet-react';
import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import * as z from 'zod/v4';

const queryParams = z.object({
  redirectUrl: z.string().optional(),
});

export const Route = createFileRoute('/idp/login')({
  component: RouteComponent,
  validateSearch: queryParams,
});

function RouteComponent() {
  const navigator = useNavigate();
  const query = Route.useSearch();
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  return (
    <Content className="flex flex-col gap-4">
      <Heading level={1} data-size="lg">
        Login
      </Heading>
      <Textfield label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <Textfield label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

      <div className="flex gap-2">
        <Button
          className="w-fit"
          onClick={async () => {
            const res = await fetch('/api/auth/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                username,
                password,
              }),
            });

            const json = await res.json();

            if (json.message) {
              alert(`Error: ${json.message}`);
              return;
            }

            if (query.redirectUrl) {
              const redirectUrl = new URL(location.href.split('?')[0]);
              redirectUrl.pathname = query.redirectUrl;
              const final = encodeURIComponent(redirectUrl.href);
              console.log(final);

              navigator({
                to: '/idp/callback',
                search: {
                  redirectUrl: final,
                  code: json.code,
                },
              });
            } else {
              navigator({
                to: '/idp/callback',
                search: {
                  code: json.code,
                },
              });
            }
          }}>
          Submit
        </Button>
        <Button asChild className="w-fit" variant="tertiary">
          <Link to="/idp/register">Register</Link>
        </Button>
      </div>
    </Content>
  );
}
