import { FC } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { getProducts, createProduct } from "../../../shared/api/products";
import { ProductCard } from "../../../features/products/ui/ProductCard";
import { IProduct } from "../../../shared/api/products/types";

const ProductSchema = Yup.object().shape({
  name: Yup.string().required("Required"),
  avatar: Yup.string().url("невалидный URL").required("Required"),
  description: Yup.string().required("Required"),
  author: Yup.string().required("Required"),
});

export const ProductsPage: FC = () => {
  const { data, isLoading, error, refetch } = useQuery<IProduct[]>({
    queryKey: ["products"],
    queryFn: getProducts,
  });

  const {
    mutate: addProduct,
    status: addStatus,
    error: addError,
    isSuccess,
  } = useMutation<void, Error, Omit<IProduct, "id">>({
    mutationFn: createProduct,
    onSuccess: () => {
      console.log("Product created successfully");
      refetch();
    },
  });

  if (isLoading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return <div>Error fetching products</div>;
  }

  return (
    <div>
      <Formik
        initialValues={{
          name: "",
          avatar: "",
          description: "",
          author: "",
        }}
        validationSchema={ProductSchema}
        onSubmit={(values, { resetForm }) => {
          addProduct(values);
          resetForm();
        }}
      >
        {({ isSubmitting }) => (
          <Form>
            <Field type="text" name="name" placeholder="Name" />
            <ErrorMessage name="name" component="div" />
            <Field type="text" name="avatar" placeholder="Avatar URL" />
            <ErrorMessage name="avatar" component="div" />
            <Field type="text" name="description" placeholder="Description" />
            <ErrorMessage name="description" component="div" />
            <Field type="text" name="author" placeholder="Author" />
            <ErrorMessage name="author" component="div" />
            <button
              type="submit"
              disabled={isSubmitting || addStatus === "pending"}
            >
              Добавить
            </button>
            {addError && <div>Error: {addError.message}</div>}
            {isSuccess && <div>Product created successfully!</div>}
          </Form>
        )}
      </Formik>
      <ul>
        {data?.map((product) => (
          <li key={product.id}>
            <ProductCard product={product} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductsPage;
