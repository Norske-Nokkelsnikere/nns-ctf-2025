import { Content } from '@/components/Content';
import { parseJwt } from '@/lib/jwt';
import { Avatar, Button, Heading, Paragraph, Link as UiLink } from '@digdir/designsystemet-react';
import { createFileRoute, Link } from '@tanstack/react-router';
import Cookie from 'js-cookie';
import { Lock } from 'lucide-react';

export const Route = createFileRoute('/profile/$profileId')({
  component: RouteComponent,
  loader: async ({ params }) => {
    const c = Cookie.get('linktea-jwt');
    let response;
    let isSelf = false;
    let notFound = false;

    if (!c) {
      const res = await fetch(`/api/profile/${params.profileId}/preview`);
      if (res.status === 404) notFound = true;
      response = await res.json();
    } else {
      const res = await fetch(`/api/profile/${params.profileId}/full`, {
        headers: {
          Authorization: 'Bearer ' + c,
        },
      });
      if (res.status === 404) notFound = true;

      response = await res.json();
      const contents = parseJwt(c);
      if (params.profileId === contents.username) {
        isSelf = true;
      }
    }

    return { bio: response.bio, avatar_url: response.avatar_url, isSelf, notFound };
  },
});

function RouteComponent() {
  const { profileId } = Route.useParams();
  const { bio, avatar_url, isSelf, notFound } = Route.useLoaderData();

  return (
    <>
      <Content className="flex flex-col items-center gap-3">
        {notFound ? (
          <Paragraph>Profile not found!</Paragraph>
        ) : (
          <>
            <Avatar aria-label={`Profile picture of user ${profileId}`} data-size="xl">
              {avatar_url ? <img src={avatar_url} /> : <></>}
            </Avatar>
            <Heading level={1}>{profileId}</Heading>
            {bio ? (
              <Paragraph data-size="sm">{bio}</Paragraph>
            ) : (
              <div className="border-t-1 border-t-[#b8bbc1]">
                <div className="flex gap-2 items-center m-5 mt-10">
                  <Lock />
                  <Paragraph data-size="sm">You need to login to see the bio.</Paragraph>
                </div>
                <Button asChild className="w-fit m-auto">
                  <Link to="/idp/login" search={{ redirectUrl: `profile/${profileId}` }}>
                    Login
                  </Link>
                </Button>
              </div>
            )}
            {isSelf ? (
              <UiLink asChild className="mt-5" data-size="sm">
                <Link to="/manage">Edit profile</Link>
              </UiLink>
            ) : (
              <></>
            )}
          </>
        )}
      </Content>
    </>
  );
}
