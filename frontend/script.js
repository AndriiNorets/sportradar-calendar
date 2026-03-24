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

function populateSportDropdown(events) {
  const select = document.getElementById("filter-sport");
  const current = select.value;
  const sports = [...new Set(events.map((e) => e.sport.name))].sort();

  select.innerHTML = '<option value="">All Sports</option>';
  sports.forEach((sport) => {
    const opt = document.createElement("option");
    opt.value = sport;
    opt.textContent = sport;
    if (sport === current) opt.selected = true;
    select.appendChild(opt);
  });
}

async function loadEvents() {
  const sport = document.getElementById("filter-sport").value;
  const date = document.getElementById("filter-date").value;
  hideError();
  try {
    const allEvents = await fetchEvents("", "");
    populateSportDropdown(allEvents);

    const events = sport || date ? await fetchEvents(sport, date) : allEvents;
    renderEvents(events);
  } catch (err) {
    showError(`Failed to load events: ${err.message}`);
    document.getElementById("events-body").innerHTML =
      '<tr><td colspan="6" class="loading">—</td></tr>';
  }
}

document.getElementById("add-event-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));

  const feedback = document.getElementById("form-feedback");
  feedback.className = "form-feedback hidden";

  try {
    const resp = await fetch(`${API_BASE}/events/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date_venue: data.date_venue,
        time_venue_utc: data.time_venue_utc || null,
        sport: data.sport,
        home_team: data.home_team,
        away_team: data.away_team,
        description: data.description || null,
      }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    form.reset();
    feedback.textContent = "Event added!";
    feedback.className = "form-feedback success";
    loadEvents();
  } catch (err) {
    feedback.textContent = `Error: ${err.message}`;
    feedback.className = "form-feedback error";
  }
});

document.getElementById("btn-apply").addEventListener("click", loadEvents);

document.getElementById("btn-clear").addEventListener("click", () => {
  document.getElementById("filter-sport").value = "";
  document.getElementById("filter-date").value = "";
  loadEvents();
});

loadEvents();
