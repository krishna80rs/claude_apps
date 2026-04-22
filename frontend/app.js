const API = "https://claude-apps-tymn.onrender.com";

// ── Navigation ──
function showView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById("view-" + name).classList.add("active");
  document.getElementById("nav-" + name).classList.add("active");
  if (name === "report") loadProfiles();
}

// ── Load profiles (report view) ──
async function loadProfiles() {
  const list = document.getElementById("profiles-list");
  list.innerHTML = '<div class="loading-state">Loading members...</div>';

  try {
    const res = await fetch(`${API}/api/profiles`);
    const profiles = await res.json();

    // update counters
    document.getElementById("member-count").textContent = `${profiles.length} member${profiles.length !== 1 ? "s" : ""}`;
    document.getElementById("side-count").textContent = profiles.length;

    if (!profiles.length) {
      list.innerHTML = '<div class="empty-state">No members yet — add the first entry.</div>';
      return;
    }

    list.innerHTML = `
      <table class="report-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Joined</th>
            <th style="text-align:right">Actions</th>
          </tr>
        </thead>
        <tbody id="profile-tbody">
          ${profiles.map(p => profileRow(p)).join("")}
        </tbody>
      </table>`;
  } catch {
    list.innerHTML = '<div class="empty-state">Could not reach backend. Is it running?</div>';
  }
}

function profileRow(p) {
  const date = new Date(p.created_at + "Z").toLocaleDateString("en-GB", { day:"2-digit", month:"short", year:"numeric" });
  return `
    <tr id="row-${p.id}">
      <td><div class="member-name">${esc(p.name)}</div></td>
      <td><div class="member-email">${esc(p.email)}</div></td>
      <td><div class="member-since">${date}</div></td>
      <td>
        <div class="td-actions" style="justify-content:flex-end">
          <button class="btn-bio" id="bio-btn-${p.id}" onclick="toggleBio(${p.id})">Bio</button>
          <button class="btn-del" onclick="deleteProfile(${p.id})" title="Delete">✕</button>
        </div>
      </td>
    </tr>
    <tr class="bio-row" id="bio-row-${p.id}" style="display:none">
      <td colspan="4">
        <div class="bio-drawer">
          <div class="bio-grid">
            <div class="bio-section">
              <label>Interests</label>
              <div class="chips">
                ${p.interests.length ? p.interests.map(i => `<span class="chip">${esc(i)}</span>`).join("") : "<span style='color:#9ca3af;font-size:.8rem'>None</span>"}
              </div>
            </div>
            <div class="bio-section">
              <label>Hobbies</label>
              <div class="chips">
                ${p.hobbies.length ? p.hobbies.map(h => `<span class="chip hobby">${esc(h)}</span>`).join("") : "<span style='color:#9ca3af;font-size:.8rem'>None</span>"}
              </div>
            </div>
            <div class="bio-section">
              <label>Document</label>
              ${p.document_name
                ? `<a class="doc-link" href="${API}/api/profiles/${p.id}/document" target="_blank">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    ${esc(p.document_name)}
                   </a>`
                : `<span style="color:#9ca3af;font-size:.8rem">No document</span>`}
            </div>
          </div>
        </div>
      </td>
    </tr>`;
}

function toggleBio(id) {
  const bioRow = document.getElementById("bio-row-" + id);
  const btn = document.getElementById("bio-btn-" + id);
  const open = bioRow.style.display === "none";
  bioRow.style.display = open ? "table-row" : "none";
  btn.classList.toggle("open", open);
  btn.textContent = open ? "Close" : "Bio";
}

async function deleteProfile(id) {
  if (!confirm("Delete this member?")) return;
  await fetch(`${API}/api/profiles/${id}`, { method: "DELETE" });
  document.getElementById("row-" + id)?.remove();
  document.getElementById("bio-row-" + id)?.remove();
  const remaining = document.querySelectorAll("#profile-tbody tr:not(.bio-row)").length;
  document.getElementById("member-count").textContent = `${remaining} member${remaining !== 1 ? "s" : ""}`;
  document.getElementById("side-count").textContent = remaining;
  if (!remaining) loadProfiles();
}

// ── File upload area ──
const docInput = document.getElementById("doc-file");
const uploadArea = document.getElementById("upload-area");
const uploadLabel = document.getElementById("upload-label");

docInput.addEventListener("change", () => {
  if (docInput.files[0]) {
    uploadLabel.textContent = docInput.files[0].name;
    uploadArea.classList.add("has-file");
  } else {
    uploadLabel.textContent = "Click to select a file";
    uploadArea.classList.remove("has-file");
  }
});

// drag-and-drop
uploadArea.addEventListener("dragover", e => { e.preventDefault(); uploadArea.classList.add("has-file"); });
uploadArea.addEventListener("dragleave", () => { if (!docInput.files[0]) uploadArea.classList.remove("has-file"); });
uploadArea.addEventListener("drop", e => {
  e.preventDefault();
  if (e.dataTransfer.files[0]) {
    docInput.files = e.dataTransfer.files;
    uploadLabel.textContent = e.dataTransfer.files[0].name;
    uploadArea.classList.add("has-file");
  }
});

// tag selection
document.querySelectorAll(".tag").forEach(tag =>
  tag.addEventListener("click", () => tag.classList.toggle("active"))
);

// ── Form submit ──
document.getElementById("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("submit-btn");
  const errEl = document.getElementById("form-error");
  errEl.classList.add("hidden");
  btn.disabled = true;
  btn.textContent = "Saving...";

  const hobbies = document.getElementById("hobbies").value
    .split(",").map(s => s.trim()).filter(Boolean);
  const interests = [...document.querySelectorAll(".tag.active")].map(t => t.dataset.value);

  const fd = new FormData();
  fd.append("name", document.getElementById("name").value.trim());
  fd.append("email", document.getElementById("email").value.trim());
  fd.append("hobbies", JSON.stringify(hobbies));
  fd.append("interests", JSON.stringify(interests));
  if (docInput.files[0]) fd.append("document", docInput.files[0]);

  try {
    const res = await fetch(`${API}/api/profiles`, { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Something went wrong");
    }
    resetForm();
    showBanner("Profile saved! Switch to Report to view it.");
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Save Profile";
  }
});

function resetForm() {
  document.getElementById("profile-form").reset();
  document.querySelectorAll(".tag").forEach(t => t.classList.remove("active"));
  uploadLabel.textContent = "Click to select a file";
  uploadArea.classList.remove("has-file");
}

function showBanner(msg) {
  const existing = document.querySelector(".success-banner");
  if (existing) existing.remove();
  const b = document.createElement("div");
  b.className = "success-banner";
  b.textContent = msg;
  document.getElementById("form-error").before(b);
  setTimeout(() => b.remove(), 4000);
}

function esc(str) {
  return String(str).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// init
loadProfiles();
