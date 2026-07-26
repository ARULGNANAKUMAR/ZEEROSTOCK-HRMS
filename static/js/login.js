document.getElementById("login-form").addEventListener("submit", async(e) => {
    e.preventDefault();
    hideAlert("login-alert");

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const btn = document.getElementById("login-btn");

    btn.disabled = true;
    btn.textContent = "Logging in...";

    try {
        const data = await Api.post("/api/auth/login", { email, password });
        window.location.href = data.user.role === "HR" ? "/hr/dashboard" : "/employee/dashboard";
    } catch (err) {
        showAlert("login-alert", err.message);
        btn.disabled = false;
        btn.textContent = "Log In";
    }
});

// If already logged in, skip straight to the right dashboard.
// Use plain fetch() instead of Api.get() to avoid the 401→redirect loop
// that Api.request() triggers on the login page.
(async() => {
    try {
        const res = await fetch("/api/auth/me", { credentials: "same-origin" });
        if (!res.ok) return; // Not logged in – stay on login page
        const me = await res.json();
        window.location.href = me.role === "HR" ? "/hr/dashboard" : "/employee/dashboard";
    } catch (e) {
        // Network error – stay on login page
    }
})();