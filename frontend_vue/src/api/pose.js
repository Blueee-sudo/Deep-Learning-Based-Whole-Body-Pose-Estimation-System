import client from "./client";

export async function inferImage(formData, actionType = "squat") {
  if (formData && typeof formData.append === "function" && !formData.has("action_type")) {
    formData.append("action_type", actionType);
  }
  const { data } = await client.post("/pose/image/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function inferVideo(formData) {
  const { data } = await client.post("/pose/video/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 0,
  });
  return data;
}

export async function downloadVideoResult(detectionId) {
  const response = await client.get(`/pose/video/${detectionId}/result/`, {
    responseType: "blob",
  });
  return response;
}

export async function getVideoProgress(detectionId) {
  const { data } = await client.get(`/pose/video/${detectionId}/progress/`);
  return data;
}

export async function inferRealtimeFrame(base64Frame) {
  const { data } = await client.post("/pose/realtime/frame/", { frame: base64Frame });
  return data;
}

export async function downloadImageResult(detectionId) {
  const response = await client.get(`/pose/image/${detectionId}/result/`, {
    responseType: "blob",
  });
  return response;
}

export async function listPoseHistory(params = {}) {
  const { data } = await client.get("/pose/history/", { params });
  return data;
}
