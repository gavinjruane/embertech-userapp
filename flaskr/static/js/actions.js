function machineAction(action) {
  const feedback = document.getElementById('action-feedback');
  const msg = document.getElementById('action-feedback-msg');
  if (!feedback || !msg) return;
  feedback.classList.remove('hidden');

  if (action === 'stop') {
    msg.textContent = 'Emergency stop triggered.';
    triggerEStop('stop-button');
  } else if (action === 'start') {
    msg.textContent = 'Start command queued.';
  } else if (action === 'pause') {
    msg.textContent = 'Pause command queued.';
  } else {
    msg.textContent = `Action: ${action}`;
  }

  setTimeout(() => feedback.classList.add('hidden'), 1400);
}
