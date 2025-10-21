import { Content } from '@/components/Content';
import { Button, Heading, Paragraph, Textfield } from '@digdir/designsystemet-react';
import { createFileRoute } from '@tanstack/react-router';
import Cookie from 'js-cookie';
import { useState } from 'react';

export const Route = createFileRoute('/report')({
  component: ReportComponent,
  loader: () => {
    return { jwt: Cookie.get('linktea-jwt') };
  },
});

function ReportComponent() {
  const [reportUrl, setReportUrl] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const { jwt } = Route.useLoaderData();

  return (
    <>
      <Content className="flex flex-col gap-3">
        <Heading level={1} data-size="md">
          Report
        </Heading>

        <Textfield
          label="URL Path"
          type="url"
          value={reportUrl}
          onChange={(e) => setReportUrl(e.target.value)}
          prefix="/"
        />

        <Button
          className="w-fit"
          onClick={async () => {
            setIsProcessing(true);

            await fetch(`/api/report`, {
              method: 'POST',
              headers: {
                Authorization: 'Bearer ' + jwt,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                path: reportUrl,
              }),
            });

            setIsProcessing(false);
          }}>
          Submit
        </Button>

        {isProcessing ? <Paragraph>Processing report...</Paragraph> : <></>}
      </Content>
    </>
  );
}
