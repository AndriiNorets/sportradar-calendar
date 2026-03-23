const API_BASE = "http://localhost:8000";

async function fetchEvents(sport = "", date = "") {
  const params = new URLSearchParams();
  if (sport) params.set("sport", sport);
  if (date) params.set("date", date);

  const url = `${API_BASE}/events/?${params}`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

function formatScore(result) {
  if (!result) return "—";
  return `${result.home_goals} – ${result.away_goals}`;
}

function formatTime(t) {
  if (!t) return "—";
  return t.slice(0, 5);
}

function renderEvents(events) {
  const tbody = document.getElementById("events-body");
  if (events.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="loading">No events found.</td></tr>';
    return;
  }

  tbody.innerHTML = events
    .map(
      (e) => `
    <tr>
      <td>${e.date_venue}</td>
      <td>${formatTime(e.time_venue_utc)}</td>
      <td>${e.sport.name}</td>
      <td>${e.home_team?.name ?? "?"} vs ${e.away_team?.name ?? "?"}</td>
      <td><span class="badge badge-${e.status}">${e.status}</span></td>
      <td>${formatScore(e.result)}</td>
    </tr>`
    )
    .join("");
}

function showError(msg) {
  const el = document.getElementById("error-msg");
  el.textContent = msg;
  el.classList.remove("hidden");
}

function hideError() {
  document.getElementById("error-msg").classList.add("hidden");
}

async function loadEvents() {
  const sport = document.getElementById("filter-sport").value.trim();
  const date = document.getElementById("filter-date").value;
  hideError();
  try {
    const events = await fetchEvents(sport, date);
    renderEvents(events);
  } catch (err) {
    showError(`Failed to load events: ${err.message}`);
    document.getElementById("events-body").innerHTML =
      '<tr><td colspan="6" class="loading">—</td></tr>';
  }
}

document.getElementById("btn-apply").addEventListener("click", loadEvents);

document.getElementById("btn-clear").addEventListener("click", () => {
  document.getElementById("filter-sport").value = "";
  document.getElementById("filter-date").value = "";
  loadEvents();
});

loadEvents();
