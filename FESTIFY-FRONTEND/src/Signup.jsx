
import { useState } from "react";
import "./Signup.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

export default function Signup({ onLogin, onBack }) {
  const [festival, setFestival] = useState("Utkarsh");
  const [form, setForm] = useState({
    fullName: "",
    collegeName: "",
    email: "",
    password: "",
    branch: "",
    studyYear: "",
    dob: "",
    gender: "",
    enrollmentNumber: "",
    contactNumber: "",
  });

  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const updateField = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({ ...previous, [name]: value }));

    if (name === "email" && value.trim().toLowerCase() !== form.email.trim().toLowerCase()) {
      setEmailVerified(false);
      setOtpSent(false);
      setOtp("");
      setNotice("");
    }

    setError("");
  };

  const requestJson = async (path, payload) => {
    let response;

    try {
      response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch {
      throw new Error(
        "Cannot connect to the backend. Make sure your Flask server is running."
      );
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.success === false) {
      throw new Error(
        data.message || data.error || `Request failed (${response.status}).`
      );
    }

    return data;
  };

  const sendOtp = async () => {
    const email = form.email.trim().toLowerCase();

    if (!email) {
      setError("Please enter your email address first.");
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setSendingOtp(true);
    setError("");
    setNotice("");
    setEmailVerified(false);
    setOtpSent(false);
    setOtp("");

    try {
      const data = await requestJson("/api/auth/send-email-otp", { email });
      setOtpSent(true);
      setNotice(data.message || "OTP sent. Check your email inbox and spam folder.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSendingOtp(false);
    }
  };

  const verifyOtp = async () => {
    const email = form.email.trim().toLowerCase();

    if (!otpSent) {
      setError("Please click Send OTP first.");
      return;
    }

    if (!/^\d{6}$/.test(otp.trim())) {
      setError("Enter the complete 6-digit OTP from your email.");
      return;
    }

    setVerifyingOtp(true);
    setError("");
    setNotice("");

    try {
      const data = await requestJson("/api/auth/verify-email-otp", {
        email,
        otp: otp.trim(),
      });

      setEmailVerified(true);
      setNotice(data.message || "Email verified successfully!");
    } catch (err) {
      setEmailVerified(false);
      setError(err.message);
    } finally {
      setVerifyingOtp(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (festival !== "Utkarsh") { setError(`${festival} is coming soon. Signup is not available for this festival yet.`); return; }
    setNotice("");

    if (!emailVerified) {
      setError("Please verify your email using the OTP before signing up.");
      return;
    }

    setSubmitting(true);

    try {
      const data = await requestJson("/api/auth/register", {
        name: form.fullName.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone: form.contactNumber.trim(),
        college_id_number: form.enrollmentNumber.trim(),
        college_name: form.collegeName.trim(),
        branch: form.branch,
        year_of_study: Number(form.studyYear),
        date_of_birth: form.dob,
        gender: form.gender,
        role: "PARTICIPANT",
      });

      setNotice(data.message || "Your account has been created successfully.");

      if (onLogin) {
        onLogin();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-decoration signup-decoration-one" />
      <div className="signup-decoration signup-decoration-two" />
      <div className="signup-decoration signup-decoration-three" />

      <header className="signup-header">
        <button type="button" className="signup-brand" onClick={onBack}>
          <span className="brand-mark">F</span>
          <span>Festify</span>
        </button>

        <button type="button" className="signup-back" onClick={onBack}>
          ← Back to home
        </button>
      </header>

      <main className="signup-main">
        <section className="signup-intro">
          <span className="signup-eyebrow">YOUR CAMPUS. YOUR STAGE.</span>
          <h1>
            Make your
            <br />
            campus life <span>unforgettable</span>
          </h1>

          <p className="signup-intro-description">
            Discover college festivals, explore events, and make memories
            with people who share your vibe.
          </p>

          <div className="signup-perks">
            <div className="signup-perk">
              <span className="signup-perk-icon perk-pink">✦</span>
              <div>
                <strong>Discover events</strong>
                <p>Find exciting events happening around you.</p>
              </div>
            </div>

            <div className="signup-perk">
              <span className="signup-perk-icon perk-teal">♫</span>
              <div>
                <strong>Show your talent</strong>
                <p>Explore competitions, performances, and more.</p>
              </div>
            </div>

            <div className="signup-perk">
              <span className="signup-perk-icon perk-yellow">♡</span>
              <div>
                <strong>Make connections</strong>
                <p>Meet people and create unforgettable memories.</p>
              </div>
            </div>
          </div>

          <div className="signup-art" aria-hidden="true">
            <span className="signup-art-star star-one">✦</span>
            <span className="signup-art-star star-two">✧</span>
            <span className="signup-art-circle">F</span>
            <span className="signup-art-note">YOUR NEXT BIG MOMENT STARTS HERE</span>
          </div>
        </section>

        <section className="signup-card">
          <div className="signup-card-heading">
            <span className="signup-card-tag">STUDENT REGISTRATION</span>
            <h2>Create your account</h2>
            <p>Join the Festify community in just a few steps.</p>
          </div>

          <form onSubmit={handleSubmit} className="signup-form">
            <div className="signup-field signup-field-full">
              <label htmlFor="signup-festival">Choose fest</label>
              <select id="signup-festival" className="festival-choice" value={festival} onChange={(e) => { setFestival(e.target.value); setError(""); setNotice(""); }}>
                <option value="Utkarsh">Utkarsh</option>
                <option value="Dandiya">Dandiya</option>
                <option value="Tech Fest">Tech Fest</option>
              </select>
              {festival !== "Utkarsh" && <p className="festival-coming-soon" role="status">{festival} is coming soon. Signup will be enabled when registration opens.</p>}
            </div>
            <div className="signup-form-grid">
              <div className="signup-field signup-field-full">
                <label htmlFor="fullName">Full name</label>
                <input
                  id="fullName"
                  name="fullName"
                  value={form.fullName}
                  onChange={updateField}
                  placeholder="Enter your full name"
                  autoComplete="name"
                  required
                />
              </div>

              <div className="signup-field signup-field-full">
                <label htmlFor="collegeName">College name</label>
                <input
                  id="collegeName"
                  name="collegeName"
                  value={form.collegeName}
                  onChange={updateField}
                  placeholder="Enter your college name"
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="branch">Branch</label>
                <input
                  id="branch"
                  name="branch"
                  value={form.branch}
                  onChange={updateField}
                  placeholder="e.g. Information Technology"
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="studyYear">Year of study</label>
                <select
                  id="studyYear"
                  name="studyYear"
                  value={form.studyYear}
                  onChange={updateField}
                  required
                >
                  <option value="">Select year</option>
                  <option value="1">1st year</option>
                  <option value="2">2nd year</option>
                  <option value="3">3rd year</option>
                  <option value="4">4th year</option>
                  <option value="5">5th year</option>
                </select>
              </div>

              <div className="signup-field signup-field-full">
                <label htmlFor="email">Email address</label>
                <div className="signup-otp-row">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={updateField}
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                  />
                  <button
                    type="button"
                    className="signup-otp-button"
                    onClick={sendOtp}
                    disabled={sendingOtp || emailVerified || festival !== "Utkarsh"}
                  >
                    {sendingOtp ? "Sending..." : emailVerified ? "Verified ✓" : otpSent ? "Resend OTP" : "Send OTP"}
                  </button>
                </div>
              </div>

              
                <div className="signup-field signup-field-full signup-otp-entry">
                  <label htmlFor="otp">Enter email OTP</label>
                  <div className="signup-otp-row">
                    <input
                      id="otp"
                      name="otp"
                      type="text"
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      value={otp}
                      onChange={(event) => {
                        setOtp(event.target.value.replace(/\D/g, "").slice(0, 6));
                        setError("");
                      }}
                      placeholder="Enter your 6-digit OTP"
                      aria-label="Enter the six-digit email OTP"
                      required
                    />
                    <button
                      type="button"
                      className="signup-otp-button signup-verify-button"
                      onClick={verifyOtp}
                      disabled={verifyingOtp || otp.length !== 6 || festival !== "Utkarsh"}
                    >
                      {verifyingOtp ? "Verifying..." : "Verify OTP"}
                    </button>
                  </div>
                  <span className="signup-otp-hint">
                    Check your inbox and spam folder for the email.
                  </span>
                </div>
              

              {emailVerified && (
                <div className="signup-field-full signup-verified-note">
                  <span>✓</span> Email address verified successfully.
                </div>
              )}

              <div className="signup-field signup-field-full">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={updateField}
                  placeholder="Create a strong password"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="contactNumber">Phone number</label>
                <input
                  id="contactNumber"
                  name="contactNumber"
                  type="tel"
                  value={form.contactNumber}
                  onChange={updateField}
                  placeholder="Enter phone number"
                  autoComplete="tel"
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="enrollmentNumber">Enrollment number</label>
                <input
                  id="enrollmentNumber"
                  name="enrollmentNumber"
                  value={form.enrollmentNumber}
                  onChange={updateField}
                  placeholder="College ID / enrollment no."
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="dob">Date of birth</label>
                <input
                  id="dob"
                  name="dob"
                  type="date"
                  value={form.dob}
                  onChange={updateField}
                  max={new Date().toISOString().split("T")[0]}
                  required
                />
              </div>

              <div className="signup-field">
                <label htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  name="gender"
                  value={form.gender}
                  onChange={updateField}
                  required
                >
                  <option value="">Select gender</option>
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="signup-error" role="alert">
                <span>!</span> {error}
              </div>
            )}

            {notice && (
              <div
                className={`signup-notice ${emailVerified ? "signup-notice-success" : ""}`}
                role="status"
              >
                {notice}
              </div>
            )}

            <button
              type="submit"
              className="signup-submit"
              disabled={submitting || !emailVerified || festival !== "Utkarsh"}
            >
              {submitting ? "Creating account..." : "Create Student Account"}
              {!submitting && <span>→</span>}
            </button>

            {!emailVerified && (
              <p className="signup-verification-reminder">
                Verify your email with the OTP before creating your account.
              </p>
            )}
          </form>

          <div className="signup-login-prompt">
            Already have an account?{" "}
            <button type="button" onClick={onLogin}>
              Log in
            </button>
          </div>
        </section>
      </main>

      <footer className="signup-footer">
        Made for campus memories <span>✦</span> Made with Festify
      </footer>
    </div>
  );
}
