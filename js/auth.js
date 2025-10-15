// ===============================
// MindMate Authentication & Requests
// ===============================

const API_URL = "http://127.0.0.1:8000"; // backend URL
window.API_URL = API_URL; // make it global

window.MindAuth = {
  // Save login info
  setUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
    localStorage.setItem("userLoggedIn", "true");
  },

  // Get current user
  getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },

  // Check if user is logged in
  isLoggedIn() {
    return localStorage.getItem("userLoggedIn") === "true" && this.getUser();
  },

  // Logout
  clearUser() {
    localStorage.removeItem("user");
    localStorage.removeItem("userLoggedIn");
    window.location.href = "login.html";
  },

  // Backend call for login
  async loginRequest(email, password) {
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {"Content-Type":"application/x-www-form-urlencoded"},
        body: new URLSearchParams({
          email: email,
          password: password
        })
      });

      const data = await res.json();
      if (res.ok) {
        this.setUser({ email, token: data.token });
      } else {
        // Handle different error response formats
        if (data && data.detail) {
          msg.textContent = data.detail;
        } else if (data && typeof data === 'object') {
          msg.textContent = "Invalid email or password";
        } else if (typeof data === 'string') {
          msg.textContent = data;
        } else {
          msg.textContent = "Login failed. Please check your credentials.";
        }
      }
      return { ok: res.ok, data };
    } catch (err) {
      console.error("Login error:", err);
      return { ok: false, data: { detail: "Server error" } };
    }
  },

  // Backend call for signup
  async signupRequest(email, password) {
    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: {"Content-Type":"application/x-www-form-urlencoded"},
        body: new URLSearchParams({
          email: email,
          password: password
        })
      });

      const data = await res.json();
      if (res.ok) {
        this.setUser({ email, token: data.token });
      } else {
        // Handle different error response formats
        if (data && data.detail) {
          msg.textContent = data.detail;
        } else if (data && typeof data === 'object') {
          msg.textContent = "Registration failed. Please try again.";
        } else if (typeof data === 'string') {
          msg.textContent = data;
        } else {
          msg.textContent = "Registration failed. Please check your information.";
        }
      }
      return { ok: res.ok, data };
    } catch (err) {
      console.error("Signup error:", err);
      return { ok: false, data: { detail: "Server error" } };
    }
  },

  // Submit feedback
  async submitFeedback(name, country, message, rating) {
    const user = this.getUser();
    if (!user) return { ok: false, data: { detail: "Please login first" } };

    try {
      const formData = new FormData();
      formData.append("name", name);
      formData.append("country", country);
      formData.append("message", message);
      formData.append("rating", rating);

      const res = await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: { "token": user.token },
        body: formData,
      });
      const data = await res.json();
      return { ok: res.ok, data };
    } catch (err) {
      console.error("Feedback error:", err);
      return { ok: false, data: { detail: "Server error" } };
    }
  },

  // Get feedbacks
  async getFeedbacks() {
    const user = this.getUser();
    if (!user) return [];

    try {
      const res = await fetch(`${API_URL}/feedback`, {
        headers: { "token": user.token },
      });
      const data = await res.json();
      return data;
    } catch (err) {
      console.error("Get feedback error:", err);
      return [];
    }
  },

  // Submit stress detection
  async submitStress(userInput) {
    const user = this.getUser();
    if (!user) return { ok: false, data: { detail: "Please login first" } };

    try {
      const res = await fetch(`${API_URL}/stress`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "token": user.token,
        },
        body: JSON.stringify(userInput),
      });
      const data = await res.json();
      return { ok: res.ok, data };
    } catch (err) {
      console.error("Stress detection error:", err);
      return { ok: false, data: { detail: "Server error" } };
    }
  },

  // Get stress history
  async getStressHistory(email) {
    const user = this.getUser();
    if (!user) return [];

    try {
      const res = await fetch(`${API_URL}/stress/history?user=${email}`, {
        headers: { "token": user.token },
      });
      const data = await res.json();
      return data;
    } catch (err) {
      console.error("Get stress history error:", err);
      return [];
    }
  },
};

// ===============================
// Restrict Navbar Links if not logged in
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const user = window.MindAuth.getUser();
  const protectedLinks = document.querySelectorAll("a[href$='.html']");

  protectedLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      if (!window.MindAuth.getUser()) {
        e.preventDefault();
        alert("Please login first to access this section.");
        window.location.href = "login.html";
      }
    });
  });
});
