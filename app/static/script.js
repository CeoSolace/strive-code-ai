// app/static/script.js
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('input');
  const actionSelect = document.getElementById('action');
  const languageInput = document.getElementById('language');
  const submitBtn = document.getElementById('submit');
  const output = document.getElementById('output');
  const status = document.getElementById('status');
  const copyBtn = document.getElementById('copy');
  const downloadBtn = document.getElementById('download');

  let currentTaskId = null;

  // Auto-focus input
  input.focus();

  // Submit handler
  submitBtn.addEventListener('click', executeTask);
  input.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') executeTask();
  });

  async function executeTask() {
    const prompt = input.value.trim();
    if (!prompt) return;

    const action = actionSelect.value;
    const language = languageInput.value.trim() || 'python';

    // Build payload
    const payload = {
      action,
      language,
      purpose: prompt
    };

    if (action === 'transpile') {
      payload.code = prompt;
      payload.from = 'python';
      payload.to = language;
    } else if (action === 'reconstruct') {
      if (!prompt.startsWith('http')) {
        alert('Please enter a valid GitHub URL');
        return;
      }
      payload.github_url = prompt;
    } else if (action === 'unrestricted') {
      payload.intent = prompt;
    } else if (['debug', 'optimize', 'explain'].includes(action)) {
      payload.code = prompt;
    }

    // UI feedback
    status.textContent = 'EXECUTING...';
    status.style.color = '#ff0';
    output.innerHTML = '<code>// Processing request...</code>';
    submitBtn.disabled = true;

    try {
      const res = await fetch('/api/v1/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (data.error) throw new Error(data.error);

      // Display result
      const result = data.result || data;
      let display = '';

      if (result.code) {
        display = result.code;
      } else if (result.optimized_code) {
        display = result.optimized_code;
      } else if (result.explanation) {
        display = result.explanation;
      } else if (result.new_repo) {
        display = `Repo reconstructed!\n${result.new_repo}`;
      } else {
        display = JSON.stringify(result, null, 2);
      }

      output.innerHTML = `<code>${escapeHtml(display)}</code>`;
      status.textContent = 'SUCCESS';
      status.style.color = '#0f0';

      // Enable download if file
      if (result.pdf || result.image || result.audio) {
        currentTaskId = Date.now();
        downloadBtn.onclick = () => downloadFile(result);
      }

    } catch (err) {
      output.innerHTML = `<code class="error">// ERROR: ${escapeHtml(err.message)}</code>`;
      status.textContent = 'FAILED';
      status.style.color = '#f00';
    } finally {
      submitBtn.disabled = false;
    }
  }

  // Copy to clipboard
  copyBtn.addEventListener('click', () => {
    const code = output.textContent;
    navigator.clipboard.writeText(code).then(() => {
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = 'Copy', 2000);
    });
  });

  // Download file
  function downloadFile(result) {
    let url, filename, type;
    if (result.pdf) {
      url = result.pdf; type = 'pdf'; filename = 'strive-output.pdf';
    } else if (result.image) {
      url = result.image; type = 'png'; filename = 'diagram.png';
    } else if (result.audio) {
      url = result.audio; type = 'mp3'; filename = 'explanation.mp3';
    }

    if (!url) return;

    const link = document.createElement('a');
    link.href = url.startsWith('http') ? url : `/download/${type}?task_id=${currentTaskId}`;
    link.download = filename;
    link.click();
  }

  // Utility
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Matrix rain effect
  const canvas = document.createElement('canvas');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '-1';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
  const fontSize = 14;
  const columns = canvas.width / fontSize;

  const drops = Array(Math.floor(columns)).fill(1);

  function draw() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0f0';
    ctx.font = `${fontSize}px monospace`;

    for (let i = 0; i < drops.length; i++) {
      const text = chars[Math.floor(Math.random() * chars.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;

      ctx.fillText(text, x, y);

      if (y > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  setInterval(draw, 35);

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });
});
