
import { useState } from "react";
import "./Login.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function Login({ onBack, onSignup }) {
  const [festival, setFestival] = useState("Utkarsh");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setMessage("");
    if (festival !== "Utkarsh") { setMessage(`${festival} is coming soon. Login is not available for this festival yet.`); return; }
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      const data = await response.json();
      
      if (!response.ok || data.success === false) {
        throw new Error(data.message || "Invalid email or password.");
      }

      // Support common response formats from the Flask backend.
      const user = data.user || data;
      const role = String(
        user.role || data.role || ""
      ).toUpperCase();

      const token = data.access_token || data.token;

      if (!token) {
        throw new Error(
          "Login succeeded, but the backend did not return an authentication token."
        );
      }

      if (!role) {
        throw new Error(
          "Your backend login response does not include the user's role. Please check auth_service.py."
        );
      }

      // Do not let a pending organizer access the organizer dashboard.
      if (role === "ORGANIZER") {
        const status = String(
          user.organizer_status || data.organizer_status || ""
        ).toUpperCase();

        if (status && status !== "APPROVED") {
          setMessage(
            status === "REJECTED"
              ? "Your organizer application was rejected. Please contact the Festify admin."
              : "Your organizer account is awaiting admin approval."
          );
          return;
        }
      }

      sessionStorage.setItem("festify_token", token);
      sessionStorage.setItem("festify_user", JSON.stringify(user));
      sessionStorage.setItem("festify_role", role);
      if (["PARTICIPANT", "STUDENT"].includes(role)) {
        window.location.href = "/student-dashboard";
      } else if (role === "ORGANIZER") {
        window.location.href = "/organizer-dashboard";
      } else if (["ADMIN", "SUPER_ADMIN"].includes(role)) {
        window.location.href = "/admin-dashboard";
      } else {
        sessionStorage.removeItem("festify_token");
        sessionStorage.removeItem("festify_user");
        sessionStorage.removeItem("festify_role");
        throw new Error("This account has an unrecognized role.");
      }
    } catch (error) {
      setMessage(
        error.message ||
          "Unable to connect to Festify. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-decoration login-decoration-one" />
      <div className="login-decoration login-decoration-two" />

      <header className="login-header">
        <button className="login-brand"  onClick={onBack}>
          <span className="brand-mark">F</span>
          FESTIFY
        </button>

        <span className="login-header-caption">
          ONE CAMPUS. ENDLESS POSSIBILITIES.
        </span>
      </header>

      <main className="login-main">
        <section className="login-visual">
          <span className="login-kicker">
            <span className="login-live-dot" />
            YOUR NEXT CHAPTER STARTS HERE
          </span>

          <h1>
            Your people.
            <br />
            Your passion.
            <br />
            <span>Your moment.</span>
          </h1>

          <p>
            Step into a world of campus events, incredible ideas,
            unforgettable experiences, and opportunities to belong.
          </p>

          <div className="login-visual-tags">
            <span>✦ CULTURE</span>
            <span>⌘ TECHNOLOGY</span>
            <span>✺ COMMUNITY</span>
          </div>

          <div className="login-visual-bottom">
            <span>MAKE MEMORIES. MAKE HISTORY.</span>
            <span>FESTIFY · CAMPUS EXPERIENCES</span>
          </div>
        </section>

        <section className="login-card">
          <div className="login-card-icon">✦</div>

          <p className="login-card-eyebrow">WELCOME BACK</p>
          <h2>Let's get you in</h2>
          <p className="login-card-description">
            Sign in to continue your Festify journey
          </p>

          <form onSubmit={handleLogin}>
            <label htmlFor="login-festival">Choose fest</label>
            <select id="login-festival" className="festival-choice" value={festival} onChange={(e) => { setFestival(e.target.value); setMessage(""); }}>
              <option value="Utkarsh">Utkarsh</option>
              <option value="Dandiya">Dandiya</option>
              <option value="Tech Fest">Tech Fest</option>
            </select>
            {festival !== "Utkarsh" && <p className="festival-coming-soon" role="status">{festival} is coming soon. Login will be enabled when registration opens.</p>}
            <label htmlFor="login-email">Email address</label>
            <input
              id="login-email"
              type="email"
              placeholder="you@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />

            <div className="login-password-heading">
              <label htmlFor="login-password">Password</label>
            </div>

            <div className="login-password-wrap">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />

              <button
                type="button"
                className="login-show-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? "HIDE" : "SHOW"}
              </button>
            </div>

            {message && (
              <div className="login-message" role="alert">
                {message}
              </div>
            )}

            <button
              type="submit"
              className="login-submit"
              disabled={loading || festival !== "Utkarsh"}
            >
              {loading ? "SIGNING YOU IN..." : "SIGN IN"}
              <span>↗</span>
            </button>
          </form>

          <div className="login-card-divider">
            <span />
            <i>✦</i>
            <span />
          </div>

          <p className="login-signup-prompt">
            New to Festify?{" "}
            <button type="button" onClick={onSignup}>
              Create an account
            </button>
          </p>

          <button className="login-back-link" onClick={onBack}>
            ← Back to Festify
          </button>

          <p className="login-security-note">
            ONE LOGIN · THREE ROLES · ONE FESTIVAL
          </p>
        </section>
      </main>

      <footer className="login-footer">
        <span>© {new Date().getFullYear()} FESTIFY</span>
        <span>BUILT FOR THE NEXT GENERATION ✦</span>
      </footer>
    </div>
  );
}

export default Login;
