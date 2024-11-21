import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  getProductById,
  deleteProductById,
} from "../../../shared/api/products";
import { IProduct } from "../../../shared/api/products/types";

export const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: product,
    isLoading: isFetching,
    error: fetchError,
  } = useQuery<IProduct>({
    queryKey: ["product", id],
    queryFn: () => getProductById(id!),
    enabled: !!id, // Только выполнять запрос, если ID существует
  });

  const { mutate: deleteProduct, error: deleteError } = useMutation({
    mutationFn: deleteProductById,
    onSuccess: () => {
      navigate("/products");
    },
  });

  const handleDelete = () => {
    if (id) {
      deleteProduct(id);
    }
  };

  if (isFetching) {
    return <div>Загрузка...</div>;
  }

  if (fetchError || deleteError) {
    return <div>error fetching/deleting product</div>;
  }

  return (
    <div>
      {product ? (
        <div>
          <img src={product.avatar} alt={product.name} />
          <h1>{product.name}</h1>
          <p>{product.description}</p>
          <p>Author: {product.author}</p>
          <button onClick={handleDelete}>Удалить</button>
        </div>
      ) : (
        <div>Product not found</div>
      )}
    </div>
  );
};

export default ProductDetailPage;
