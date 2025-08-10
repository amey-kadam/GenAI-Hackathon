const form = document.getElementById('promptForm');
const output = document.getElementById('output');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  if (!prompt) return;

  output.textContent = 'Generating…';
  try {
    const res = await fetch('/api/spec', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = 'Error: ' + (err?.message || err);
  }
});