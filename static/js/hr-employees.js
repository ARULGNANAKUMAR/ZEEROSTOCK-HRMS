let isEditMode = false;

(async () => {
  const me = await requireAuth("HR");
  if (!me) return;
  loadEmployees();
})();

document.getElementById("search-input").addEventListener("keyup", (e) => {
  if (e.key === "Enter") loadEmployees();
});

async function loadEmployees() {
  hideAlert("page-alert");
  const q = document.getElementById("search-input").value.trim();
  const body = document.getElementById("employees-body");
  body.innerHTML = '<tr><td colspan="7" class="empty-state">Loading...</td></tr>';

  try {
    const params = q ? `?q=${encodeURIComponent(q)}` : "";
    const rows = await Api.get(`/api/hr/employees${params}`);

    if (!rows.length) {
      body.innerHTML = '<tr><td colspan="7" class="empty-state">No employees found.</td></tr>';
      return;
    }

    body.innerHTML = rows.map(r => `
      <tr>
        <td>${escapeHtml(r.name)}</td>
        <td>${escapeHtml(r.login_email)}</td>
        <td>${escapeHtml(r.phone) || "-"}</td>
        <td>${escapeHtml(r.department) || "-"}</td>
        <td>${escapeHtml(r.designation) || "-"}</td>
        <td>${escapeHtml(r.date_of_joining)}</td>
        <td><button class="btn btn-secondary btn-sm" onclick="openEditModal(${r.id})">Edit</button></td>
      </tr>
    `).join("");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

function openAddModal() {
  isEditMode = false;
  document.getElementById("modal-title").textContent = "Add Employee";
  document.getElementById("employee-form").reset();
  document.getElementById("emp-id").value = "";
  document.getElementById("password-group").classList.remove("hidden");
  hideAlert("modal-alert");
  document.getElementById("employee-modal").classList.remove("hidden");
}

async function openEditModal(id) {
  isEditMode = true;
  hideAlert("modal-alert");
  try {
    const emp = await Api.get(`/api/hr/employees/${id}`);
    document.getElementById("modal-title").textContent = "Edit Employee";
    document.getElementById("emp-id").value = emp.id;
    document.getElementById("emp-name").value = emp.name;
    document.getElementById("emp-email").value = emp.login_email;
    document.getElementById("emp-phone").value = emp.phone || "";
    document.getElementById("emp-doj").value = emp.date_of_joining;
    document.getElementById("emp-department").value = emp.department || "";
    document.getElementById("emp-designation").value = emp.designation || "";
    document.getElementById("password-group").classList.add("hidden");
    document.getElementById("employee-modal").classList.remove("hidden");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

function closeModal() {
  document.getElementById("employee-modal").classList.add("hidden");
}

document.getElementById("employee-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("modal-alert");

  const payload = {
    name: document.getElementById("emp-name").value.trim(),
    email: document.getElementById("emp-email").value.trim(),
    phone: document.getElementById("emp-phone").value.trim(),
    date_of_joining: document.getElementById("emp-doj").value,
    department: document.getElementById("emp-department").value.trim(),
    designation: document.getElementById("emp-designation").value.trim(),
  };

  const saveBtn = document.getElementById("save-btn");
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";

  try {
    if (isEditMode) {
      const id = document.getElementById("emp-id").value;
      await Api.put(`/api/hr/employees/${id}`, payload);
    } else {
      const pw = document.getElementById("emp-password").value.trim();
      if (pw) payload.password = pw;
      await Api.post("/api/hr/employees", payload);
    }
    closeModal();
    loadEmployees();
  } catch (err) {
    showAlert("modal-alert", err.message);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save";
  }
});
