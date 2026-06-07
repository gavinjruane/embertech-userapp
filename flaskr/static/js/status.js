async function pollForStatus () {
  try {
    const response = await fetch("api/state");
    const status = await response.json();
    // console.log("JSON", status);
    const state = status["state"];

    if ( state["error"] ) {
      AlarmManager.add(state["error"]["error"]);
    }
    updateUI(state);
  } catch ( error ) {
    console.warn("Polling failed with error", error);
  } finally {
    setTimeout(pollForStatus, 500);
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

function toggleEStop() {
  if ( window.eStopTriggered ) {
    window.eStopTriggered = false;
    AlarmManager.add("Emergency stop deactivated. Machine is ready.", "E-STOP RESET");
    setGlobalAlarm("E-STOP INACTIVE");
    callPushApi("/api/estop_reset");
  } else {
    window.eStopTriggered = true;
    // const message = 'Emergency stop activated via ' + source + '. Machine is halted.';
    AlarmManager.add("Emergency stop activated. Machine is halted.", 'E-STOP');
    setGlobalAlarm('E-STOP ACTIVE');
    callPushApi("/api/estop")
  }
}

function togglePause() {
  if ( window.taskState === "PAUSED" ) {
    callPushApi("/api/unpause");
  } else {
    callPushApi("/api/pause");
  }
}

const callStop = () => { callPushApi("/api/stop") };

async function callPushApi(endpoint) {
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    })
    const data = await response.json();

    if ( ! data.success ) {
      console.error("Push API response failed", data);
    } else {
      return data;
    }
  } catch ( error ) {
    console.error("Push API request failed", error);
  }
}

document.addEventListener('keydown', (event) => {
  if (event.code !== 'Space' || event.repeat) return;
  const tag = event.target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || event.target.isContentEditable) return;
  event.preventDefault();
  triggerEStop('spacebar');
});
