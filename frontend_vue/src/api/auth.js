import client from "./client";

export async function registerApi(payload) {
  const { data } = await client.post("/auth/register/", payload);
  return data;
}

export async function loginApi(payload) {
  const { data } = await client.post("/auth/login/", payload);
  return data;
}

export async function meApi() {
  const { data } = await client.get("/auth/me/");
  return data;
}

export async function updateMeApi(payload) {
  const { data } = await client.put("/auth/me/", payload);
  return data;
}
