const API_BASE = "http://localhost:8000";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/documents`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Upload failed");
  }

  return response.json();
}

export async function listDocuments() {
  const response = await fetch(`${API_BASE}/api/documents`);
  if (!response.ok) throw new Error("Failed to fetch documents");
  return response.json();
}

export async function deleteDocument(docId) {
  const response = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete document");
}

export async function askQuestion(question) {
  const response = await fetch(`${API_BASE}/api/chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get answer");
  }

  return response.json();
}