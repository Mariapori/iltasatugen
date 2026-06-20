/**
 * API-kutsut backendille.
 * Vite proxy ohjaa /api-pyydökset localhost:8000:lle.
 */

const BASE = '/api';

/** Hae kaikki iltasatuja */
export async function fetchStories() {
  const res = await fetch(`${BASE}/stories`);
  if (!res.ok) throw new Error(`Hakuvirhe: ${res.status}`);
  return res.json();
}

/** Hae yksi iltasatu */
export async function fetchStory(id) {
  const res = await fetch(`${BASE}/stories/${id}`);
  if (!res.ok) throw new Error(`Hakuvirhe: ${res.status}`);
  return res.json();
}

/** Luo uusi iltasatu */
export async function createStory(title, content) {
  const res = await fetch(`${BASE}/stories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Luontivirhe: ${res.status}`);
  }
  return res.json();
}

/** Poista iltasatu */
export async function deleteStory(id) {
  const res = await fetch(`${BASE}/stories/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`Poistovirhe: ${res.status}`);
  return res.json();
}

/** Generoi ääni iltasadulle (TTS) */
export async function generateAudio(id) {
  const res = await fetch(`${BASE}/stories/${id}/generate`, { method: 'POST' });
  if (!res.ok) throw new Error(`Generointivirhe: ${res.status}`);
  return res.json();
}

/** Palauta äänitiedoston URL */
export function audioUrl(id) {
  return `${BASE}/stories/${id}/audio`;
}