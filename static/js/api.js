/**
 * api.js
 * Small fetch() wrapper shared by every page. Talks to the Flask JSON API
 * using the session cookie for authentication (credentials: 'same-origin').
 */

const Api = {
  async request(path, options = {}) {
    const opts = {
      method: options.method || "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
    };
    if (options.body !== undefined) {
      opts.body = JSON.stringify(options.body);
    }

    const res = await fetch(path, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }

    if (res.status === 401) {
      window.location.href = "/login";
      throw new Error("Not authenticated");
    }

    if (!res.ok) {
      const message = (data && data.error) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return data;
  },

  get(path) { return this.request(path); },
  post(path, body) { return this.request(path, { method: "POST", body }); },
  put(path, body) { return this.request(path, { method: "PUT", body }); },
};

async function requireAuth(expectedRole) {
  try {
    const me = await Api.get("/api/auth/me");
    if (expectedRole && me.role !== expectedRole) {
      window.location.href = me.role === "HR" ? "/hr/dashboard" : "/employee/dashboard";
      return null;
    }
    const emailEl = document.getElementById("current-user-email");
    if (emailEl) emailEl.textContent = me.email;
    return me;
  } catch (e) {
    window.location.href = "/login";
    return null;
  }
}

async function doLogout() {
  await Api.post("/api/auth/logout");
  window.location.href = "/login";
}

function showAlert(containerId, message, type = "error") {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = message;
  el.classList.remove("hidden");
}

function hideAlert(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.classList.add("hidden");
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
