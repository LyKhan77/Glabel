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
