import client from "./client";

export async function listHistory(params) {
  const { data } = await client.get("/history/", { params });
  return data;
}

export async function getHistoryDetail(detectionId, params = {}) {
  const { data } = await client.get(`/history/${detectionId}/`, { params });
  return data;
}

export async function deleteHistory(detectionId) {
  const { data } = await client.delete(`/history/${detectionId}/delete/`);
  return data;
}

export async function exportHistoryFile(fmt = "csv", params = {}) {
  const { data, headers } = await client.get("/history/export/", {
    params: { ...params, fmt },
    responseType: "blob",
  });
  return { data, headers };
}
