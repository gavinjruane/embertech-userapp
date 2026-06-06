async function pollForStatus () {
  try {
    const response = await fetch("api/state");
    const status = await response.json();

    updateUI(status["state"]);
  } catch ( error ) {
    console.warn("Polling failed with error", error);
  } finally {
    setTimeout(pollForStatus, 3000);
  }
}

const AlarmManager = {
  alarms: [],
  add(message, type = 'alarm') {
    const existing = this.alarms.find((alarm) => alarm.type === type);
    if (existing) {
      existing.message = message;
    } else {
      this.alarms.push({ type, message });
    }
    this.render();
  },
  render() {
    const list = document.getElementById('alarm-list');
    const count = document.getElementById('alarm-count');
    const empty = document.getElementById('alarm-empty');
    if (!list || !count || !empty) return;

    list.querySelectorAll('.alarm-item').forEach((item) => item.remove());

    if (this.alarms.length === 0) {
      empty.classList.remove('hidden');
      count.textContent = '0';
      count.classList.remove('has-alarms');
      return;
    }

    empty.classList.add('hidden');
    this.alarms.forEach((alarm) => {
      const alarmItem = document.createElement('div');
      alarmItem.className = 'alarm-item';
      alarmItem.innerHTML = `
        <span class="alarm-label">${alarm.type.toUpperCase()}</span>
        <span>${alarm.message}</span>
      `;
      list.appendChild(alarmItem);
    });
    count.textContent = String(this.alarms.length);
    count.classList.add('has-alarms');
  }
};

function setGlobalAlarm(message) {
  const pill = document.getElementById('global-alarm-pill');
  const text = document.getElementById('global-alarm-text');
  if (!pill || !text) return;
  pill.classList.remove('hidden');
  text.textContent = message;
}

function triggerEStop(source = 'keyboard') {
  if (window.eStopTriggered) return;
  window.eStopTriggered = true;
  const message = 'Emergency stop activated via ' + source + '. Machine is halted.';
  AlarmManager.add(message, 'E-STOP');
  setGlobalAlarm('E-STOP ACTIVE');
  callEStopApi(source);
}

function callEStopApi(source = 'keyboard') {
  fetch('/api/estop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source })
  })
    .then((res) => res.json())
    .then((data) => {
      if (!data.success) {
        console.error('E-stop API response failure', data);
      }
    })
    .catch((err) => {
      console.warn('E-stop API request failed (no backend yet)', err);
    });
}

document.addEventListener('keydown', (event) => {
  if (event.code !== 'Space' || event.repeat) return;
  const tag = event.target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || event.target.isContentEditable) return;
  event.preventDefault();
  triggerEStop('spacebar');
});
