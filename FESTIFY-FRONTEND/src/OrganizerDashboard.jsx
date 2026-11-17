import { useEffect, useRef, useState } from "react";
import "./OrganizerDashboard.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const categories = [
  "Technical", "Cultural", "Music", "Dance", "Gaming",
  "Sports", "Literary", "Workshop", "Other",
];

const FEST_DATES = {
  "Day-1": "2026-11-28",
  "Day-2": "2026-11-29",
  "Day-3": "2026-11-30",
};

const emptyEvent = {
  event_name: "",
  description: "",
  category: "Technical",
  fest_day: "Day-1",
  event_date: "",
  start_time: "",
  end_time: "",
  venue_id: "",
  capacity: 100,
  eligibility: "",
  rules: "",
  registration_deadline: "",
  event_image: "",
};

function OrganizerDashboard() {
  const token = sessionStorage.getItem("festify_token");
  const [user] = useState(() =>
    JSON.parse(sessionStorage.getItem("festify_user") || "{}")
  );
  const organizerId =
    user.organizer_id ?? user.organizer_profile?.organizer_id ??
    user.organizer?.organizer_id;

  const [page, setPage] = useState("Events");
  const mainContentRef = useRef(null);
  const pageContentRef = useRef(null);
  const [events, setEvents] = useState([]);
  const [venues, setVenues] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyEvent);
  const [search, setSearch] = useState("");
  const profileRef = useRef(null);

  async function api(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.message || data.error || `Request failed (${response.status})`);
    return data;
  }

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const [eventData, venueData] = await Promise.all([
        api("/api/events/"),
        api("/api/venues/active").catch(() => api("/api/venues/")),
      ]);

      const eventList = Array.isArray(eventData)
        ? eventData
        : eventData.events || eventData.data || [];

      setEvents(
        organizerId
          ? eventList.filter((event) =>
            String(event.organizer_id) === String(organizerId)
          )
          : []
      );

      const venueList = Array.isArray(venueData)
        ? venueData
        : venueData.venues || venueData.data || [];
      setVenues(venueList.filter((venue) =>
        String(venue.venue_status || venue.status || "ACTIVE").toUpperCase() === "ACTIVE"
      ));

      if (organizerId) {
        const analyticsData = await api(`/api/analytics/organizer/${organizerId}`);
        setAnalytics(analyticsData.analytics || analyticsData.data || analyticsData);
      }
    } catch (err) {
      setError(err.message || "Unable to load organizer data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      window.location.href = "/";
      return;
    }
    if (!["ORGANIZER", "ADMIN", "SUPER_ADMIN"].includes(
      String(sessionStorage.getItem("festify_role") || "").toUpperCase()
    )) {
      window.location.href = "/";
      return;
    }
    loadDashboard();
    // The token and organizer profile ID identify this dashboard session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, organizerId]);

  useEffect(() => {
    function closeOutside(event) {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", closeOutside);
    return () => document.removeEventListener("mousedown", closeOutside);
  }, []);

  function logout() {
    ["festify_token", "festify_user", "festify_role"].forEach((key) =>
      sessionStorage.removeItem(key)
    );
    window.location.href = "/";
  }

  function openCreate() {
    setEditingId(null);
    setForm(emptyEvent);
    setFormOpen(true);
    setNotice("");
  }

  function openEdit(event) {
    setEditingId(event.event_id);
    setForm({
      ...emptyEvent,
      ...event,
      venue_id: event.venue_id ?? "",
      event_date: event.event_date || "",
      start_time: String(event.start_time || "").slice(0, 5),
      end_time: String(event.end_time || "").slice(0, 5),
      registration_deadline: event.registration_deadline
        ? String(event.registration_deadline).replace(" ", "T").slice(0, 16)
        : "",
    });
    setFormOpen(true);
    setNotice("");
  }

  async function saveEvent(event) {
    event.preventDefault();
    if (!organizerId) {
      setNotice("Your login response is missing organizer_id. Please update the backend login response to include the organizer profile ID.");
      return;
    }

    setSaving(true);
    setNotice("");
    try {
      const payload = {
          ...form,
          event_date: form.event_date || FEST_DATES[form.fest_day || "Day-1"],
          organizer_id: organizerId,
        venue_id: form.venue_id ? Number(form.venue_id) : null,
        capacity: Number(form.capacity),
        registration_deadline: form.registration_deadline
          ? `${form.registration_deadline.replace("T", " ")}:00`
          : "",
      };

      const path = editingId
        ? `/api/events/${editingId}`
        : "/api/events/";
      const result = await api(path, {
        method: editingId ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });

      setNotice(result.message || (editingId ? "Event updated successfully." : "Event created successfully."));
      setFormOpen(false);
      await loadDashboard();
    } catch (err) {
      setNotice(err.message || "Unable to save the event.");
    } finally {
      setSaving(false);
    }
  }


  async function submitForApproval(event) {
    try {
      const result = await api(`/api/events/${event.event_id}/submit`, {
        method: "POST",
      });

      setNotice(result.message || "Event submitted for approval.");
      await loadDashboard();
    } catch (err) {
      setNotice(err.message || "Unable to submit event for approval.");
    }
  }


  async function publishEvent(event) {
    try {
      const result = await api(
        `/api/events/${event.event_id}/publish`,
        { method: "PATCH" }
      );

      setNotice(result.message || "Event published successfully!");
      await loadDashboard();
    } catch (err) {
      setNotice(err.message || "Unable to publish event.");
    }
  }

  useEffect(() => {
    // Wait until the selected page content has rendered, then scroll to that
    // section (not just to the top of the dashboard container).
    const timer = window.setTimeout(() => {
      pageContentRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 80);
    return () => window.clearTimeout(timer);
  }, [page]);

  const navigateTo = (nextPage) => { setPage(nextPage); setProfileOpen(false); };

  const visibleEvents = events.filter((event) =>
    `${event.event_name || ""} ${event.category || ""} ${event.status || ""}`
      .toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fest-dashboard">
      <header className="fd-nav">
        <button className="intro-brand dashboard-home-brand" onClick={() => navigateTo("Events")} aria-label="Festify home"><span className="brand-symbol">F</span>FESTIFY</button>
        <nav className="fd-links">
          {["Events", "Analytics"].map((item) => (
            <button key={item} className={page === item ? "fd-active" : ""} onClick={() => navigateTo(item)}>
              {item}
            </button>
          ))}
        </nav>
        <div className="fd-profile-wrap" ref={profileRef}>
          <button className="fd-profile" onClick={() => setProfileOpen((value) => !value)}>
            <span className="fd-avatar">{(user.name || "O").charAt(0).toUpperCase()}</span>
            <span>{user.name || "Organizer"}</span><span>⌄</span>
          </button>
          {profileOpen && (
            <div className="fd-dropdown">
              <strong>{user.name || "Organizer"}</strong>
              <small>{user.email || "Organizer account"}</small>
              <button onClick={() => navigateTo("Profile")}>My Profile</button>
              <button className="fd-logout" onClick={logout}>↗ Log out</button>
            </div>
          )}
        </div>
      </header>

      <main className="fd-main" ref={mainContentRef} id="organizer-main-content">
        <section className="fd-hero">
          <div className="fd-hero-copy">
            <span className="fd-kicker">YOUR EVENTS. YOUR STAGE.</span>
            <h1>MAKE IT<br /><span>HAPPEN</span></h1>
            <p>Welcome back, {user.name?.split(" ")[0] || "Organizer"}. Create experiences your campus will remember.</p>
            <button className="fd-primary" onClick={openCreate}>＋ Create an event</button>
          </div>
          <div className="fd-hero-art" aria-hidden="true"><span>✳</span><b>01</b></div>
          <div className="fd-hero-foot"><span>FESTIFY / ORGANIZER STUDIO</span><span>MAKE NOISE. MAKE MEMORIES.</span></div>
        </section>

        {notice && <div className="fd-notice" role="status">{notice}<button onClick={() => setNotice("")}>×</button></div>}
        {error && <div className="fd-alert">{error}<button onClick={loadDashboard}>Retry ↻</button></div>}

        {!organizerId && (
          <div className="fd-alert">
            Your login data does not include the organizer profile ID. Add `organizer_id` to the login response to enable event creation and organizer analytics.
          </div>
        )}

        {page === "Analytics" ? (
          <>
            <div className="fd-section-title" ref={pageContentRef}><div><span className="fd-kicker">THE NUMBERS BEHIND THE MAGIC</span><h2>YOUR ANALYTICS<span>.</span></h2></div><button className="fd-secondary" onClick={loadDashboard}>Refresh ↻</button></div>
            <div className="fd-stats">
              <Stat icon="✦" label="TOTAL EVENTS" value={analytics.total_events ?? events.length} />
              <Stat icon="▣" label="REGISTRATIONS" value={analytics.total_registrations ?? 0} />
              <Stat icon="↗" label="TOTAL ATTENDANCE" value={analytics.total_attendance ?? 0} />
              <Stat icon="◉" label="CAPACITY USED" value={`${analytics.capacity_utilization_percent ?? 0}%`} />
            </div>
            <div className="fd-panel">
              <span className="fd-kicker">AUDIENCE FEEDBACK</span>
              <div className="fd-feedback-row">
                <div><strong className="fd-rating">{analytics.average_rating ?? 0}<small>/5</small></strong><p>Average rating</p></div>
                <div><strong>{analytics.total_feedback_count ?? 0}</strong><p>Feedback responses</p></div>
                <div><strong>{analytics.upcoming_events ?? 0}</strong><p>Published events</p></div>
              </div>
              <div className="fd-rating-bars">
                {[5, 4, 3, 2, 1].map((rating) => {
                  const count = Number(analytics.rating_distribution?.[String(rating)] || 0);
                  const total = Number(analytics.total_feedback_count || 0);
                  return <div className="fd-rating-line" key={rating}><span>{rating} ★</span><div><i style={{ width: `${total ? count / total * 100 : 0}%` }} /></div><b>{count}</b></div>;
                })}
              </div>
              <div className="fd-event-feedback-list">
                <h3>Feedback by event</h3>
                {Object.entries(analytics.feedback_by_event || {}).length ? Object.entries(analytics.feedback_by_event).map(([eventId, item]) => (
                  <div className="fd-event-feedback-item" key={eventId}>
                    <div><strong>{item.event_name}</strong><span>{item.feedback_count} responses · {item.average_rating}/5 average</span></div>
                    <div className="fd-event-rating-distribution">{[5,4,3,2,1].map((rating) => <span key={rating}>{rating}★ {item.rating_distribution?.[String(rating)] || 0}</span>)}</div>
                    {(item.comments || []).slice(0, 3).map((comment, index) => <p key={`${eventId}-${index}`}>“{comment.comment}” <small>— {comment.user_name}, {comment.rating}/5</small></p>)}
                  </div>
                )) : <p>No event feedback has been submitted yet.</p>}
              </div>
            </div>
          </>
        ) : page === "Profile" ? (
          <section className="fd-panel fd-profile-panel" ref={pageContentRef}>
            <span className="fd-kicker">YOUR ACCOUNT</span><h2>MY PROFILE<span>.</span></h2>
            <div className="fd-profile-detail"><span className="fd-avatar fd-avatar-large">{(user.name || "O").charAt(0).toUpperCase()}</span><div><h3>{user.name || "Organizer"}</h3><p>{user.email || "No email available"}</p><span className="fd-status">{user.organizer_status || "ORGANIZER ACCOUNT"}</span></div></div>
            <button className="fd-secondary" onClick={logout}>Log out of Festify ↗</button>
          </section>
        ) : (
          <>
            <div className="fd-section-title" ref={pageContentRef}>
              <div><span className="fd-kicker">BUILD YOUR NEXT BIG MOMENT</span><h2>YOUR EVENTS</h2><p>Manage drafts, track approvals, and see your event lineup.</p></div>
              <button className="fd-primary" onClick={openCreate}>＋ New event</button>
            </div>
            <div className="fd-toolbar">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search your events..." />
              <span className="fd-live"><i /> LIVE WORKSPACE</span>
            </div>
            {loading ? <Empty title="Setting the stage..." text="Loading your events." loading /> :
              visibleEvents.length === 0 ? <Empty title="Your stage is waiting." text="You haven't created any events yet. Start building your first campus experience." action="＋ Create your first event" onAction={openCreate} /> :
                <div className="fd-event-grid">{visibleEvents.map((event) => <article className="fd-event-card" key={event.event_id}>
                  <div className="fd-event-poster"><span>{event.category || "EVENT"}</span><strong>{event.event_name}</strong><small>{event.event_date || "Date to be announced"}</small><b className="fd-event-day fd-event-day-card">{event.fest_day || event.day || "Day-1"}</b><em>{event.status || "DRAFT"}</em></div>
                  <div className="fd-event-content"><p>{event.description || "Your event description will appear here."}</p><div className="fd-event-meta"><span>◷ {event.start_time || "--:--"} – {event.end_time || "--:--"}</span><span>♙ {event.capacity || 0} seats</span></div><div className="fd-event-actions"><span className={`fd-status status-${String(event.status || "DRAFT").toLowerCase()}`}>{event.status || "DRAFT"}</span>{["DRAFT", "REJECTED"].includes(String(event.status).toUpperCase()) && <button className="fd-secondary" onClick={() => openEdit(event)}>Edit</button>}
                    {String(event.status).toUpperCase() === "DRAFT" && (
                      <button
                        className="fd-primary fd-small"
                        onClick={() => submitForApproval(event)}
                      >
                        Submit ↗
                      </button>
                    )}

                    {String(event.status).toUpperCase() === "APPROVED" && (
                      <button
                        className="fd-primary fd-small"
                        onClick={() => publishEvent(event)}
                      >
                        Publish ↗
                      </button>
                    )}
                  </div>{event.rejection_reason && <p className="fd-rejection">Feedback: {event.rejection_reason}</p>}</div>
                </article>)}</div>
            }
          </>
        )}

        <footer className="fd-footer"><span className="intro-brand dashboard-home-brand"><span className="brand-symbol">F</span>FESTIFY</span><span>YOUR FEST. YOUR STORY.</span><span>ORGANIZER STUDIO</span></footer>
      </main>

      {formOpen && <div className="fd-modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setFormOpen(false); }}>
        <form className="fd-modal" onSubmit={saveEvent}>
          <div className="fd-modal-head"><div><span className="fd-kicker">LET'S MAKE SOMETHING GREAT</span><h2>{editingId ? "EDIT EVENT" : "CREATE EVENT"}<span>.</span></h2></div><button type="button" onClick={() => setFormOpen(false)}>×</button></div>
          <label>Event name *<input required value={form.event_name} onChange={(e) => setForm({ ...form, event_name: e.target.value })} /></label>
          <div className="fd-form-grid">
            <label>Category *<select required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{categories.map((c) => <option key={c}>{c}</option>)}</select></label>
            <label>
  Festival day *
  <select
    required
    value={form.fest_day || "Day-1"}
    onChange={(e) => {
      const selectedDay = e.target.value;
      setForm({
        ...form,
        fest_day: selectedDay,
        event_date: FEST_DATES[selectedDay],
      });
    }}
  >
    <option value="Day-1">Day-1</option>
    <option value="Day-2">Day-2</option>
    <option value="Day-3">Day-3</option>
  </select>
</label>
            <label>Venue<select value={form.venue_id} onChange={(e) => setForm({ ...form, venue_id: e.target.value })}><option value="">Choose a venue</option>{venues.map((v) => <option key={v.venue_id} value={v.venue_id}>{v.venue_name} {v.capacity ? `· ${v.capacity} seats` : ""}</option>)}</select></label>
            <label>
  Event date
  <input
    type="date"
    value={form.event_date || FEST_DATES[form.fest_day || "Day-1"]}
    disabled
  />
</label>
            <label>Capacity *<input required min="1" type="number" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} /></label>
            <label>Start time *<input required type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} /></label>
            <label>End time *<input required type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} /></label>
            <label>Registration deadline *<input required type="datetime-local" value={form.registration_deadline} onChange={(e) => setForm({ ...form, registration_deadline: e.target.value })} /></label>
            <label>Poster image URL<input value={form.event_image || ""} onChange={(e) => setForm({ ...form, event_image: e.target.value })} placeholder="https://..." /></label>
          </div>
          <label>Description *<textarea required rows="3" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          <label>Eligibility<textarea rows="2" value={form.eligibility || ""} onChange={(e) => setForm({ ...form, eligibility: e.target.value })} placeholder="Who can participate?" /></label>
          <label>Rules<textarea rows="2" value={form.rules || ""} onChange={(e) => setForm({ ...form, rules: e.target.value })} placeholder="Event rules and guidelines" /></label>
          <div className="fd-modal-actions"><button type="button" className="fd-secondary" onClick={() => setFormOpen(false)}>Cancel</button><button disabled={saving} className="fd-primary">{saving ? "Saving..." : editingId ? "Save changes" : "Create event ↗"}</button></div>
        </form>
      </div>}
    </div>
  );
}

function Stat({ icon, label, value }) {
  return <div className="fd-stat"><span>{icon}</span><div><strong>{value}</strong><small>{label}</small></div></div>;
}

function Empty({ title, text, action, onAction, loading }) {
  return <div className="fd-empty">{loading && <div className="fd-spinner" />}<span className="fd-empty-star">✳</span><h3>{title}</h3><p>{text}</p>{action && <button className="fd-primary" onClick={onAction}>{action}</button>}</div>;
}

export default OrganizerDashboard;