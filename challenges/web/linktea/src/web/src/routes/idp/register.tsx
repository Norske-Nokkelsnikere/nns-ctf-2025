import { Content } from '@/components/Content';
import { Button, Heading, Textfield } from '@digdir/designsystemet-react';
import { createFileRoute, Link, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/idp/register')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigator = useNavigate();
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  return (
    <Content className="flex flex-col gap-4">
      <Heading level={1} data-size="lg">
        Register
      </Heading>
      <Textfield id="username" label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <Textfield
        id="password"
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <div className="flex gap-2">
        <Button
          className="w-fit"
          onClick={async () => {
            const res = await fetch('/api/auth/register', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                username,
                password,
              }),
            });

            if (res.status == 200) {
              navigator({
                to: '/idp/login',
              });
            } else {
              alert(`Error: ${(await res.json()).message}`);
            }
          }}>
          Submit
        </Button>
        <Button asChild className="w-fit" variant="tertiary">
          <Link to="/idp/login">Login</Link>
        </Button>
      </div>
    </Content>
  );
}
