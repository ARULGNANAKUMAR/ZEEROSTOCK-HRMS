(async () => {
  const me = await requireAuth("HR");
  if (!me) return;
  loadLeaves();
})();

function statusBadge(status) {
  const cls = status === "Approved" ? "badge-success" : status === "Rejected" ? "badge-danger" : "badge-warning";
  return `<span class="badge ${cls}">${escapeHtml(status)}</span>`;
}

async function loadLeaves() {
  hideAlert("page-alert");
  const status = document.getElementById("filter-status").value;
  const body = document.getElementById("leaves-body");
  body.innerHTML = '<tr><td colspan="7" class="empty-state">Loading...</td></tr>';

  try {
    const params = status ? `?status=${encodeURIComponent(status)}` : "";
    const rows = await Api.get(`/api/hr/leaves${params}`);

    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="7" class="empty-state">No leave requests found.</td></tr>';
      return;
    }

    body.innerHTML = rows.map(r => `
      <tr>
        <td>${escapeHtml(r.employee_name)}</td>
        <td>${escapeHtml(r.leave_type)}</td>
        <td>${escapeHtml(r.start_date)}</td>
        <td>${escapeHtml(r.end_date)}</td>
        <td>${escapeHtml(r.reason) || "-"}</td>
        <td>${statusBadge(r.status)}</td>
        <td>
          ${r.status === "Pending" ? `
            <button class="btn btn-success btn-sm" onclick="decide(${r.id}, 'Approved')">Approve</button>
            <button class="btn btn-danger btn-sm" onclick="decide(${r.id}, 'Rejected')">Reject</button>
          ` : ""}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

async function decide(id, status) {
  hideAlert("page-alert");
  try {
    await Api.put(`/api/hr/leaves/${id}`, { status });
    loadLeaves();
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}
