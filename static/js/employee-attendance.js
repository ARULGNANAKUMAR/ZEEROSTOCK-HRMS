(async () => {
  const me = await requireAuth("Employee");
  if (!me) return;
  loadAll();
})();

async function loadAll() {
  await loadHistory();
}

async function loadHistory() {
  hideAlert("page-alert");
  try {
    const rows = await Api.get("/api/employee/attendance");
    const todayStr = new Date().toISOString().slice(0, 10);
    const today = rows.find(r => r.date === todayStr);

    const summaryEl = document.getElementById("today-summary");
    const checkinBtn = document.getElementById("checkin-btn");
    const checkoutBtn = document.getElementById("checkout-btn");

    if (!today || !today.check_in) {
      summaryEl.textContent = "You haven't checked in today.";
      checkinBtn.disabled = false;
      checkoutBtn.disabled = true;
    } else if (today.check_in && !today.check_out) {
      summaryEl.textContent = `Checked in at ${today.check_in}. Don't forget to check out.`;
      checkinBtn.disabled = true;
      checkoutBtn.disabled = false;
    } else {
      summaryEl.textContent = `Checked in at ${today.check_in}, checked out at ${today.check_out}.`;
      checkinBtn.disabled = true;
      checkoutBtn.disabled = true;
    }

    const body = document.getElementById("history-body");
    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="4" class="empty-state">No attendance history yet.</td></tr>';
      return;
    }
    body.innerHTML = rows.map(r => `
      <tr>
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

async function checkIn() {
  hideAlert("page-alert"); hideAlert("page-success");
  try {
    await Api.post("/api/employee/attendance/checkin");
    showAlert("page-success", "Checked in successfully.", "success");
    loadHistory();
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

async function checkOut() {
  hideAlert("page-alert"); hideAlert("page-success");
  try {
    await Api.post("/api/employee/attendance/checkout");
    showAlert("page-success", "Checked out successfully.", "success");
    loadHistory();
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}
