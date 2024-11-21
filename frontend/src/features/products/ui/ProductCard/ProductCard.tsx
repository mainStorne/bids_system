import { FC } from "react";
import { IProduct } from "../../../../shared/api/products/types";
import styles from "./productcard.module.scss";
import { useNavigate } from "react-router-dom";

interface ProductCardProps {
  product: IProduct;
}

export const ProductCard: FC<ProductCardProps> = ({ product }) => {
  const nav = useNavigate();

  const handleClickCard = () => {
    nav(`/products/${product.id}`);
  };

  return (
    <div onClick={handleClickCard} className={styles.card}>
      <img src={product.avatar} alt={product.name} />
      <h2>{product.name}</h2>
      <p>{product.description}</p>
      <p>Author: {product.author}</p>
    </div>
  );
};

export default ProductCard;
