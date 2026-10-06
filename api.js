// Mock REST endpoint (JSONPlaceholder echoes the POST body with an id and status 201).
export const API_URL = 'https://jsonplaceholder.typicode.com/posts';

export async function sendMessage({ name, email, message }) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=UTF-8' },
    body: JSON.stringify({ title: name, email, body: message }),
  });
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}
