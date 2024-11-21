import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  RouterProvider,
} from "react-router-dom";
import { Layout } from "../layout";
import { ProductsPage } from "../../pages/ProductsPage";
import { ProductDetailPage } from "../../pages/ProductDetailPage";
import { LoginPage } from "../../pages/LoginPage";
import { RegisterPage } from "../../pages/RegisterPage";

export const AppRouter = () => {
  const routes = createRoutesFromElements(
    <Route path="/" element={<Layout />}>
      <Route path="/products" element={<ProductsPage />} />
      <Route path="products/:id" element={<ProductDetailPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Route>
  );

  const router = createBrowserRouter(routes, {
    future: {
      v7_relativeSplatPath: true,
      v7_fetcherPersist: true,
      v7_normalizeFormMethod: true,
      v7_partialHydration: true,
      v7_skipActionErrorRevalidation: true,
    },
  });

  return (
    <div>
      <RouterProvider router={router} />
    </div>
  );
};
