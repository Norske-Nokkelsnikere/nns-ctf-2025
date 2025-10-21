import { Content } from '@/components/Content';
import { Button, Heading, Paragraph } from '@digdir/designsystemet-react';
import { createFileRoute, Link } from '@tanstack/react-router';
import Cookie from 'js-cookie';

export const Route = createFileRoute('/')({
  component: App,
});

function App() {
  const signedIn = !!Cookie.get('linktea-jwt');

  return (
    <>
      <Content className="flex flex-col gap-3">
        <Heading level={1} data-size="xl">
          Linktea
        </Heading>
        <Paragraph>The shittiest Link-in-bio service.</Paragraph>

        <div className="flex gap-2">
          <Button asChild className="w-fit">
            <Link to="/idp/login">Login</Link>
          </Button>
          <Button asChild className="w-fit" variant="tertiary">
            <Link to="/idp/register">Register</Link>
          </Button>
          <Button asChild variant="tertiary" className="w-fit">
            <Link to="/report">Report profile</Link>
          </Button>
          {signedIn ? (
            <Button
              variant="tertiary"
              className="w-fit"
              onClick={() => {
                Cookie.remove('linktea-jwt');
                location.reload();
              }}>
              Sign out
            </Button>
          ) : (
            <></>
          )}
        </div>
      </Content>
    </>
  );
}
