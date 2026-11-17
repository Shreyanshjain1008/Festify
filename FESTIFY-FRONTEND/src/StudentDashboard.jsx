
import { useEffect, useMemo, useRef, useState } from "react";
import "./StudentDashboard.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const DEFAULT_FESTIFY_FAQS = [
  { faq_id: "default-1", category: "Registration", question: "How do I register for an event?", answer: "Open Discover, find the event, and select Register. If registration is open and you meet the eligibility rules, it will appear under My Events.", keywords: "register,registration,event" },
  { faq_id: "default-2", category: "Registration", question: "Where can I see my registered events?", answer: "Open My Events in your student dashboard to see your confirmed event registrations.", keywords: "my events,registered" },
  { faq_id: "default-3", category: "Day Pass", question: "How do I get my festival day pass?", answer: "Open the Day Pass section, choose Day-1, Day-2 or Day-3, then select Register & Get QR Pass.", keywords: "day pass,qr,pass" },
  { faq_id: "default-4", category: "Day Pass", question: "Where can I find my QR pass?", answer: "Your active QR pass appears in the Day Pass section after successful registration.", keywords: "qr,pass,find" },
  { faq_id: "default-5", category: "Registration", question: "Can I register after the deadline?", answer: "No. Registration closes at the deadline set by the organizer. Contact the organizer if you need help.", keywords: "deadline,late,closed" },
  { faq_id: "default-6", category: "Organizer", question: "How do I become an organizer?", answer: "Choose Become an Organizer from your dashboard and submit your society details. The admin team must approve your application.", keywords: "organizer,society,apply" },
  { faq_id: "default-7", category: "Events", question: "Where can I see event venue and timing?", answer: "Open the event details from Discover to see its venue, date and timing.", keywords: "venue,location,time,date" },
  { faq_id: "default-8", category: "Help", question: "What should I do if my QR pass is not showing?", answer: "Refresh your dashboard and check your day-pass registration. If it is still missing, contact the Festify help desk.", keywords: "qr missing,pass not showing,problem" },
];

const CATEGORIES = [
  "All Events",
  "Technical",
  "Cultural",
  "Music",
  "Dance",
  "Gaming",
  "Sports",
  "Literary",
];

