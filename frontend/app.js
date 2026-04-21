const API = "https://claude-apps-tymn.onrender.com";

// Tag selection
document.querySelectorAll(".tag").forEach(tag => {
  tag.addEventListener("click", () => tag.classList.toggle("active"));
});

// Form submit
document.getElementById("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("submit-btn");
  const errEl = document.getElementById("form-error");
  errEl.classList.add("hidden");
  btn.disabled = true;
  btn.textContent = "Saving...";

  const hobbies = document.getElementById("hobbies").value
    .split(",").map(s => s.trim()).filter(Boolean);

  const interests = [...document.querySelectorAll(".tag.active")]
    .map(t => t.dataset.value);

  const payload = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    hobbies,
    interests,
  };

  try {
    const res = await fetch(`${API}/api/profiles`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Something went wrong");
    }

    e.target.reset();
    document.querySelectorAll(".tag").forEach(t => t.classList.remove("active"));
    showBanner("Profile saved successfully!");
    loadProfiles();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Profile";
  }
});

document.getElementById("refresh-btn").addEventListener("click", loadProfiles);

async function loadProfiles() {
  const list = document.getElementById("profiles-list");
  list.innerHTML = '<p class="muted">Loading...</p>';
  try {
    const res = await fetch(`${API}/api/profiles`);
    const profiles = await res.json();

    if (!profiles.length) {
      list.innerHTML = '<p class="muted">No profiles yet. Be the first!</p>';
      return;
    }

    list.innerHTML = profiles.map(p => `
      <div class="profile-card" id="profile-${p.id}">
        <div class="profile-info">
          <h3>${escHtml(p.name)}</h3>
          <div class="email">${escHtml(p.email)}</div>
          <div class="chips">
            ${p.interests.map(i => `<span class="chip">${escHtml(i)}</span>`).join("")}
            ${p.hobbies.map(h => `<span class="chip hobby">${escHtml(h)}</span>`).join("")}
          </div>
        </div>
        <button class="btn-delete" title="Delete" onclick="deleteProfile(${p.id})">&#x2715;</button>
      </div>
    `).join("");
  } catch {
    list.innerHTML = '<p class="muted">Could not load profiles. Is the backend running?</p>';
  }
}

async function deleteProfile(id) {
  if (!confirm("Delete this profile?")) return;
  await fetch(`${API}/api/profiles/${id}`, { method: "DELETE" });
  document.getElementById(`profile-${id}`)?.remove();
  if (!document.querySelector(".profile-card")) {
    document.getElementById("profiles-list").innerHTML =
      '<p class="muted">No profiles yet. Be the first!</p>';
  }
}

function showBanner(msg) {
  const existing = document.querySelector(".success-banner");
  if (existing) existing.remove();
  const banner = document.createElement("div");
  banner.className = "success-banner";
  banner.textContent = msg;
  document.getElementById("profile-form").prepend(banner);
  setTimeout(() => banner.remove(), 3000);
}

function escHtml(str) {
  return str.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

loadProfiles();
