// ==========================================================================
// OmniSave - Client Application Logic
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // DOM References
  const htmlRoot = document.documentElement;
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const themeLabelText = document.getElementById('theme-label-text');
  const currentThemeName = document.getElementById('current-theme-name');

  const platformTabs = document.querySelectorAll('.tab-btn');
  const btnFmtVideo = document.getElementById('btn-fmt-video');
  const btnFmtAudio = document.getElementById('btn-fmt-audio');

  const mediaForm = document.getElementById('media-form');
  const urlInput = document.getElementById('media-url');
  const inputShell = document.getElementById('input-shell');
  const pasteBtn = document.getElementById('paste-action-btn');
  const clearBtn = document.getElementById('clear-action-btn');
  const mainDownloadBtn = document.getElementById('main-download-btn');

  const platformDetectBadge = document.getElementById('platform-detect-badge');
  const detectBadgeText = document.getElementById('detect-badge-text');

  const statusBox = document.getElementById('status-box');
  const statusTitle = document.getElementById('status-title');
  const statusDesc = document.getElementById('status-desc');

  const errorBox = document.getElementById('error-box');
  const errorTitle = document.getElementById('error-title');
  const errorMsg = document.getElementById('error-msg');

  const resultBox = document.getElementById('result-box');
  const resPlatformTag = document.getElementById('res-platform-tag');
  const resThumbnail = document.getElementById('res-thumbnail');
  const resDuration = document.getElementById('res-duration');
  const resUploader = document.getElementById('res-uploader');
  const resTitle = document.getElementById('res-title');
  const resFormatPill = document.getElementById('res-format-pill');
  const resSizePill = document.getElementById('res-size-pill');

  const resPlayerWrap = document.getElementById('res-player-wrap');
  const resVideoPlayer = document.getElementById('res-video-player');
  const resAudioPlayer = document.getElementById('res-audio-player');

  const resDirectDownloadBtn = document.getElementById('res-direct-download-btn');
  const resDownloadBtnLabel = document.getElementById('res-download-btn-label');
  const resPreviewToggleBtn = document.getElementById('res-preview-toggle-btn');
  const resToggleFormatBtn = document.getElementById('res-toggle-format-btn');
  const resToggleFormatLabel = document.getElementById('res-toggle-format-label');

  const toast = document.getElementById('toast');

  let currentFormat = 'video';
  let activePlatformFilter = 'all';
  let lastResultData = null;
  let statusCycleTimer = null;

  // --------------------------------------------------------------------------
  // Theme Toggle (Default: Dark, with Light Mode switch)
  // --------------------------------------------------------------------------
  function applyTheme(theme) {
    htmlRoot.setAttribute('data-theme', theme);
    localStorage.setItem('omnisave-theme', theme);

    if (theme === 'light') {
      themeLabelText.textContent = 'Dark Mode';
      if (currentThemeName) currentThemeName.textContent = 'Light';
    } else {
      themeLabelText.textContent = 'Light Mode';
      if (currentThemeName) currentThemeName.textContent = 'Dark';
    }
  }

  // Load saved theme or default to dark
  const savedTheme = localStorage.getItem('omnisave-theme') || 'dark';
  applyTheme(savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = htmlRoot.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    showToast(`Switched to ${newTheme.charAt(0).toUpperCase() + newTheme.slice(1)} Mode`);
  });

  // --------------------------------------------------------------------------
  // Format Selection (Video MP4 vs Audio MP3)
  // --------------------------------------------------------------------------
  function setFormat(fmt) {
    currentFormat = fmt;
    if (fmt === 'video') {
      btnFmtVideo.classList.add('active');
      btnFmtAudio.classList.remove('active');
      resToggleFormatLabel.textContent = 'Extract Audio (MP3)';
    } else {
      btnFmtAudio.classList.add('active');
      btnFmtVideo.classList.remove('active');
      resToggleFormatLabel.textContent = 'Download Video (MP4)';
    }
  }

  btnFmtVideo.addEventListener('click', () => setFormat('video'));
  btnFmtAudio.addEventListener('click', () => setFormat('audio'));

  // --------------------------------------------------------------------------
  // Platform Filter Tabs
  // --------------------------------------------------------------------------
  const placeholders = {
    all: 'Paste Instagram, YouTube, or Facebook video/reel link here...',
    instagram: 'Paste Instagram Reel or Post link (e.g. https://www.instagram.com/reel/...)',
    youtube: 'Paste YouTube Shorts or Video link (e.g. https://youtube.com/shorts/...)',
    facebook: 'Paste Facebook Video or Reel link (e.g. https://www.facebook.com/watch/...)'
  };

  platformTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      platformTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activePlatformFilter = tab.dataset.platform;
      urlInput.placeholder = placeholders[activePlatformFilter] || placeholders.all;
      urlInput.focus();
    });
  });

  // --------------------------------------------------------------------------
  // Real-time Platform Detection
  // --------------------------------------------------------------------------
  function detectPlatformFromUrl(val) {
    const u = val.toLowerCase().trim();
    if (u.includes('instagram.com')) return 'instagram';
    if (u.includes('youtube.com') || u.includes('youtu.be')) return 'youtube';
    if (u.includes('facebook.com') || u.includes('fb.watch')) return 'facebook';
    return 'all';
  }

  function updateDetectBadge(val) {
    const p = detectPlatformFromUrl(val);
    platformDetectBadge.className = 'platform-detect-badge';

    if (p === 'instagram') {
      platformDetectBadge.classList.add('ig');
      detectBadgeText.textContent = 'Instagram';
    } else if (p === 'youtube') {
      platformDetectBadge.classList.add('yt');
      detectBadgeText.textContent = 'YouTube';
    } else if (p === 'facebook') {
      platformDetectBadge.classList.add('fb');
      detectBadgeText.textContent = 'Facebook';
    } else {
      detectBadgeText.textContent = 'Auto';
    }
  }

  urlInput.addEventListener('input', () => {
    const val = urlInput.value.trim();
    clearBtn.style.display = val.length > 0 ? 'block' : 'none';
    updateDetectBadge(val);
  });

  clearBtn.addEventListener('click', () => {
    urlInput.value = '';
    clearBtn.style.display = 'none';
    updateDetectBadge('');
    urlInput.focus();
  });

  // --------------------------------------------------------------------------
  // Paste Button
  // --------------------------------------------------------------------------
  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text && text.trim().length > 0) {
        urlInput.value = text.trim();
        clearBtn.style.display = 'block';
        updateDetectBadge(urlInput.value);
        showToast('Pasted link from clipboard');
        urlInput.focus();
      } else {
        showToast('Clipboard is empty.');
      }
    } catch (_) {
      urlInput.focus();
      showToast('Press Ctrl+V to paste your link.');
    }
  });

  // --------------------------------------------------------------------------
  // Toast notifications
  // --------------------------------------------------------------------------
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  // --------------------------------------------------------------------------
  // Status Animation
  // --------------------------------------------------------------------------
  const steps = [
    { title: 'Connecting to server...', desc: 'Resolving media stream and validating source' },
    { title: 'Extracting media tracks...', desc: 'Fetching highest quality available stream' },
    { title: 'Finalizing file...', desc: 'Encoding container and preparing download' }
  ];

  function startStatus(format) {
    statusBox.style.display = 'flex';
    errorBox.style.display = 'none';
    resultBox.style.display = 'none';
    mainDownloadBtn.disabled = true;

    let idx = 0;
    const cycle = () => {
      const s = steps[idx % steps.length];
      statusTitle.textContent = s.title;
      statusDesc.textContent = format === 'audio' && idx === 2
        ? 'Extracting and encoding high-bitrate 192kbps MP3 audio...'
        : s.desc;
      idx++;
    };

    cycle();
    statusCycleTimer = setInterval(cycle, 2200);
  }

  function stopStatus() {
    if (statusCycleTimer) {
      clearInterval(statusCycleTimer);
      statusCycleTimer = null;
    }
    statusBox.style.display = 'none';
    mainDownloadBtn.disabled = false;
  }

  // --------------------------------------------------------------------------
  // Error handling
  // --------------------------------------------------------------------------
  function showError(title, message) {
    stopStatus();
    errorTitle.textContent = title || 'Error';
    errorMsg.textContent = message || 'Could not complete request.';
    errorBox.style.display = 'flex';
  }

  window.dismissError = function() {
    errorBox.style.display = 'none';
  };

  // --------------------------------------------------------------------------
  // Form Submission
  // --------------------------------------------------------------------------
  mediaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const rawUrl = urlInput.value.trim();

    if (!rawUrl) {
      showError('Empty Input', 'Please paste a valid video or reel link before proceeding.');
      urlInput.focus();
      return;
    }

    await performDownload(rawUrl, currentFormat);
  });

  // --------------------------------------------------------------------------
  // Download API Request
  // --------------------------------------------------------------------------
  async function performDownload(url, format) {
    startStatus(format);

    try {
      const res = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, format: format })
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to download media.');
      }

      displayResult(data.data);
    } catch (err) {
      showError('Download Failed', err.message);
    } finally {
      stopStatus();
    }
  }

  // --------------------------------------------------------------------------
  // Display Download Result
  // --------------------------------------------------------------------------
  function displayResult(data) {
    lastResultData = data;
    errorBox.style.display = 'none';

    // Platform tag
    resPlatformTag.textContent = data.platform_name || 'Media';
    resTitle.textContent = data.title || 'Media Video';
    resUploader.textContent = data.uploader ? `@${data.uploader}` : '@Creator';
    
    // Format tag
    resFormatPill.textContent = data.format === 'video' ? '🎬 Video (MP4)' : '🎵 Audio (MP3)';
    resSizePill.textContent = `${data.file_size_mb} MB`;

    // Download action button
    resDirectDownloadBtn.href = data.download_url;
    resDirectDownloadBtn.setAttribute('download', data.suggested_filename);
    resDownloadBtnLabel.textContent = data.format === 'video' ? 'Save Video (MP4)' : 'Save Audio (MP3)';

    // Switch format label
    if (data.format === 'video') {
      resToggleFormatLabel.textContent = 'Extract Audio (MP3)';
    } else {
      resToggleFormatLabel.textContent = 'Download Video (MP4)';
    }

    // Media players
    resVideoPlayer.pause();
    resAudioPlayer.pause();
    resVideoPlayer.style.display = 'none';
    resAudioPlayer.style.display = 'none';
    resPlayerWrap.style.display = 'none';

    if (data.format === 'video') {
      resVideoPlayer.src = data.preview_url;
      resVideoPlayer.style.display = 'block';
    } else {
      resAudioPlayer.src = data.preview_url;
      resAudioPlayer.style.display = 'block';
    }

    // Fetch live thumbnail
    fetchThumbnailInfo(urlInput.value.trim());

    // Show result card
    resultBox.style.display = 'block';
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Trigger direct browser download
    triggerBrowserSave(data.download_url);
    showToast('Download started automatically!');
  }

  async function fetchThumbnailInfo(url) {
    try {
      const res = await fetch('/api/info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const json = await res.json();
      if (json.success && json.data) {
        if (json.data.thumbnail) {
          resThumbnail.src = json.data.thumbnail;
        }
        if (json.data.duration_str) {
          resDuration.textContent = json.data.duration_str;
        }
      }
    } catch (_) {
      resThumbnail.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='180' viewBox='0 0 140 180'%3E%3Crect width='100%25' height='100%25' fill='%23111'/%3E%3Ctext x='50%25' y='50%25' fill='%23666' dominant-baseline='middle' text-anchor='middle'%3EMedia%3C/text%3E%3C/svg%3E";
    }
  }

  function triggerBrowserSave(url) {
    const a = document.createElement('a');
    a.href = url;
    a.setAttribute('download', '');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // --------------------------------------------------------------------------
  // Preview toggle button
  // --------------------------------------------------------------------------
  resPreviewToggleBtn.addEventListener('click', () => {
    if (resPlayerWrap.style.display === 'none') {
      resPlayerWrap.style.display = 'block';
      resPreviewToggleBtn.querySelector('span').textContent = 'Hide Preview';
      if (lastResultData?.format === 'video') {
        resVideoPlayer.play().catch(() => {});
      } else {
        resAudioPlayer.play().catch(() => {});
      }
    } else {
      resPlayerWrap.style.display = 'none';
      resPreviewToggleBtn.querySelector('span').textContent = 'Preview';
      resVideoPlayer.pause();
      resAudioPlayer.pause();
    }
  });

  // --------------------------------------------------------------------------
  // Switch format button
  // --------------------------------------------------------------------------
  resToggleFormatBtn.addEventListener('click', () => {
    const nextFmt = currentFormat === 'video' ? 'audio' : 'video';
    setFormat(nextFmt);
    const rawUrl = urlInput.value.trim();
    if (rawUrl) {
      performDownload(rawUrl, nextFmt);
    }
  });
});