function StudentDashboard() {
  const [user, setUser] = useState(() =>
    JSON.parse(sessionStorage.getItem("festify_user") || "{}")
  );

  const [events, setEvents] = useState([]);
  const [reactions, setReactions] = useState({});
  const profileRef = useRef(null);
  const [registrations, setRegistrations] = useState([]);
  const [activeCategory, setActiveCategory] = useState("All Events");
  const [activeDay, setActiveDay] = useState("All Days");
  const [activeSociety, setActiveSociety] = useState("All Societies");
  const [search, setSearch] = useState("");
  const [activePage, setActivePage] = useState("Explore Events");
  const [profileOpen, setProfileOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [registeringId, setRegisteringId] = useState(null);
  const [selectedPassDay, setSelectedPassDay] = useState("Day-1");
  const [dayPasses, setDayPasses] = useState([]);
  const [newlyIssuedDayPass, setNewlyIssuedDayPass] = useState(null);
  const [dayPassLoading, setDayPassLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const deadlineAlertRef = useRef(null);
const shouldScrollToDeadlineAlert = useRef(false);

useEffect(() => {
  if (!shouldScrollToDeadlineAlert.current) return;

  // Wait until React has rendered the red alert.
  const frameId = requestAnimationFrame(() => {
    if (deadlineAlertRef.current) {
      deadlineAlertRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      shouldScrollToDeadlineAlert.current = false;
    }
  });

  return () => cancelAnimationFrame(frameId);
}, [notice]);
  const [societyCode, setSocietyCode] = useState("");
  const [organizerSubmitting, setOrganizerSubmitting] = useState(false);
  const [organizerNotice, setOrganizerNotice] = useState({ type: "", message: "" });
  const [feedbackEventId, setFeedbackEventId] = useState("");
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackNotice, setFeedbackNotice] = useState({ type: "", message: "" });
  const [myFeedback, setMyFeedback] = useState([]);
  const [faqs, setFaqs] = useState([]);
  const [faqLoadMessage, setFaqLoadMessage] = useState("");
  const [selectedFaqId, setSelectedFaqId] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const token = sessionStorage.getItem("festify_token");

  useEffect(() => {
    function closeProfileOutside(event) {
      if (profileRef.current && !profileRef.current.contains(event.target)) setProfileOpen(false);
    }
    function closeProfileOnEscape(event) { if (event.key === "Escape") setProfileOpen(false); }
    document.addEventListener("pointerdown", closeProfileOutside);
    document.addEventListener("keydown", closeProfileOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeProfileOutside);
      document.removeEventListener("keydown", closeProfileOnEscape);
    };
  }, []);

  useEffect(() => {
    if (!token) {
      window.location.href = "/";
      return;
    }

    let cancelled = false;

    // Fetch the complete student record from the database-backed API.
    // Login intentionally stores only a small user object in sessionStorage.
    async function loadUserProfile() {
      try {
        const storedUser = JSON.parse(sessionStorage.getItem("festify_user") || "{}");
        const userId = storedUser.user_id;

        if (!userId) {
          throw new Error("Your user ID is missing. Please log out and log in again.");
        }

        const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.success || !result.user) {
          throw new Error(result.message || `Unable to load profile (${response.status}).`);
        }

        if (!cancelled) {
          // Keep the full API record in state and refresh the dashboard so other
          // dashboard sections can use the same up-to-date details.
          setUser((previous) => ({ ...previous, ...result.user }));
          sessionStorage.setItem(
            "festify_user",
            JSON.stringify({ ...storedUser, ...result.user })
          );
        }
      } catch (err) {
        console.error("Failed to load student profile:", err.message);
      }
    }

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_BASE_URL}/api/events/published`);

        if (!response.ok) {
          throw new Error(
            response.status === 404
              ? "The events API route has not been connected yet."
              : `Unable to load events (${response.status}).`
          );
        }

        const result = await response.json();
        const eventList = Array.isArray(result)
          ? result
          : result.events || result.data || [];

        if (!cancelled) {
          setEvents(eventList);
          const ids = eventList.map(getEventId).filter((id) => id != null);
          if (ids.length && token) {
            fetch(`${API_BASE_URL}/api/feedback/reactions?event_ids=${ids.join(",")}`, { headers: { Authorization: `Bearer ${token}` } })
              .then((r) => r.json()).then((data) => { if (!cancelled && data.reactions) setReactions(data.reactions); })
              .catch((err) => console.error("Unable to load event reactions", err));
          }
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Unable to load events.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }


    async function loadRegistrations() {
      try {
        if (!user.user_id) {
          console.error("Student user_id is missing from festify_user.");
          return;
        }

        const response = await fetch(
          `${API_BASE_URL}/api/registrations/users/${user.user_id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const result = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            result.message || `Unable to load registrations (${response.status}).`
          );
        }

        const list = Array.isArray(result)
          ? result
          : result.registrations || result.data || [];

        setRegistrations(list);
      } catch (err) {
        console.error("Failed to load registrations:", err.message);
      }
    }


    async function loadDayPasses() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/day-passes/me`, { headers: { Authorization: `Bearer ${token}` } });
        const result = await response.json().catch(() => ({}));
        if (response.ok) setDayPasses(result.day_passes || []);
      } catch (err) { console.error("Failed to load day passes:", err.message); }
    }

    async function loadStudentExtras() {
      // Load FAQs and feedback independently: a failure in one must not prevent
      // the other section from rendering. The FAQ picker always gets usable rows.
      try {
        const faqResponse = await fetch(`${API_BASE_URL}/api/faq/`, {
          headers: { Accept: "application/json" },
          cache: "no-store",
        });
        const faqData = await faqResponse.json().catch(() => ({}));
        const faqRows = Array.isArray(faqData)
          ? faqData
          : Array.isArray(faqData.faqs)
            ? faqData.faqs
            : Array.isArray(faqData.data)
              ? faqData.data
              : [];
        if (!faqResponse.ok) {
          console.error("FAQ API error:", faqResponse.status, faqData);
        }
        if (!cancelled) {
          const usableFaqs = faqRows.length ? faqRows : DEFAULT_FESTIFY_FAQS;
          setFaqs(usableFaqs);
          setFaqLoadMessage(faqRows.length
            ? ""
            : "Showing built-in questions because the FAQ API returned no database records.");
        }
      } catch (err) {
        console.error("Unable to load database FAQs; showing built-in questions.", err);
        if (!cancelled) {
          setFaqs(DEFAULT_FESTIFY_FAQS);
          setFaqLoadMessage("Showing built-in questions while the FAQ API is unavailable.");
        }
      }

      try {
        const feedbackResponse = await fetch(`${API_BASE_URL}/api/feedback/mine`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const feedbackData = await feedbackResponse.json().catch(() => ({}));
        if (!cancelled && feedbackResponse.ok) {
          setMyFeedback(Array.isArray(feedbackData.feedback) ? feedbackData.feedback : []);
        }
      } catch (err) {
        console.error("Unable to load submitted feedback", err);
      }
    }

    loadDashboard();
    loadRegistrations();
    loadUserProfile();
    loadDayPasses();
    loadStudentExtras();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const societies = useMemo(() => {
    const names = events
      .map((event) => getSociety(event))
      .filter(Boolean);

    return ["All Societies", ...new Set(names)];
  }, [events]);

  const days = useMemo(() => {
    const names = events
      .map((event) => getDay(event))
      .filter(Boolean);

    return ["All Days", ...new Set(names)];
  }, [events]);

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const category = getCategory(event);
      const society = getSociety(event);
      const day = getDay(event);
      const title = getTitle(event);

      const matchesCategory =
        activeCategory === "All Events" ||
        category.toLowerCase() === activeCategory.toLowerCase();

      const matchesDay =
        activeDay === "All Days" || day === activeDay;

      const matchesSociety =
        activeSociety === "All Societies" ||
        society === activeSociety;

      const matchesSearch =
        `${title} ${society} ${category}`
          .toLowerCase()
          .includes(search.toLowerCase());

      return (
        matchesCategory &&
        matchesDay &&
        matchesSociety &&
        matchesSearch
      );
    });
  }, [events, activeCategory, activeDay, activeSociety, search]);

  const registrationKey = (eventId, day) => `${String(eventId)}::${day}`;
  const registeredIds = new Set(
    registrations.filter((item) => item.registration_status !== "CANCELLED").map((item) =>
      registrationKey(item.event_id ?? item.event?.event_id ?? item.event?.id ?? item.eventId, item.event_day || "Day-1")
    )
  );

  async function reactToEvent(event, reaction) {
    const eventId = getEventId(event);
    if (!eventId) return;
    const current = reactions[String(eventId)] || { likes: 0, dislikes: 0, my_reaction: null };
    const next = current.my_reaction === reaction ? null : reaction;
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback/reactions/${eventId}`, {
        method: next ? "PUT" : "DELETE",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        ...(next ? { body: JSON.stringify({ reaction: next }) } : {}),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.message || "Could not save your reaction");
      const likes = current.likes - (current.my_reaction === "like" ? 1 : 0) + (next === "like" ? 1 : 0);
      const dislikes = current.dislikes - (current.my_reaction === "dislike" ? 1 : 0) + (next === "dislike" ? 1 : 0);
      setReactions((previous) => ({ ...previous, [String(eventId)]: { likes, dislikes, my_reaction: next } }));
    } catch (err) { setNotice(err.message || "Unable to save reaction."); }
  }

  async function registerForEvent(event, eventDay = "Day-1") {
    const eventId = getEventId(event);

    if (eventId == null) {
      setNotice("This event does not have an event ID yet.");
      return;
    }

    const eventDayForRegistration = getDay(event) || eventDay || "Day-1";
    if (registeredIds.has(registrationKey(eventId, eventDayForRegistration))) {
      setNotice(`You are already registered for this event on ${eventDayForRegistration}.`);
      return;
    }

    setRegisteringId(registrationKey(eventId, eventDay));
    setNotice("");

    try {

      const response = await fetch(
        `${API_BASE_URL}/api/registrations/events/${eventId}/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            custom_field_values: {},
            event_day: eventDayForRegistration,
          }),
        }
      );


      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(result.message || result.error || "Registration failed.");
      }

      setRegistrations((previous) => [
        ...previous,
        { ...(result.registration || { event_id: eventId, event }), event, event_day: eventDayForRegistration },
      ]);

      const alreadyHasPass = dayPasses.some((pass) => pass.festival_day === eventDayForRegistration && pass.status !== "CANCELLED");
      setNotice(`${result.message || `You're registered for ${getTitle(event)}!`}${alreadyHasPass ? "" : ` Also register for ${eventDayForRegistration} and get the QR pass for entry to campus.`}`);
    
} catch (err) {
  const errorMessage =
    err.message || "Registration failed. Please try again.";

  const isDeadlineError =
    /deadline|registration closed|registration is closed|registration has ended|last date.*passed/i.test(
      errorMessage
    );

  if (isDeadlineError) {
    // Hide the regular notice so only the red alert is displayed.
    shouldScrollToDeadlineAlert.current = true;
    setNotice(errorMessage);
  } else {
    setNotice(
      `${errorMessage} Please check that the registration API is configured.`
    );
  }
} finally {

      setRegisteringId(null);
    }
  }

  async function registerForFestivalDay() {
    const existing = dayPasses.find((pass) => pass.festival_day === selectedPassDay && pass.status !== "CANCELLED");
    if (existing) {
      setNotice(`Your ${selectedPassDay} campus QR pass has already been issued. Please check your registered email.`);
      return;
    }
    setDayPassLoading(true);
    setNotice("");
    try {
      const response = await fetch(`${API_BASE_URL}/api/day-passes/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ festival_day: selectedPassDay }),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.message || "Unable to register for this festival day.");
      if (result.day_pass) {
        setDayPasses((previous) => [...previous.filter((p) => p.festival_day !== selectedPassDay), result.day_pass]);
        setNewlyIssuedDayPass(result.day_pass);
      }
      setNotice(result.message || `Your ${selectedPassDay} campus pass is ready. Check your registered email.`);
    } catch (err) {
      setNotice(err.message || "Unable to register for this festival day.");
    } finally { setDayPassLoading(false); }
  }

  async function applyAsOrganizer(event) {
    event.preventDefault();

    if (!societyCode.trim()) {
      setOrganizerNotice({ type: "error", message: "Society code is required." });
      return;
    }

    if (!token) {
      setOrganizerNotice({ type: "error", message: "Your session has expired. Please log in again." });
      return;
    }

    setOrganizerSubmitting(true);
    setOrganizerNotice({ type: "", message: "" });

    try {
      const response = await fetch(`${API_BASE_URL}/api/organizers/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        // user_id is taken securely from the JWT by the backend.
        // society_id is resolved from the approved society_code by the service.
        body: JSON.stringify({ society_code: societyCode.trim() }),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.success) {
        throw new Error(
          result.message ||
          result.error ||
          `Organizer application failed (${response.status}). Check that the society code is correct and the society is approved.`
        );
      }

      setOrganizerNotice({
        type: "success",
        message: result.message || "Application submitted. Waiting for admin approval.",
      });
      setSocietyCode("");
    } catch (err) {
      setOrganizerNotice({
        type: "error",
        message: err.message || "Something went wrong. Please try again.",
      });
    } finally {
      setOrganizerSubmitting(false);
    }
  }

  async function submitFeedback(event) {
    event.preventDefault();
    setFeedbackNotice({ type: "", message: "" });
    if (!feedbackEventId) {
      setFeedbackNotice({ type: "error", message: "Please select an event." });
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/feedback/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ event_id: Number(feedbackEventId), rating: Number(feedbackRating), comment: feedbackComment.trim() }),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = result.error ? ` (${result.error})` : "";
        throw new Error(`${result.message || "Unable to submit feedback."}${detail}`);
      }
      setFeedbackNotice({ type: "success", message: "Thank you! Your feedback has been submitted." });
      setMyFeedback((previous) => [...previous, { event_id: Number(feedbackEventId), rating: Number(feedbackRating), comment: feedbackComment.trim() }]);
      setFeedbackEventId("");
      setFeedbackRating(5);
      setFeedbackComment("");
    } catch (err) {
      setFeedbackNotice({ type: "error", message: err.message || "Unable to submit feedback." });
    }
  }

  async function askFestify(question = chatQuestion) {
    const value = String(question || "").trim();
    if (!value) return;
    setChatQuestion(value);
    setChatAnswer("");
    setChatLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/faq/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: value }),
      });
      const result = await response.json().catch(() => ({}));
      const matches = result.matches || [];
      setChatAnswer(matches.length
        ? matches.map((item) => `${item.question}\n${item.answer}`).join("\n\n")
        : (result.message || "Please contact the Festify help desk."));
    } catch {
      setChatAnswer("Unable to connect right now. Please try again or contact your event organizer.");
    } finally {
      setChatLoading(false);
    }
  }

  function logout() {
    sessionStorage.removeItem("festify_token");
    sessionStorage.removeItem("festify_user");
    sessionStorage.removeItem("festify_role");
    window.location.href = "/";
  }

  function showPage(page) {
    setActivePage(page);
    window.setTimeout(() => {
      const target = page === "Explore Events"
        ? document.querySelector("#event-lineup")
        : page === "My Registrations"
          ? document.querySelector(".student-main .lineup-section")
          : page === "My Profile" || page === "Become an Organizer"
            ? document.querySelector(".student-main .profile-page")
            : document.querySelector(".student-main");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 0);
    setProfileOpen(false);
    setNotice("");
    setOrganizerNotice({ type: "", message: "" });
  }

  return (
    <div className="student-app">
      <header className="student-nav">
        <button
          className="intro-brand dashboard-home-brand"
          onClick={() => showPage("Explore Events")}
          aria-label="Festify home"
        >
          <span className="brand-symbol">F</span>
          FESTIFY
        </button>
        

        <nav className="student-nav-links">
          <button
            className={activePage === "Explore Events" ? "nav-active" : ""}
            onClick={() => showPage("Explore Events")}
          >
            Discover
          </button>
          <button
            className={activePage === "My Registrations" ? "nav-active" : ""}
            onClick={() => showPage("My Registrations")}
          >
            My Events
          </button>
          <button
            className={activePage === "Feedback" ? "nav-active" : ""}
            onClick={() => showPage("Feedback")}
          >
            Feedback
          </button>
        </nav>

        <div className="profile-wrapper" ref={profileRef}>
          <button
            className="profile-button"
            onClick={() => setProfileOpen((open) => !open)}
            aria-expanded={profileOpen}
          >
            <span className="profile-avatar">
              {(user.name || "S").charAt(0).toUpperCase()}
            </span>
            <span className="profile-name">{user.name || "Student"}</span>
            <span className="profile-chevron">⌄</span>
          </button>

          {profileOpen && (
            <div className="profile-dropdown">
              <div className="dropdown-user">
                <strong>{user.name || "Student"}</strong>
                <span>{user.email || "Student account"}</span>
              </div>
              <button onClick={() => showPage("My Profile")}>
                <span>◉</span> My Profile
              </button>
              <button onClick={() => showPage("Become an Organizer")}>
                <span>✦</span> Become an Organizer
              </button>
              <button onClick={() => showPage("My Registrations")}>
                <span>▣</span> My Registrations
              </button>
              <button className="dropdown-logout" onClick={logout}>
                ↗ Log out
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="organizer-sticky-banner">
        <span>Want to contribute to Festify?</span>
        <button type="button" onClick={() => showPage("Become an Organizer")}>Become an organizer ↗</button>
      </div>

      <main className="student-main">
        <section className="student-hero">
          <div className="hero-orb hero-orb-one" />
          <div className="hero-orb hero-orb-two" />

          <div className="hero-content">
            <span className="eyebrow">
              <span className="eyebrow-dot" />
              THE FESTIVAL EXPERIENCE
            </span>
            <h1>
              THE CAMPUS
              <br />
              <span>IS YOURS</span>
            </h1>
            <p>
              Hey, {user.name?.split(" ")[0] || "there"}! Discover the
              competitions, performances, and people that make this fest
              unforgettable.
            </p>
            <button
              className="hero-cta"
              onClick={() => {
                showPage("Explore Events");
                document
                  .getElementById("event-lineup")
                  ?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              Explore the lineup <span>↗</span>
            </button>
          </div>

          <div className="hero-art" aria-hidden="true">
            <div className="art-ring art-ring-one" />
            <div className="art-ring art-ring-two" />
            <div className="art-star">✳</div>
            <div className="art-number">01</div>
            <div className="art-caption">YOUR MOMENT<br />STARTS HERE</div>
          </div>

          <div className="hero-bottom">
            <span>DISCOVER YOUR NEXT BIG MOMENT</span>
            <span>SCROLL TO EXPLORE ↓</span>
          </div>
        </section>

        <section className="student-stats">
          <div className="stat-item">
            <span className="stat-icon stat-purple">✦</span>
            <div>
              <strong>{events.length}</strong>
              <span>EVENTS TO EXPLORE</span>
            </div>
          </div>
          <div className="stat-item">
            <span className="stat-icon stat-pink">▣</span>
            <div>
              <strong>{registrations.length}</strong>
              <span>YOUR REGISTRATIONS</span>
            </div>
          </div>
          <div className="stat-item">
            <span className="stat-icon stat-yellow">♧</span>
            <div>
              <strong>{Math.max(0, societies.length - 1)}</strong>
              <span>PARTICIPATING SOCIETIES</span>
            </div>
          </div>
        </section>

        
{notice &&
  !/deadline|registration closed|registration is closed|registration has ended|last date.*passed/i.test(
    notice
  ) && (
    <div className="student-notice" role="status">
      <span>{notice}</span>
      <button
        type="button"
        onClick={() => setNotice("")}
        aria-label="Dismiss message"
      >
        ×
      </button>
    </div>
  )}


        {activePage === "My Profile" ? (
          <section className="profile-page">
            <span className="section-kicker">YOUR ACCOUNT</span>
            <h2>My Profile<span>.</span></h2>
            <div className="profile-detail-card">
              <div className="large-avatar">
                {(user.name || "S").charAt(0).toUpperCase()}
              </div>
              <div>
                <h3>{user.name || "Student"}</h3>
                <p>{user.email || "No email available"}</p>
                <span className="account-label">STUDENT / PARTICIPANT ACCOUNT</span>
              </div>
            </div>

            <div className="profile-information-card">
              <h3>Account information</h3>
              <div className="profile-information-grid">
                <div><span>Phone number</span><strong>{user.phone || "Not available"}</strong></div>
                <div><span>College</span><strong>{user.college_name || "Not available"}</strong></div>
                <div><span>College ID number</span><strong>{user.college_id_number || "Not available"}</strong></div>
                <div><span>Branch</span><strong>{user.branch || "Not available"}</strong></div>
                <div><span>Year of study</span><strong>{user.year_of_study ? `Year ${user.year_of_study}` : "Not available"}</strong></div>
                <div><span>Date of birth</span><strong>{user.date_of_birth || "Not available"}</strong></div>
                <div><span>Gender</span><strong>{user.gender || "Not available"}</strong></div>
              </div>
            </div>

            <div className="profile-action-row">
              <div>
                <h3>Want to organize events?</h3>
                <p>Submit an organizer application using your existing student account.</p>
              </div>
              <button className="organizer-primary-button" onClick={() => showPage("Become an Organizer")}>
                Become an Organizer ↗
              </button>
            </div>
            <button className="secondary-button" onClick={logout}>
              Log out of Festify ↗
            </button>
          </section>
        ) : activePage === "Become an Organizer" ? (
          <section className="profile-page organizer-application-page">
            <span className="section-kicker">TAKE THE LEAD</span>
            <h2>Become an Organizer<span>.</span></h2>
            <p className="organizer-page-intro">
              Apply to manage events for your college society. Your existing student account details will be linked automatically.
            </p>

            <div className="organizer-account-summary">
              <div className="organizer-summary-avatar">{(user.name || "S").charAt(0).toUpperCase()}</div>
              <div className="organizer-summary-copy">
                <strong>{user.name || "Student"}</strong>
                <span>{user.email || "No email available"}</span>
                <small>{user.college_name || "College not available"} · {user.branch || "Branch not available"}</small>
              </div>
              <span className="organizer-pending-label">STUDENT</span>
            </div>

            {organizerNotice.message && (
              <div className={`organizer-form-notice ${organizerNotice.type}`} role="status">
                {organizerNotice.message}
              </div>
            )}

            <form className="organizer-application-form" onSubmit={applyAsOrganizer}>
              <div className="organizer-form-heading">
                <span>APPLICATION DETAILS</span>
                <h3>Society information</h3>
                <p>Only enter the society code here. Your user ID and society ID are linked by the backend.</p>
              </div>

              <label htmlFor="organizer-society-code">Approved society code <span>*</span></label>
              <input
                id="organizer-society-code"
                type="text"
                value={societyCode}
                onChange={(event) => setSocietyCode(event.target.value)}
                placeholder="e.g. SOCIETY-2026"
                maxLength={50}
                autoComplete="off"
                required
              />
              <p className="organizer-form-hint">
                Enter the code provided by a society that has already been approved by the Festify admin. A maximum of four pending or approved organizers is allowed per society.
              </p>

              <div className="organizer-form-footer">
                <button type="button" className="secondary-button" onClick={() => showPage("My Profile")}>
                  Back to profile
                </button>
                <button type="submit" className="organizer-primary-button" disabled={organizerSubmitting}>
                  {organizerSubmitting ? "Submitting..." : "Submit application ↗"}
                </button>
              </div>
            </form>

            <div className="organizer-approval-note">
              <span>ⓘ</span>
              <p>Your application will be marked <strong>PENDING</strong>. Your account role changes to ORGANIZER only after admin approval.</p>
            </div>
          </section>
        ) : activePage === "Feedback" ? (
          <section className="profile-page student-feedback-page">
            <span className="section-kicker">YOUR VOICE MATTERS</span>
            <h2>EVENT FEEDBACK<span>.</span></h2>
            <p className="organizer-page-intro">Share your experience and help us make every Festify event better.</p>
            {feedbackNotice.message && <div className={`organizer-form-notice ${feedbackNotice.type}`} role="status">{feedbackNotice.message}</div>}
            <form className="organizer-application-form" onSubmit={submitFeedback}>
              <div className="organizer-form-heading"><span>STUDENT EXPERIENCE</span><h3>Tell us what you think</h3><p>Your student identity is taken securely from your login. Feedback is linked to the selected event.</p></div>
              <label htmlFor="feedback-event">Select event <span>*</span></label>
              <select id="feedback-event" value={feedbackEventId} onChange={(e) => setFeedbackEventId(e.target.value)} required>
                <option value="">Choose an event</option>
                {events.map((event) => {
                  const id = getEventId(event);
                  const alreadySubmitted = myFeedback.some((item) => String(item.event_id) === String(id));
                  return id != null ? <option key={id} value={id} disabled={alreadySubmitted}>{getTitle(event)}{alreadySubmitted ? " · Feedback submitted" : ""}</option> : null;
                })}
              </select>
              <label htmlFor="feedback-rating">Your rating <span>*</span></label>
              <select id="feedback-rating" value={feedbackRating} onChange={(e) => setFeedbackRating(Number(e.target.value))}>
                <option value={5}>5 - Excellent</option><option value={4}>4 - Very good</option><option value={3}>3 - Good</option><option value={2}>2 - Needs improvement</option><option value={1}>1 - Poor</option>
              </select>
              <label htmlFor="feedback-comment">Comments</label>
              <textarea id="feedback-comment" rows={5} maxLength={2000} value={feedbackComment} onChange={(e) => setFeedbackComment(e.target.value)} placeholder="What did you enjoy? What can we improve?" />
              <div className="organizer-form-footer"><span>{feedbackComment.length}/2000</span><button type="submit" className="organizer-primary-button">Submit feedback ↗</button></div>
            </form>
            <div className="profile-information-card">
              <h3>Your submitted feedback</h3>
              {myFeedback.length ? myFeedback.map((item, index) => {
                const event = events.find((entry) => String(getEventId(entry)) === String(item.event_id));
                return <div className="student-feedback-history" key={item.feedback_id || `${item.event_id}-${index}`}><strong>{event ? getTitle(event) : `Event #${item.event_id}`}</strong><span>{"★".repeat(item.rating)}{"☆".repeat(5-item.rating)}</span><p>{item.comment || "No comment added."}</p></div>;
              }) : <p>You haven't submitted feedback yet.</p>}
            </div>
          </section>
        ) : activePage === "My Registrations" ? (
          <section className="lineup-section">
            <div className="section-heading">
              <div>
                <span className="section-kicker">YOUR FESTIVAL JOURNEY</span>
                <h2>MY EVENTS<span>.</span></h2>
                <p>Your registered events, all in one place.</p>
              </div>
              <button
                className="secondary-button"
                onClick={() => showPage("Explore Events")}
              >
                Discover more ↗
              </button>
            </div>

            {registrations.length === 0 ? (
              <div className="empty-state">
                <span>✳</span>
                <h3>Your lineup is waiting.</h3>
                <p>You haven't registered for any events yet.</p>
                <button
                  className="hero-cta"
                  onClick={() => showPage("Explore Events")}
                >
                  Find your first event ↗
                </button>
              </div>
            ) : (
              <div className="event-grid">
                {registrations.map((registration, index) => {
                  const event = registration.event || registration;
                  const id =
                    registration.event_id ??
                    event.event_id ??
                    event.id ??
                    index;

                  return (
                    <EventCard
                      key={`${id}-${registration.event_day || "Day-1"}`}
                      event={{ ...event, day: registration.event_day || "Day-1" }}
                      registeredDays={new Set([registration.event_day || "Day-1"])}
                      hasCampusPass={dayPasses.some((pass) => pass.festival_day === (registration.event_day || getDay(event) || "Day-1") && pass.status !== "CANCELLED")}
                      readOnly
                    />
                  );
                })}
              </div>
            )}
          </section>
        ) : (
          <>
            <section className="day-pass-section day-pass-registration-section" id="day-register-section">
              <div className="section-heading">
                <div><span className="section-kicker">PLAN YOUR FESTIVAL</span><h2>CAMPUS DAY PASS<span>.</span></h2><p>Register once for the festival day you plan to attend. This pass is separate from event registration.</p></div>
              </div>
              <div className="day-pass-panel day-pass-register-panel">
                <label htmlFor="festival-day-select">Choose festival day
                  <select id="festival-day-select" value={selectedPassDay} onChange={(e) => { setSelectedPassDay(e.target.value); setNotice(""); setNewlyIssuedDayPass(null); }}>
                    <option value="Day-1">Day-1</option><option value="Day-2">Day-2</option><option value="Day-3">Day-3</option>
                  </select>
                </label>
                {dayPasses.some((pass) => pass.festival_day === selectedPassDay && pass.status !== "CANCELLED") ? (
                  <div className="campus-pass-already"><strong>✓ Already registered for {selectedPassDay}</strong><span>Your QR pass has already been sent to your registered email.</span></div>
                ) : (
                  <button type="button" className="register-button" onClick={registerForFestivalDay} disabled={dayPassLoading}>{dayPassLoading ? "Registering..." : "Register & Get QR Pass ↗"}</button>
                )}
              </div>
              {newlyIssuedDayPass?.festival_day === selectedPassDay && newlyIssuedDayPass.qr_code_base64 && (
                <div className="campus-pass-qr-result"><img src={`data:image/png;base64,${newlyIssuedDayPass.qr_code_base64}`} alt={`${selectedPassDay} campus entry QR pass`} /><div><strong>{selectedPassDay} QR pass generated</strong><span>Keep this QR ready for campus entry. A copy was sent by email when delivery succeeded.</span></div></div>
              )}
              {registrations.some((r) => (r.event_day || getDay(r.event) || "Day-1") === selectedPassDay && String(r.registration_status || "").toUpperCase() !== "CANCELLED") && !dayPasses.some((pass) => pass.festival_day === selectedPassDay && pass.status !== "CANCELLED") && (
                <p className="campus-pass-reminder" role="status">You have registered for an event on {selectedPassDay}. Also get the QR pass for {selectedPassDay} in order to enter the campus.</p>
              )}
              {notice && <p className="day-register-notice" role="status">{notice}</p>}
              <p className="day-pass-note">One campus QR pass per festival day. Event registration remains available on each event card.</p>
            </section>

            
{notice &&
  /deadline|registration closed|registration is closed|registration has ended|last date.*passed/i.test(
    notice
  ) && (
    <p
      ref={deadlineAlertRef}
      className="registration-deadline-alert"
      role="alert"
      aria-live="assertive"
    >
      <span aria-hidden="true">!</span>
      {" "}{notice}
      <button
        type="button"
        className="deadline-alert-dismiss"
        onClick={() => setNotice("")}
        aria-label="Dismiss deadline alert"
      >
        ×
      </button>
    </p>
  )}

            <section className="lineup-section" id="event-lineup">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">FIND YOUR THING</span>
                  <h2>THE LINEUP</h2>
                  <p>One fest. Countless ways to make a memory.</p>
                </div>
                <span className="live-label">
                  <span /> LIVE LINEUP
                </span>
              </div>

              <div className="category-tabs">
                {CATEGORIES.map((category) => (
                  <button
                    key={category}
                    className={activeCategory === category ? "category-active" : ""}
                    onClick={() => setActiveCategory(category)}
                  >
                    {category}
                  </button>
                ))}
              </div>

              <div className="event-filters">
                <label className="event-search">
                  <span>⌕</span>
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search events, societies..."
                  />
                </label>

                <select
                  value={activeDay}
                  onChange={(event) => setActiveDay(event.target.value)}
                  aria-label="Filter by day"
                >
                  {days.map((day) => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>

                <select
                  value={activeSociety}
                  onChange={(event) => setActiveSociety(event.target.value)}
                  aria-label="Filter by society"
                >
                  {societies.map((society) => (
                    <option key={society} value={society}>{society}</option>
                  ))}
                </select>
              </div>

              {loading ? (
                <div className="empty-state">
                  <div className="loading-spinner" />
                  <h3>Setting the stage...</h3>
                  <p>Loading the latest events.</p>
                </div>
              ) : error ? (
                <div className="empty-state error-state">
                  <span>✳</span>
                  <h3>The lineup couldn't load.</h3>
                  <p>{error}</p>
                  <button
                    className="secondary-button"
                    onClick={() => window.location.reload()}
                  >
                    Try again ↻
                  </button>
                </div>
              ) : filteredEvents.length === 0 ? (
                <div className="empty-state">
                  <span>✳</span>
                  <h3>No events found.</h3>
                  <p>Try another category, day, society, or search term.</p>
                  <button
                    className="secondary-button"
                    onClick={() => {
                      setActiveCategory("All Events");
                      setActiveDay("All Days");
                      setActiveSociety("All Societies");
                      setSearch("");
                    }}
                  >
                    Clear filters
                  </button>
                </div>
              ) : (
                <div className="event-grid">
                  {filteredEvents.map((event, index) => (
                    <EventCard
                      key={getEventId(event) ?? index}
                      event={event}
                      registeredDays={new Set(["Day-1", "Day-2", "Day-3"].filter((day) => registeredIds.has(registrationKey(getEventId(event), day))))}
                      hasCampusPass={dayPasses.some((pass) => pass.festival_day === (getDay(event) || "Day-1") && pass.status !== "CANCELLED")}
                      registering={registeringId != null && registeringId.startsWith(`${String(getEventId(event))}::`)}
                      onRegister={(day) => registerForEvent(event, day)}
                      reaction={reactions[String(getEventId(event))] || { likes: 0, dislikes: 0, my_reaction: null }}
                      onReact={(choice) => reactToEvent(event, choice)}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}

        <div className="festify-chatbot">
          {chatOpen && (
            <section className="festify-chat-panel" aria-label="Festify help and questions">
              <header><div><strong>Festify Assistant</strong><span>Quick answers for your fest</span></div><button type="button" onClick={() => setChatOpen(false)} aria-label="Close chatbot">×</button></header>
              <div className="festify-chat-content">
                <p className="festify-chat-intro">Hi {user.name?.split(" ")[0] || "there"}! Choose a common question or type your own.</p>
                <div className="festify-faq-picker">
                  <label htmlFor="festify-faq-select">Browse frequently asked questions</label>
                  <select
                    id="festify-faq-select"
                    value={selectedFaqId}
                    onChange={(event) => {
                      const selected = faqs.find((faq) => String(faq.faq_id) === event.target.value);
                      setSelectedFaqId(event.target.value);
                      if (selected) {
                        setChatQuestion(selected.question);
                        setChatAnswer(`${selected.question}\n\n${selected.answer}`);
                      }
                    }}
                  >
                    <option value="">Select a question...</option>
                    {faqs.map((faq) => (
                      <option key={faq.faq_id} value={String(faq.faq_id)}>
                        {faq.category ? `${faq.category}: ` : ""}{faq.question}
                      </option>
                    ))}
                  </select>
                  {!faqs.length && <small>{faqLoadMessage || "Loading questions from the FAQ database..."}</small>}
                </div>
                {chatAnswer && <pre className="festify-chat-answer">{chatAnswer}</pre>}
              </div>
              <form className="festify-chat-input" onSubmit={(e) => { e.preventDefault(); askFestify(); }}>
                <input value={chatQuestion} onChange={(e) => setChatQuestion(e.target.value)} placeholder="Ask about registrations, passes..." />
                <button type="submit" disabled={chatLoading || !chatQuestion.trim()}>{chatLoading ? "…" : "Send"}</button>
              </form>
            </section>
          )}
          <button type="button" className="festify-chat-launcher" onClick={() => setChatOpen((open) => !open)} aria-expanded={chatOpen}>
            <span>✦</span>{chatOpen ? "Close help" : "Ask Festify"}
          </button>
        </div>

        <footer className="student-footer">
          <button
            className="intro-brand dashboard-home-brand"
            onClick={() => showPage("Explore Events")}
            aria-label="Festify home"
          >
            <span className="brand-symbol">F</span>
            FESTIFY
          </button>
          <span>MAKE NOISE. MAKE MEMORIES.</span>
          <span>YOUR FEST. YOUR STORY.</span>
        </footer>
      </main>
    </div>
  );
}

function formatTime12(value) {
  if (!value) return "To be announced";

  const text = String(value).trim();

  // Handle values such as "14:30:00", "14:30", or "2:30 PM".
  const match = text.match(/^(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)?$/i);

  if (!match) return text;

  let hour = Number(match[1]);
  const minute = match[2];
  let period = match[3]?.toUpperCase();

  if (!period) {
    period = hour >= 12 ? "PM" : "AM";
  }

  hour = hour % 12 || 12;

  return `${hour}:${minute} ${period}`;
}

function formatDateDisplay(value) {
  if (!value) return "To be announced";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}


function EventCard({
  event,
  registeredDays = new Set(),
  registering,
  onRegister,
  readOnly = false,
  reaction = { likes: 0, dislikes: 0, my_reaction: null },
  onReact,
}) {
  const [detailsOpen, setDetailsOpen] = useState(false);

  const title = getTitle(event);
  const category = getCategory(event);
  const society = getSociety(event);
  const day = getDay(event);

  const image =
    event.image_url ||
    event.poster_url ||
    event.banner_url ||
    event.image ||
    event.poster ||
    "";

  const startTime = event.start_time || event.event_time;
  const deadline =
    event.registration_deadline ||
    event.last_registration_date ||
    event.registration_last_date ||
    event.registration_deadline_date;

  return (
    <article className="event-card">
      {/* Event poster */}
      <div
        className={`event-poster poster-${category
          .toLowerCase()
          .replace(/\s+/g, "-")}`}
      >
        {image ? (
          <img src={image} alt={`${title} poster`} />
        ) : (
          <span className="poster-decoration">✳</span>
        )}

        <div className="event-poster-overlay">
          <span className="poster-category">{category}</span>

          {society && (
            <span className="poster-society">{society}</span>
          )}

          <strong className="poster-event-title">{title}</strong>
          <span className="poster-bottom">FESTIFY / LIVE</span>
        </div>

        <span className="poster-day">{day || "FEST DAY"}</span>
      </div>

      {/* Event details and actions */}
      <div className="event-card-body">
        <div className="event-extra-details">
          <button
            type="button"
            className="event-details-toggle"
            aria-expanded={detailsOpen}
            onClick={() => setDetailsOpen((open) => !open)}
          >
            <summary>View event details</summary>

            <span className="event-details-icon" aria-hidden="true">
              {detailsOpen ? "−" : "+"}
            </span>
          </button>

          {detailsOpen && (
            <div className="event-extra-details-content">
              <strong>Description</strong>
              <p>
                {event.description ||
                  event.about ||
                  "Details will be announced by the organizer."}
              </p>

              <strong>Rules &amp; regulations</strong>
              <p>
                {event.rules ||
                  event.event_rules ||
                  event.rules_and_regulations ||
                  "Please follow the instructions shared by the event organizer."}
              </p>

              <strong>Eligibility</strong>
              <p>
                {event.eligibility ||
                  event.eligibility_criteria ||
                  "Check the event instructions or contact the organizer for eligibility details."}
              </p>

              <div className="event-detail-time-grid">
                <div>
                  <strong>Starts</strong>
                  <p>
                    {typeof formatEventDateTime === "function"
                      ? formatEventDateTime(
                          event.event_date || event.date,
                          startTime
                        )
                      : formatTime12(startTime)}
                  </p>
                </div>

                <div>
                  <strong>Ends</strong>
                  <p>
                    {typeof formatEventDateTime === "function"
                      ? formatEventDateTime(
                          event.event_date || event.date,
                          event.end_time
                        )
                      : formatTime12(event.end_time)}
                  </p>
                </div>

                <div>
                  <strong>Last date to register</strong>
                  <p>
                    {deadline
                      ? typeof formatDeadline === "function"
                        ? formatDeadline(deadline)
                        : formatDateDisplay(deadline)
                      : "To be announced"}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Likes and dislikes */}
        <div className="event-reactions" aria-label="Event reactions">
          <button
            type="button"
            className={`reaction-button reaction-like ${
              reaction.my_reaction === "like" ? "reaction-active" : ""
            }`}
            onClick={() => onReact?.("like")}
            aria-pressed={reaction.my_reaction === "like"}
          >
            <span aria-hidden="true">👍</span>
            <span>Like</span>
            <b>{reaction.likes || 0}</b>
          </button>

          <button
            type="button"
            className={`reaction-button reaction-dislike ${
              reaction.my_reaction === "dislike" ? "reaction-active" : ""
            }`}
            onClick={() => onReact?.("dislike")}
            aria-pressed={reaction.my_reaction === "dislike"}
          >
            <span aria-hidden="true">👎</span>
            <span>Dislike</span>
            <b>{reaction.dislikes || 0}</b>
          </button>
        </div>

        {/* Registration */}
        <div className="event-card-bottom">
          <p className="event-date">
                    {typeof formatEventDateTime === "function"
                      ? formatEventDateTime(
                          event.event_date || event.date,
                          startTime
                        )
                      : formatTime12(startTime)}
                  </p>
          

          <div className="event-day-registration">
            {readOnly ? (
              <span className="registered-button">
                ✓ Registered · {day || "Day-1"}
              </span>
            ) : registeredDays.has(day || "Day-1") ? (
              <span className="registered-button">✓ Registered</span>
            ) : (
              <button
                type="button"
                className="register-button"
                onClick={() => onRegister?.(day || "Day-1")}
                disabled={registering || !onRegister}
              >
                {registering ? "Registering..." : "Register ↗"}
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}


function formatEventTime(value) {
  if (!value) return "";
  const match = String(value).match(/^(\d{1,2}):(\d{2})/);
  if (!match) return String(value);
  let hour = Number(match[1]);
  const minute = match[2];
  const suffix = hour >= 12 ? "PM" : "AM";
  hour = hour % 12 || 12;
  return `${hour}:${minute} ${suffix}`;
}

function formatEventDateTime(dateValue, timeValue) {
  if (!dateValue && !timeValue) return "To be announced";
  const dateText = dateValue ? new Date(`${String(dateValue).slice(0, 10)}T00:00:00`).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "";
  const timeText = formatEventTime(timeValue);
  return [dateText, timeText].filter(Boolean).join(" · ") || "To be announced";
}

function formatDeadline(value) {
  if (!value) return "To be announced";
  const raw = String(value);
  const normalized = raw.includes("T") ? raw : raw.replace(" ", "T");
  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) return raw;
  return `${parsed.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })} · ${formatEventTime(`${String(parsed.getHours()).padStart(2, "0")}:${String(parsed.getMinutes()).padStart(2, "0")}`)}`;
}

function getTitle(event) {
  return event.title || event.event_name || event.name || "Untitled Event";
}

function getCategory(event) {
  return event.category || event.event_category || event.event_type || "Other";
}

function getSociety(event) {
  const society =
    event.society_name ||
    event.society?.name ||
    event.society?.society_name ||
    event.organizer_name ||
    event.organizing_society;

  return typeof society === "string" ? society : "";
}

function getDay(event) {
  const day = event.day || event.event_day || event.fest_day;
  if (day != null && day !== "") {
    return String(day).toLowerCase().includes("day")
      ? String(day)
      : `Day ${day}`;
  }
  return "";
}

function getEventId(event) {
  return event.event_id ?? event.id ?? event.eventId;
}

export default StudentDashboard;
