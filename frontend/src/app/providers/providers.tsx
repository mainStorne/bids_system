import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FC } from "react";

interface IProviders {
  readonly children: JSX.Element;
}
const queryClient = new QueryClient();

export const Providers: FC<IProviders> = ({ children }) => {
  return (
    <>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </>
  );
};

export default Providers;
