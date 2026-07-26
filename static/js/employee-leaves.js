(async () => {
  const me = await requireAuth("Employee");
  if (!me) return;
  loadLeaves();
})();

function statusBadge(status) {
  const cls = status === "Approved" ? "badge-success" : status === "Rejected" ? "badge-danger" : "badge-warning";
  return `<span class="badge ${cls}">${escapeHtml(status)}</span>`;
}

async function loadLeaves() {
  hideAlert("page-alert");
  const body = document.getElementById("leaves-body");
  body.innerHTML = '<tr><td colspan="5" class="empty-state">Loading...</td></tr>';
  try {
    const rows = await Api.get("/api/employee/leaves");
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state">No leave requests yet.</td></tr>';
      return;
    }
    body.innerHTML = rows.map(r => `
      <tr>
        <td>${escapeHtml(r.leave_type)}</td>
        <td>${escapeHtml(r.start_date)}</td>
        <td>${escapeHtml(r.end_date)}</td>
        <td>${escapeHtml(r.reason) || "-"}</td>
        <td>${statusBadge(r.status)}</td>
      </tr>
    `).join("");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

function openApplyModal() {
  document.getElementById("apply-form").reset();
  hideAlert("modal-alert");
  document.getElementById("apply-modal").classList.remove("hidden");
}

function closeApplyModal() {
  document.getElementById("apply-modal").classList.add("hidden");
}

document.getElementById("apply-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("modal-alert");

  const payload = {
    leave_type: document.getElementById("leave-type").value,
    start_date: document.getElementById("leave-start").value,
    end_date: document.getElementById("leave-end").value,
    reason: document.getElementById("leave-reason").value.trim(),
  };

  const btn = document.getElementById("apply-btn");
  btn.disabled = true;
  btn.textContent = "Submitting...";

  try {
    await Api.post("/api/employee/leaves", payload);
    closeApplyModal();
    loadLeaves();
  } catch (err) {
    showAlert("modal-alert", err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Submit";
  }
});
