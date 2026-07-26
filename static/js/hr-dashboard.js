(async () => {
  const me = await requireAuth("HR");
  if (!me) return;

  try {
    const data = await Api.get("/api/hr/dashboard");
    document.getElementById("stat-total").textContent = data.total_employees;
    document.getElementById("stat-present").textContent = data.present_today;
    document.getElementById("stat-leave").textContent = data.on_leave_today;

    const body = document.getElementById("recent-activity-body");
    if (!data.recent_activity.length) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state">No attendance activity yet.</td></tr>';
    } else {
      body.innerHTML = data.recent_activity.map(r => `
        <tr>
          <td>${escapeHtml(r.name)}</td>
          <td>${escapeHtml(r.date)}</td>
          <td>${escapeHtml(r.check_in) || "-"}</td>
          <td>${escapeHtml(r.check_out) || "-"}</td>
          <td><span class="badge badge-success">${escapeHtml(r.status)}</span></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    showAlert("dash-alert", err.message);
  }
})();
