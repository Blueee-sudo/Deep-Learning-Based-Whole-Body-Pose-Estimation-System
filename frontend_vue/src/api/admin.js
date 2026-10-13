import client from "./client";

export async function adminUsers(params) {
  const { data } = await client.get("/admin/users/", { params });
  return data;
}

export async function createAdminUser(payload) {
  const { data } = await client.post("/admin/users/", payload);
  return data;
}

export async function getAdminUser(userId) {
  const { data } = await client.get(`/admin/users/${userId}/`);
  return data;
}

export async function updateAdminUser(userId, payload) {
  const { data } = await client.put(`/admin/users/${userId}/`, payload);
  return data;
}

export async function deleteAdminUser(userId) {
  const { data } = await client.delete(`/admin/users/${userId}/`);
  return data;
}

export async function adminDetections(params) {
  const { data } = await client.get("/admin/detections/", { params });
  return data;
}

export async function adminLogs(params) {
  const { data } = await client.get("/admin/logs/", { params });
  return data;
}

export async function adminMetrics(params) {
  const { data } = await client.get("/admin/metrics/", { params });
  return data;
}

export async function adminMetricsPlot(params) {
  const { data } = await client.get("/admin/metrics/plot/", { params, responseType: "blob" });
  return data;
}
