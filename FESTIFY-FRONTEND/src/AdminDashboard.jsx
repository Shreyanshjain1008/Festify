import { useCallback, useEffect, useRef, useState } from "react";
import "./AdminDashboard.css";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function AdminDashboard() {
  const token = sessionStorage.getItem("festify_token");
  const [user] = useState(() =>
    JSON.parse(sessionStorage.getItem("festify_user") || "{}")
  );
  const [page, setPage] = useState("Overview");
  const [analytics, setAnalytics] = useState({});
  const [organizers, setOrganizers] = useState([]);
  const [users, setUsers] = useState([]);
  const [events, setEvents] = useState([]);
  const [venues, setVenues] = useState([]);
  const [societies, setSocieties] = useState([]);
  const [societyForm, setSocietyForm] = useState(null);
  const [savingSociety, setSavingSociety] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [review, setReview] = useState(null);
  const [reviewReason, setReviewReason] = useState("");
  const [venueForm, setVenueForm] = useState(null);
  const [savingVenue, setSavingVenue] = useState(false);
  const profileRef = useRef(null);

  const api = useCallback(async (path, options = {}) => {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.message || data.error || `Request failed (${response.status})`);
    }
    return data;
  }, [token]);

  const listFrom = (data, key) =>
    Array.isArray(data) ? data : data[key] || data.data || [];

  const refresh = useCallback(async (showLoader = false) => {
    if (showLoader) setLoading(true);
    setError("");
    try {
      const [analyticsData, organizerData, userData, eventData, venueData, societyData] =
        await Promise.all([
          api("/api/analytics/admin/"),
          api("/api/admin/organizers"),
          api("/api/admin/users"),
          api("/api/admin/events"),
          api("/api/venues/").catch(() => ({ venues: [] })),
          api("/api/admin/societies").catch(() => ({ societies: [] })),
        ]);

      setAnalytics(analyticsData.analytics || analyticsData.data || analyticsData);
      setOrganizers(listFrom(organizerData, "organizers"));
      setUsers(listFrom(userData, "users"));
      setEvents(listFrom(eventData, "events"));
      setVenues(listFrom(venueData, "venues"));
      setSocieties(listFrom(societyData, "societies"));
    } catch (err) {
      setError(err.message || "Unable to load admin dashboard.");
    } finally {
      if (showLoader) setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    if (!token) {
      window.location.href = "/";
      return;
    }
    const role = String(sessionStorage.getItem("festify_role") || "").toUpperCase();
    if (!["ADMIN", "SUPER_ADMIN"].includes(role)) {
      window.location.href = "/";
      return;
    }
    refresh(true);
    const interval = window.setInterval(() => refresh(false), 30000);
    return () => window.clearInterval(interval);
  }, [token, refresh]);

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

  function openReview(type, item, action) {
    setReview({ type, item, action });
    setReviewReason("");
    setNotice("");
  }

  async function submitReview(event) {
    event.preventDefault();
    if (!review) return;

    const { type, item, action } = review;
    const id = type === "organizer" ? item.organizer_id : item.event_id;
    const base = type === "organizer"
      ? `/api/admin/organizers/${id}`
      : `/api/admin/events/${id}`;
    const endpoint = `${base}/${action}`;
    const body = action === "reject"
      ? { rejection_reason: reviewReason.trim() }
      : undefined;

    if (action === "reject" && !reviewReason.trim()) {
      setNotice("Please enter a reason for rejection.");
      return;
    }

    setBusyId(String(id));
    setNotice("");
    try {
      const result = await api(endpoint, {
        method: "PATCH",
        ...(body ? { body: JSON.stringify(body) } : {}),
      });
      setNotice(result.message || `${type === "organizer" ? "Organizer" : "Event"} ${action} action completed.`);
      setReview(null);
      await refresh(false);
    } catch (err) {
      setNotice(err.message || "The action could not be completed.");
    } finally {
      setBusyId(null);
    }
  }

  async function saveSociety(event) {
    event.preventDefault();
    setSavingSociety(true);
    setError("");
    setNotice("");
    try {
      const editing = Boolean(societyForm.society_id);
      const path = editing
        ? `/api/admin/societies/${societyForm.society_id}`
        : "/api/admin/societies";
      const payload = { ...societyForm };
      delete payload.society_id;
      delete payload.status;
      delete payload.date_created;
      delete payload.rejection_reason;
      const result = await api(path, {
        method: editing ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      setNotice(`${result.message || (editing ? "Society updated" : "Society created")}${result.society?.society_code ? ` — Code: ${result.society.society_code}` : ""}`);
      setSocietyForm(null);
      await refresh(true);
    } catch (err) {
      setError(err.message || "Unable to save society.");
    } finally {
      setSavingSociety(false);
    }
  }

  function openSocietyForm(society = null) {
    setError("");
    setNotice("");
    setSocietyForm(society ? { ...society } : {
      society_name: "",
      description: "",
      contact_email: "",
      contact_phone: "",
      society_code: "",
    });
  }

  async function updateVenue(event) {
    event.preventDefault();
    setSavingVenue(true);
    setNotice("");
    try {
      const editing = Boolean(venueForm.venue_id);
      const path = editing
        ? `/api/admin/venues/${venueForm.venue_id}`
        : "/api/admin/venues";
      const payload = {
        ...venueForm,
        capacity: Number(venueForm.capacity),
      };
      delete payload.venue_id;

      const result = await api(path, {
        method: editing ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      setNotice(result.message || "Venue saved successfully.");
      setVenueForm(null);
      await refresh(false);
    } catch (err) {
      setNotice(err.message || "Unable to save venue.");
    } finally {
      setSavingVenue(false);
    }
  }

  async function disableVenue(venue) {
    if (!window.confirm(`Deactivate "${venue.venue_name}"?`)) return;
    setBusyId(String(venue.venue_id));
    try {
      const result = await api(`/api/admin/venues/${venue.venue_id}/disable`, {
        method: "PATCH",
      });
      setNotice(result.message || "Venue deactivated.");
      await refresh(false);
    } catch (err) {
      setNotice(err.message || "Unable to deactivate venue.");
    } finally {
      setBusyId(null);
    }
  }

  const filteredOrganizers = organizers.filter((item) => {
    const linkedUser = users.find((u) => String(u.user_id) === String(item.user_id));
    const text = `${linkedUser?.name || ""} ${linkedUser?.email || ""} ${item.organizer_status || ""} ${item.society_id || ""}`;
    return text.toLowerCase().includes(search.toLowerCase());
  });

  const filteredEvents = events.filter((item) =>
    `${item.event_name || ""} ${item.category || ""} ${item.status || ""}`
      .toLowerCase().includes(search.toLowerCase())
  );

  const filteredVenues = venues.filter((item) =>
    `${item.venue_name || ""} ${item.location || ""} ${item.venue_status || ""}`
      .toLowerCase().includes(search.toLowerCase())
  );

  const pendingOrganizers = organizers.filter((o) => o.organizer_status === "PENDING").length;
  const pendingEvents = events.filter((e) => e.status === "PENDING").length;

  return (
    <div className="fest-dashboard admin-dashboard">
      <header className="fd-nav">
        <button className="intro-brand dashboard-home-brand" onClick={() => setPage("Overview")} aria-label="Festify home"><span className="brand-symbol">F</span>FESTIFY</button>
        <nav className="fd-links">
          {["Overview", "Organizers", "Events", "Venues", "Societies"].map((item) => (
            <button key={item} className={page === item ? "fd-active" : ""} onClick={() => { setPage(item); setSearch(""); window.setTimeout(() => document.querySelector(".fd-section-title")?.scrollIntoView({ behavior: "smooth", block: "start" }), 0); }}>
              {item}
            </button>
          ))}
        </nav>
        <div className="fd-profile-wrap" ref={profileRef}>
          <button className="fd-profile" onClick={() => setProfileOpen((v) => !v)}>
            <span className="fd-avatar">{(user.name || "A").charAt(0).toUpperCase()}</span>
            <span>{user.name || "Admin"}</span><span>⌄</span>
          </button>
          {profileOpen && <div className="fd-dropdown">
            <strong>{user.name || "Festify Admin"}</strong>
            <small>{user.email || "Administrator account"}</small>
            <button onClick={() => setPage("Overview")}>Admin overview</button>
            <button className="fd-logout" onClick={logout}>↗ Log out</button>
          </div>}
        </div>
      </header>

      <main className="fd-main">
        <section className="fd-hero">
          <div className="fd-hero-copy">
            <span className="fd-kicker">THE FESTIFY CONTROL ROOM</span>
            <h1>YOU RUN<br /><span>THE SHOW</span></h1>
            <p>Keep the campus buzzing. Review event requests, support organizers, and manage the spaces where memories happen.</p>
            <button className="fd-primary" onClick={() => { setPage("Events"); setSearch(""); }}>Review event lineup ↗</button>
          </div>
          <div className="fd-hero-art" aria-hidden="true"><span>✳</span><b>∞</b></div>
          <div className="fd-hero-foot"><span>FESTIFY / ADMIN CONTROL ROOM</span><span>KEEP THE GOOD TIMES ROLLING</span></div>
        </section>

        {notice && <div className="fd-notice" role="status"><span>{notice}</span><button onClick={() => setNotice("")}>×</button></div>}
        {error && <div className="fd-alert"><span>{error}</span><button onClick={() => refresh(true)}>Retry ↻</button></div>}

        {page === "Overview" && (
          <>
            <div className="fd-section-title">
              <div><span className="fd-kicker">THE BIG PICTURE</span><h2>FESTIFY AT A GLANCE</h2><p>Platform activity and approvals.</p></div>
              <button className="fd-secondary" onClick={() => refresh(true)}>Refresh now ↻</button>
            </div>
            {loading ? <div className="fd-empty"><div className="fd-spinner" /><h3>Loading your control room...</h3></div> : (
              <>
                <div className="fd-stats">
                  <Stat icon="♙" label="PARTICIPANTS" value={analytics.total_participants ?? 0} />
                  <Stat icon="✦" label="ORGANIZERS" value={analytics.total_organizers ?? 0} />
                  <Stat icon="▣" label="TOTAL EVENTS" value={analytics.total_events ?? events.length} />
                  <Stat icon="↗" label="REGISTRATIONS" value={analytics.total_registrations ?? 0} />
                  <Stat icon="♧" label="SOCIETIES" value={analytics.total_societies ?? 0} />
                  <Stat icon="◉" label="ATTENDANCE" value={analytics.total_attendance ?? 0} />
                  <Stat icon="★" label="AVERAGE RATING" value={`${analytics.average_rating ?? 0}/5`} />
                  <Stat icon="✉" label="FEEDBACK ENTRIES" value={analytics.total_feedback_count ?? 0} />
                </div>
                <section className="fd-panel fd-admin-feedback-panel">
                  <span className="fd-kicker">STUDENT EXPERIENCE</span><h3>Feedback by event</h3>
                  {Object.entries(analytics.feedback_by_event || {}).length ? Object.entries(analytics.feedback_by_event).map(([eventId, item]) => (
                    <div className="fd-event-feedback-item" key={eventId}>
                      <div><strong>{item.event_name}</strong><span>{item.feedback_count} responses · {item.average_rating}/5 average</span></div>
                      <div className="fd-event-rating-distribution">{[5,4,3,2,1].map((rating) => <span key={rating}>{rating}★ {item.rating_distribution?.[String(rating)] || 0}</span>)}</div>
                    </div>
                  )) : <p>No feedback has been submitted yet.</p>}
                </section>
                <div className="fd-overview-grid">
                  <section className="fd-panel"><span className="fd-kicker">NEEDS YOUR ATTENTION</span><h3>Approval queue</h3>
                    <button className="fd-queue-row" onClick={() => { setPage("Organizers"); setSearch("PENDING"); }}><span className="fd-queue-icon">♙</span><span><b>Organizer applications</b><small>Review new organizer profiles</small></span><strong>{pendingOrganizers}</strong></button>
                    <button className="fd-queue-row" onClick={() => { setPage("Events"); setSearch("PENDING"); }}><span className="fd-queue-icon pink">✦</span><span><b>Event submissions</b><small>Approve or reject event proposals</small></span><strong>{pendingEvents}</strong></button>
                  </section>
                  <section className="fd-panel"><span className="fd-kicker">EVENT STATUS</span><h3>What's happening</h3>
                    {["PENDING", "APPROVED", "PUBLISHED", "REJECTED", "COMPLETED"].map((status) => {
                      const count = Number(analytics.events_by_status?.[status] ?? events.filter((e) => e.status === status).length);
                      const total = Number(analytics.total_events ?? events.length);
                      return <div className="fd-status-line" key={status}><span>{status}</span><div><i style={{ width: `${total ? count / total * 100 : 0}%` }} /></div><b>{count}</b></div>;
                    })}
                  </section>
                </div>
              </>
            )}
          </>
        )}

        {page !== "Overview" && (
          <>
            <div className="fd-section-title">
              <div><span className="fd-kicker">ADMIN MANAGEMENT</span><h2>{page.toUpperCase()}</h2><p>Review and manage Festify platform records.</p></div>
              {page === "Venues" && <button className="fd-primary" onClick={() => setVenueForm({ venue_name: "", location: "", capacity: 100, venue_status: "ACTIVE", description: "" })}>＋ Add venue</button>}
              {page === "Societies" && <button className="fd-primary" onClick={() => openSocietyForm()}>＋ Add approved society</button>}
            </div>
            <div className="fd-toolbar"><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={`Search ${page.toLowerCase()}...`} /><button className="fd-secondary" onClick={() => refresh(true)}>Refresh ↻</button></div>

            {loading ? <div className="fd-empty"><div className="fd-spinner" /><h3>Loading records...</h3></div> :
              page === "Organizers" ? (
                filteredOrganizers.length === 0 ? <Empty title="No organizer profiles found." text="Organizer applications will appear here when submitted." /> :
                <div className="fd-table-wrap"><table className="fd-table"><thead><tr><th>Organizer</th><th>Society</th><th>Status</th><th>Applied</th><th>Actions</th></tr></thead><tbody>
                  {filteredOrganizers.map((o) => {
                    const linkedUser = users.find((u) => String(u.user_id) === String(o.user_id));
                    return <tr key={o.organizer_id}><td><b>{linkedUser?.name || `User #${o.user_id}`}</b><small>{linkedUser?.email || "Email unavailable"}</small></td><td>Society #{o.society_id}</td><td><Status value={o.organizer_status} /></td><td>{o.date_joined ? String(o.date_joined).slice(0, 10) : "—"}</td><td className="fd-actions">
                      {o.organizer_status === "PENDING" ? <>
                        <button className="fd-approve" disabled={busyId === String(o.organizer_id)} onClick={() => openReview("organizer", o, "approve")}>Approve</button>
                        <button className="fd-reject" disabled={busyId === String(o.organizer_id)} onClick={() => openReview("organizer", o, "reject")}>Reject</button>
                      </> : <span className="fd-muted">No pending action</span>}
                    </td></tr>;
                  })}
                </tbody></table></div>
              ) : page === "Events" ? (
                filteredEvents.length === 0 ? <Empty title="No events found." text="New event submissions will appear here for review." /> :
                <div className="fd-table-wrap"><table className="fd-table"><thead><tr><th>Event</th><th>Date</th><th>Venue</th><th>Status</th><th>Actions</th></tr></thead><tbody>
                  {filteredEvents.map((e) => <tr key={e.event_id}><td><b>{e.event_name}</b><small>{e.category || "Uncategorized"} · Organizer #{e.organizer_id}</small></td><td>{e.event_date || "—"}<small>{e.start_time || ""}{e.end_time ? ` – ${e.end_time}` : ""}</small></td><td>{venues.find((v) => String(v.venue_id) === String(e.venue_id))?.venue_name || (e.venue_id ? `Venue #${e.venue_id}` : "Not assigned")}</td><td><Status value={e.status} /></td><td className="fd-actions">
                    {e.status === "PENDING" ? <>
                      <button className="fd-approve" disabled={busyId === String(e.event_id)} onClick={() => openReview("event", e, "approve")}>Approve</button>
                      <button className="fd-reject" disabled={busyId === String(e.event_id)} onClick={() => openReview("event", e, "reject")}>Reject</button>
                    </> : e.rejection_reason ? <span className="fd-muted" title={e.rejection_reason}>Reason recorded</span> : <span className="fd-muted">No pending action</span>}
                  </td></tr>)}
                </tbody></table></div>
              ) : page === "Societies" ? (
                societies.filter((society) => `${society.society_name || ""} ${society.society_code || ""} ${society.status || ""}`.toLowerCase().includes(search.toLowerCase())).length === 0 ? <Empty title="No societies found." text="Add an approved society so organizers can register using its society code." action="＋ Add society" onAction={() => openSocietyForm()} /> :
                <div className="fd-table-wrap"><table className="fd-table"><thead><tr><th>Society</th><th>Society code</th><th>Society member contact</th><th>Status</th><th>Actions</th></tr></thead><tbody>{societies.filter((society) => `${society.society_name || ""} ${society.society_code || ""} ${society.status || ""}`.toLowerCase().includes(search.toLowerCase())).map((society) => <tr key={society.society_id}><td><b>{society.society_name}</b><small>{society.description || "—"}</small></td><td>{society.society_code || "—"}</td><td>{society.contact_email}<small>{society.contact_phone}</small></td><td><Status value={society.status} /></td><td className="fd-actions"><button className="fd-secondary" onClick={() => openSocietyForm(society)}>Edit society</button></td></tr>)}</tbody></table></div>
              ) : (
                filteredVenues.length === 0 ? <Empty title="No venues found." text="Add a venue to make it available for event creation." action="＋ Add your first venue" onAction={() => setVenueForm({ venue_name: "", location: "", capacity: 100, venue_status: "ACTIVE", description: "" })} /> :
                <div className="fd-venue-grid">{filteredVenues.map((v) => <article className="fd-venue-card" key={v.venue_id}><div className="fd-venue-icon">⌂</div><Status value={v.venue_status || "ACTIVE"} /><h3>{v.venue_name}</h3><p>⌖ {v.location || "Location not specified"}</p><p>♙ Capacity: {v.capacity}</p><small>{v.description || "A space for your next campus event."}</small><div className="fd-venue-actions"><button className="fd-secondary" onClick={() => setVenueForm({ ...v })}>Edit venue</button>{String(v.venue_status || "ACTIVE").toUpperCase() === "ACTIVE" && <button className="fd-reject" disabled={busyId === String(v.venue_id)} onClick={() => disableVenue(v)}>Deactivate</button>}</div></article>)}</div>
              )
            }
          </>
        )}

        <footer className="fd-footer"><span className="intro-brand dashboard-home-brand"><span className="brand-symbol">F</span>FESTIFY</span><span>YOUR FEST. YOUR STORY.</span><span>ADMIN CONTROL ROOM</span></footer>
      </main>

      {review && <div className="fd-modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setReview(null); }}>
        <form className="fd-modal" onSubmit={submitReview}>
          <div className="fd-modal-head"><div><span className="fd-kicker">ADMIN REVIEW</span><h2>{review.action === "approve" ? "APPROVE" : "REJECT"} {review.type.toUpperCase()}<span>.</span></h2></div><button type="button" onClick={() => setReview(null)}>×</button></div>
          <p className="fd-modal-description"><b>{review.item.event_name || `Organizer profile #${review.item.organizer_id}`}</b></p>
          {review.action === "approve" ? <p className="fd-modal-description">Confirm that you want to approve this {review.type}. Your backend currently does not persist approval remarks.</p> : <label>Reason for rejection *<textarea required rows="4" value={reviewReason} onChange={(e) => setReviewReason(e.target.value)} placeholder="Explain what needs to be changed..." /></label>}
          <div className="fd-modal-actions"><button type="button" className="fd-secondary" onClick={() => setReview(null)}>Cancel</button><button className={review.action === "approve" ? "fd-primary" : "fd-reject"} disabled={Boolean(busyId)}>{busyId ? "Saving..." : review.action === "approve" ? "Confirm approval" : "Confirm rejection"}</button></div>
        </form>
      </div>}

      {societyForm && <div className="fd-modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setSocietyForm(null); }}>
        <form className="fd-modal" onSubmit={saveSociety}>
          <div className="fd-modal-head"><div><span className="fd-kicker">SOCIETY MANAGEMENT</span><h2>{societyForm.society_id ? "EDIT SOCIETY" : "ADD SOCIETY"}<span>.</span></h2></div><button type="button" onClick={() => setSocietyForm(null)}>×</button></div>
          <p className="fd-modal-description">Enter the contact details of a society member, not the organizer. {societyForm.society_id ? "Saving changes will preserve the current approval status." : "New societies are saved with APPROVED status and can be used for organizer registration."}</p>
          <label>Society name *<input required maxLength="150" value={societyForm.society_name || ""} onChange={(e) => setSocietyForm({ ...societyForm, society_name: e.target.value })} /></label>
          <label>Description<textarea rows="3" maxLength="500" value={societyForm.description || ""} onChange={(e) => setSocietyForm({ ...societyForm, description: e.target.value })} /></label>
          <label>Society member contact email *<input required type="email" maxLength="150" value={societyForm.contact_email || ""} onChange={(e) => setSocietyForm({ ...societyForm, contact_email: e.target.value })} /></label>
          <label>Society member contact phone *<input required maxLength="15" value={societyForm.contact_phone || ""} onChange={(e) => setSocietyForm({ ...societyForm, contact_phone: e.target.value })} /></label>
          <label>Society code *<input required maxLength="30" pattern="[A-Za-z0-9_-]+" title="Use letters, numbers, hyphens or underscores only" value={societyForm.society_code || ""} onChange={(e) => setSocietyForm({ ...societyForm, society_code: e.target.value.toUpperCase() })} /></label>
          <div className="fd-modal-actions"><button type="button" className="fd-secondary" onClick={() => setSocietyForm(null)}>Cancel</button><button className="fd-primary" disabled={savingSociety}>{savingSociety ? "Saving..." : societyForm.society_id ? "Save changes ↗" : "Create approved society ↗"}</button></div>
        </form>
      </div>}

      {venueForm && <div className="fd-modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setVenueForm(null); }}>
        <form className="fd-modal" onSubmit={updateVenue}>
          <div className="fd-modal-head"><div><span className="fd-kicker">VENUE MANAGEMENT</span><h2>{venueForm.venue_id ? "EDIT VENUE" : "ADD VENUE"}<span>.</span></h2></div><button type="button" onClick={() => setVenueForm(null)}>×</button></div>
          <label>Venue name *<input required value={venueForm.venue_name} onChange={(e) => setVenueForm({ ...venueForm, venue_name: e.target.value })} /></label>
          <label>Location *<input required value={venueForm.location || ""} onChange={(e) => setVenueForm({ ...venueForm, location: e.target.value })} /></label>
          <label>Capacity *<input required min="1" type="number" value={venueForm.capacity} onChange={(e) => setVenueForm({ ...venueForm, capacity: e.target.value })} /></label>
          <label>Status<select value={venueForm.venue_status || "ACTIVE"} onChange={(e) => setVenueForm({ ...venueForm, venue_status: e.target.value })}><option value="ACTIVE">Active</option><option value="INACTIVE">Inactive</option></select></label>
          <label>Description<textarea rows="3" value={venueForm.description || ""} onChange={(e) => setVenueForm({ ...venueForm, description: e.target.value })} /></label>
          <div className="fd-modal-actions"><button type="button" className="fd-secondary" onClick={() => setVenueForm(null)}>Cancel</button><button className="fd-primary" disabled={savingVenue}>{savingVenue ? "Saving..." : "Save venue ↗"}</button></div>
        </form>
      </div>}
    </div>
  );
}

function Stat({ icon, label, value }) {
  return <div className="fd-stat"><span>{icon}</span><div><strong>{value}</strong><small>{label}</small></div></div>;
}
function Status({ value }) {
  const status = String(value || "UNKNOWN").toUpperCase();
  return <span className={`fd-status status-${status.toLowerCase()}`}>{status}</span>;
}
function Empty({ title, text, action, onAction }) {
  return <div className="fd-empty"><span className="fd-empty-star">✳</span><h3>{title}</h3><p>{text}</p>{action && <button className="fd-primary" onClick={onAction}>{action}</button>}</div>;
}

export default AdminDashboard;