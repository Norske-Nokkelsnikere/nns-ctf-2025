import { Content } from '@/components/Content';
import { parseJwt } from '@/lib/jwt';
import { Alert, Button, Heading, Textfield } from '@digdir/designsystemet-react';
import { createFileRoute, Link } from '@tanstack/react-router';
import Cookie from 'js-cookie';
import { useState } from 'react';

export const Route = createFileRoute('/manage')({
  component: RouteComponent,
  loader: async () => {
    const c = Cookie.get('linktea-jwt');
    const jwtContents = parseJwt(c!);

    const res = await fetch(`/api/profile/${jwtContents.username}/full`, {
      headers: {
        Authorization: 'Bearer ' + c,
      },
    });
    const json = await res.json();

    return { cookie: c, bio: json.bio, username: json.username, avatar_url: json.avatar_url };
  },
});

function RouteComponent() {
  const data = Route.useLoaderData();
  const [avatarUrl, setAvatarUrl] = useState<string>(data.avatar_url);
  const [bio, setBio] = useState<string>(data.bio);
  const [ok, setOk] = useState<boolean>(false);

  return (
    <Content className="flex flex-col gap-5">
      <Heading level={1} data-size="lg">
        Manage profile
      </Heading>
      <Textfield
        label="Avatar URL"
        type="url"
        value={avatarUrl}
        onChange={(e) => setAvatarUrl(e.target.value)}></Textfield>
      <Textfield label="Bio" multiline value={bio} onChange={(e) => setBio(e.target.value)}></Textfield>

      <div className="flex gap-1">
        <Button
          className="w-fit"
          onClick={async () => {
            await fetch(`/api/update`, {
              method: 'POST',
              headers: {
                Authorization: 'Bearer ' + data.cookie,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                bio,
                avatar_url: avatarUrl,
              }),
            });

            setOk(true);
          }}>
          Save
        </Button>
        <Button className="w-fit" variant="tertiary" asChild>
          <Link to="/profile/$profileId" params={{ profileId: data.username }}>
            View profile
          </Link>
        </Button>
      </div>
      {ok ? <Alert>Ok</Alert> : <></>}
    </Content>
  );
}
