(async () => {
  const me = await requireAuth("Employee");
  if (!me) return;
  loadProfile();
})();

async function loadProfile() {
  hideAlert("page-alert");
  try {
    const p = await Api.get("/api/employee/profile");
    document.getElementById("p-name").value = p.name;
    document.getElementById("p-email").value = p.email;
    document.getElementById("p-department").value = p.department || "-";
    document.getElementById("p-designation").value = p.designation || "-";
    document.getElementById("p-phone").value = p.phone || "";
  } catch (err) {
    showAlert("page-alert", err.message);
  }
}

document.getElementById("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("page-alert"); hideAlert("page-success");
  try {
    await Api.put("/api/employee/profile", { phone: document.getElementById("p-phone").value.trim() });
    showAlert("page-success", "Profile updated.", "success");
  } catch (err) {
    showAlert("page-alert", err.message);
  }
});

document.getElementById("password-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert("pw-alert"); hideAlert("pw-success");
  const current_password = document.getElementById("current-password").value;
  const new_password = document.getElementById("new-password").value;
  try {
    await Api.put("/api/employee/change-password", { current_password, new_password });
    showAlert("pw-success", "Password changed successfully.", "success");
    document.getElementById("password-form").reset();
  } catch (err) {
    showAlert("pw-alert", err.message);
  }
});
