async function uploadVideo() {
  const input = document.getElementById('videoInput');
  const status = document.getElementById('status');
  const player = document.getElementById('player');

  if (!input.files.length) {
    alert('Please select a video file.');
    return;
  }

  const videoFile = input.files[0];
  const formData = new FormData();
  formData.append('file', videoFile);

  status.textContent = 'Uploading...';

  try {
    const response = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    status.textContent = `Upload successful!`;

    // Play the local file immediately
    player.src = URL.createObjectURL(videoFile);
    player.load();
    player.play();
  } catch (error) {
    status.textContent = 'Upload failed.';
    console.error(error);
  }
}

async function trimVideo() {
  const filename = document.getElementById('videoInput').files[0]?.name;
  const start = parseFloat(document.getElementById('startTime').value);
  const end = parseFloat(document.getElementById('endTime').value);
  const status = document.getElementById('status');
  const player = document.getElementById('player');

  if (!filename) {
    alert('Please upload a video first!');
    return;
  }
  if (start < 0 || end <= start) {
    alert('Please enter valid start and end times.');
    return;
  }

  status.textContent = 'Trimming video... This may take a moment.';

  try {
    // Call your backend trim endpoint with query params
    const response = await fetch(`http://127.0.0.1:8000/edit/trim?filename=${encodeURIComponent(filename)}&start=${start}&end=${end}`, {
      method: 'POST'
    });
    const result = await response.json();

    if (result.error) {
      status.textContent = `Error: ${result.error}`;
      return;
    }

    status.textContent = 'Trim complete! Playing trimmed video.';

    // Load trimmed video into player
    player.src = `http://127.0.0.1:8000${result.trimmed_video}`;
    player.load();
    player.play();
  } catch (e) {
    status.textContent = 'Failed to trim video.';
    console.error(e);
  }
}
