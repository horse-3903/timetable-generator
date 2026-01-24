const form = document.getElementById("build-form");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

const setStatus = (text, tone = "idle") => {
  statusEl.textContent = text;
  statusEl.dataset.tone = tone;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Building...", "busy");
  resultEl.textContent = "Creating calendar and inserting events...";

  const data = Object.fromEntries(new FormData(form).entries());
  const payload = {
    calendar_name: data.calendar_name,
    owner_email: data.owner_email,
    year: Number(data.year),
    concurrency: Number(data.concurrency),
  };

  try {
    const response = await fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Request failed.");
    }

    const { calendar_id } = await response.json();
    setStatus("Complete", "ok");
    resultEl.textContent = `Calendar created: ${calendar_id}`;
  } catch (error) {
    setStatus("Error", "error");
    resultEl.textContent = error.message;
  }
});
