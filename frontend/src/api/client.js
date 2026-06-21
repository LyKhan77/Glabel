export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export function listProjects() {
  return request('/api/v1/projects/')
}

export function createProject(payload) {
  return request('/api/v1/projects/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function getProject(projectId) {
  return request(`/api/v1/projects/${projectId}`)
}

export function updateProject(projectId, payload) {
  return request(`/api/v1/projects/${projectId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function deleteProject(projectId) {
  return request(`/api/v1/projects/${projectId}`, {
    method: 'DELETE'
  })
}

export function listDatasetAssets(projectId, status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/api/v1/projects/${projectId}/dataset/assets${query}`)
}

export function uploadDatasetFiles(projectId, files, extractFps) {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  form.append('extract_fps', String(extractFps))
  return request(`/api/v1/projects/${projectId}/dataset/upload`, {
    method: 'POST',
    body: form
  })
}

export function autoAnnotateDataset(projectId) {
  return request(`/api/v1/projects/${projectId}/dataset/auto-annotate`, {
    method: 'POST'
  })
}

export function listDatasetVersions(projectId) {
  return request(`/api/v1/projects/${projectId}/versions`)
}

export function createDatasetVersion(projectId, payload) {
  return request(`/api/v1/projects/${projectId}/versions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

export function assignDatasetAssets(projectId, assetIds) {
  return request(`/api/v1/projects/${projectId}/dataset/assets/assign`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: assetIds })
  })
}

export function unassignDatasetAssets(projectId, assetIds) {
  return request(`/api/v1/projects/${projectId}/dataset/assets/unassign`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: assetIds })
  })
}

export function deleteDatasetAssets(projectId, assetIds) {
  return request(`/api/v1/projects/${projectId}/dataset/assets`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: assetIds })
  })
}

export function saveAssetAnnotations(projectId, assetId, annotations, status) {
  return request(`/api/v1/projects/${projectId}/dataset/assets/${assetId}/annotations`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ annotations, status })
  })
}

export async function getDatasetVersion(projectId, versionId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/versions/${versionId}`);
  if (!response.ok) throw new Error('Failed to fetch dataset version');
  return response.json();
}

export async function deleteDatasetVersion(projectId, versionId) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/versions/${versionId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete dataset version');
  return response.json();
}

export async function exportDatasetVersion(projectId, versionId, format) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/versions/${versionId}/export?format=${format}`, {
    method: 'POST'
  });
  if (!response.ok) throw new Error('Failed to export dataset version');
  // Return blob
  return response.blob();
}

export async function previewAugmentation(projectId, key, params, assetId = null) {
  const payload = { augmentation_key: key, params };
  if (assetId) payload.asset_id = assetId;

  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/dataset/preview-augmentation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error('Failed to preview augmentation');
  return response.blob();
}

export function listModels() {
  return request('/api/v1/models')
}

export function downloadModel(modelId) {
  return request(`/api/v1/models/${modelId}/download`, {
    method: 'POST'
  })
}

export function detectHardware() {
  return request('/api/v1/system/hardware')
}
