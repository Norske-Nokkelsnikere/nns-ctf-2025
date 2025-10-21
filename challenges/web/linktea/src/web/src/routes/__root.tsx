import { Outlet, createRootRoute } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

export const Route = createRootRoute({
  component: () => (
    <>
      <div className="flex items-center justify-center bg-[#f3f4f4] h-full">
        <main className="w-3/7 h-fit">
          <Outlet />
          <TanStackRouterDevtools />
        </main>
      </div>
    </>
  ),
});
