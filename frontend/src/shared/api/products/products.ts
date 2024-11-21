import api from "../base";
import { IProduct } from "./types";

export const getProducts = async (): Promise<IProduct[]> => {
  const response = await api.get<IProduct[]>("/products");
  return response.data;
};

export const getProductById = async (id: string): Promise<IProduct> => {
  const response = await api.get<IProduct>(`/products/${id}`);
  return response.data;
};

export const deleteProductById = async (id: string): Promise<void> => {
  await api.delete(`/products/${id}`);
};

export const createProduct = async (
  product: Omit<IProduct, "id">
): Promise<void> => {
  await api.post("/products", product);
};
