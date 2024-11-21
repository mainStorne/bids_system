import api from "../base";
import { RegisterData } from "./types";

export const register = async (data: RegisterData): Promise<void> => {
  await api.post("/users/register", data);
};
