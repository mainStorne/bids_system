import { ErrorMessage, Field, Form, Formik } from "formik";
import * as Yup from "yup";
import { useMutation, UseMutationResult } from "@tanstack/react-query";
import { register } from "../../shared/api/auth";
import { RegisterData } from "../../shared/api/auth/types";

const ProductSchema = Yup.object().shape({
  login: Yup.string()
    .min(5, "Login must be at least 5 characters")
    .required("Required"),
  phone: Yup.string()
    .matches(/^\d{10}$/, "Phone number must be exactly 10 digits")
    .required("Required"),
  first_name: Yup.string().required("Required"),
  middle_name: Yup.string().required("Required"),
  last_name: Yup.string().required("Required"),
  password: Yup.string()
    .min(8, "Password must be at least 8 characters")
    .required("Required"),
});

export const RegisterPage = () => {
  const mutation: UseMutationResult<void, Error, RegisterData> = useMutation({
    mutationFn: register,
    onSuccess: () => {
      console.log("Registration successful");
      alert("Registration successful!");
    },
    onError: (error: Error) => {
      console.error("Registration failed:", error);
      alert("Registration failed. Please try again.");
    },
  });

  return (
    <div>
      <h1>Register</h1>
      <Formik
        initialValues={{
          login: "",
          phone: "",
          first_name: "",
          middle_name: "",
          last_name: "",
          password: "",
        }}
        validationSchema={ProductSchema}
        onSubmit={(values, { resetForm }) => {
          mutation.mutate(values);
          resetForm();
        }}
      >
        {({ isSubmitting }) => (
          <Form>
            <div>
              <label htmlFor="login">Логин</label>
              <Field type="text" id="login" name="login" placeholder="Логин" />
              <ErrorMessage
                name="login"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <label htmlFor="phone">Номер телефона</label>
              <Field
                type="text"
                id="phone"
                name="phone"
                placeholder="Номер телефона"
              />
              <ErrorMessage
                name="phone"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <label htmlFor="first_name">Имя</label>
              <Field
                type="text"
                id="first_name"
                name="first_name"
                placeholder="Имя"
              />
              <ErrorMessage
                name="first_name"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <label htmlFor="middle_name">Отчество</label>
              <Field
                type="text"
                id="middle_name"
                name="middle_name"
                placeholder="Отчество"
              />
              <ErrorMessage
                name="middle_name"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <label htmlFor="last_name">Фамилия</label>
              <Field
                type="text"
                id="last_name"
                name="last_name"
                placeholder="Фамилия"
              />
              <ErrorMessage
                name="last_name"
                component="div"
                className="error-message"
              />
            </div>

            <div>
              <label htmlFor="password">Пароль</label>
              <Field
                type="password"
                id="password"
                name="password"
                placeholder="Пароль"
              />
              <ErrorMessage
                name="password"
                component="div"
                className="error-message"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting || mutation.status === "pending"}
            >
              {mutation.status === "pending"
                ? "Registering..."
                : "Зарегистрироваться"}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default RegisterPage;
