function machineAction(action) {
  const feedback = document.getElementById('action-feedback');
  const msg = document.getElementById('action-feedback-msg');
  if (!feedback || !msg) return;
  feedback.classList.remove('hidden');

  if (action === 'stop') {
    msg.textContent = 'Emergency stop triggered.';
    callStop();
  } else if (action === 'start') {
    msg.textContent = 'Start command queued.';
    (async () => {
      const data = await callPushApi("/api/start");
      console.log(data);
      if (!data["started"]) {
        AlarmManager.add(data["message"], "Program");
      }
    })()
  } else if (action === 'pause') {
    msg.textContent = 'Pause command queued.';
    togglePause();
  } else if (action === "enable") {
    msg.textContent = "Enable command queued.";
    (async () => {
      const data = await callPushApi("/api/enable");
      if (!data["success"]) {
        AlarmManager.add(data["message"], "Enable");
      }
    })();
  } else if (action === "estop") {
    msg.textContent = "Emergency stop triggered.";
    toggleEStop();
  } else {
    msg.textContent = `Action: ${action}`;
  }

  setTimeout(() => feedback.classList.add('hidden'), 1400);
}
