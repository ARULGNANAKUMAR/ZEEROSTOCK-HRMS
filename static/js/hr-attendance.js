(async () => {
  const me = await requireAuth("HR");
  if (!me) return;
  loadAttendance();
})();

function clearFilters() {
  document.getElementById("filter-employee").value = "";
  document.getElementById("filter-date").value = "";
  loadAttendance();
}

async function loadAttendance() {
  hideAlert("page-alert");
  const empId = document.getElementById("filter-employee").value;
  const dateVal = document.getElementById("filter-date").value;
  const body = document.getElementById("attendance-body");
  body.innerHTML = '<tr><td colspan="5" class="empty-state">Loading...</td></tr>';

  const params = new URLSearchParams();
  if (empId) params.set("employee_id", empId);
  if (dateVal) params.set("date", dateVal);

  try {
    const data = await Api.get(`/api/hr/attendance?${params.toString()}`);

    const select = document.getElementById("filter-employee");
    if (select.options.length <= 1) {
      data.employees.forEach(emp => {
        const opt = document.createElement("option");
        opt.value = emp.id;
        opt.textContent = emp.name;
        select.appendChild(opt);
      });
      select.value = empId || "";
    }

    if (!data.records.length) {
      body.innerHTML = '<tr><td colspan="5" class="empty-state">No attendance records found.</td></tr>';
      return;
    }

    body.innerHTML = data.records.map(r => `
      <tr>
        <td>${escapeHtml(r.employee_name)}</td>
        <td>${escapeHtml(r.date)}</td>
        <td>${escapeHtml(r.check_in) || "-"}</td>
        <td>${escapeHtml(r.check_out) || "-"}</td>
        <td><span class="badge badge-success">${escapeHtml(r.status)}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}
