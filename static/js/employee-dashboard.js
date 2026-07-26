(async () => {
  const me = await requireAuth("Employee");
  if (!me) return;

  try {
    const data = await Api.get("/api/employee/dashboard");

    const att = data.today_attendance;
    let statusText = "Not Checked In";
    if (att && att.check_in && att.check_out) statusText = "Completed";
    else if (att && att.check_in) statusText = "Checked In";
    document.getElementById("stat-today-status").textContent = statusText;

    document.getElementById("stat-approved").textContent = data.leave_summary.Approved || 0;
    document.getElementById("stat-pending").textContent = data.leave_summary.Pending || 0;

    const p = data.profile;
    document.getElementById("profile-info").innerHTML = p ? `
      <table>
        <tbody>
          <tr><td><strong>Name</strong></td><td>${escapeHtml(p.name)}</td></tr>
          <tr><td><strong>Email</strong></td><td>${escapeHtml(p.email)}</td></tr>
          <tr><td><strong>Phone</strong></td><td>${escapeHtml(p.phone) || "-"}</td></tr>
          <tr><td><strong>Department</strong></td><td>${escapeHtml(p.department) || "-"}</td></tr>
          <tr><td><strong>Designation</strong></td><td>${escapeHtml(p.designation) || "-"}</td></tr>
          <tr><td><strong>Date of Joining</strong></td><td>${escapeHtml(p.date_of_joining)}</td></tr>
        </tbody>
      </table>
    ` : '<p class="empty-state">Profile not found.</p>';

    const list = document.getElementById("notifications-list");
    if (!data.notifications.length) {
      list.innerHTML = '<li class="empty-state" style="list-style:none;">No new notifications.</li>';
    } else {
      list.innerHTML = data.notifications.map(n => `<li>${escapeHtml(n)}</li>`).join("");
    }
  } catch (err) {
    showAlert("page-alert", err.message);
  }
})();
