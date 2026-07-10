const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

async function handleResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }
  return data;
}

export async function extractText(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${BASE_URL}/api/extract`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(response);
}

export async function summarizeText(text, length) {
  const response = await fetch(`${BASE_URL}/api/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, length }),
  });
  return handleResponse(response);
}

export async function getSuggestions(text) {
  const response = await fetch(`${BASE_URL}/api/suggestions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return handleResponse(response);
}

export async function processDocument(file, length) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("length", length);
  const response = await fetch(`${BASE_URL}/api/process`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(response);
}
