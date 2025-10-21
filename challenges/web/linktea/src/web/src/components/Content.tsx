import type { ReactNode } from 'react';

export function Content({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={'p-8 bg-white border-[#b8bbc1] border-1 rounded-sm ' + (className ?? '')}>{children}</div>;
}
