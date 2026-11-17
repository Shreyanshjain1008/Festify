
import { useEffect, useMemo, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

function UtkarshPage({ onBack, onLogin, onSignup }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });

    let cancelled = false;

    async function loadEvents() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/events/lineup`);
        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.success) {
          throw new Error(
            result.message || "Unable to load the event lineup."
          );
        }

        if (!cancelled) {
          setEvents(Array.isArray(result.events) ? result.events : []);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load events.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadEvents();

    return () => {
      cancelled = true;
    };
  }, []);

  const categories = useMemo(() => {
    const uniqueCategories = [
      ...new Set(
        events
          .map((event) => event.category?.trim())
          .filter(Boolean)
      ),
    ];

    return ["All", ...uniqueCategories.sort((a, b) => a.localeCompare(b))];
  }, [events]);

  const filteredEvents = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return events.filter((event) => {
      const matchesCategory =
        activeCategory === "All" || event.category === activeCategory;

      const searchableText = [
        event.event_name,
        event.category,
        event.description,
        event.venue_name,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return matchesCategory && searchableText.includes(query);
    });
  }, [events, searchTerm, activeCategory]);

  function formatDate(value) {
    if (!value) return "To be announced";

    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) return value;

    return date.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  function formatTime12(value) {
    if (!value) return "To be announced";

    const match = String(value)
      .trim()
      .match(/^(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)?$/i);

    if (!match) return String(value);

    let hour = Number(match[1]);
    const minute = match[2];
    const period = (
      match[3] || (hour >= 12 ? "PM" : "AM")
    ).toUpperCase();

    hour = hour % 12 || 12;

    return `${hour}:${minute} ${period}`;
  }

  function getRegistrationDeadline(event) {
    return (
      event.registration_deadline ||
      event.last_registration_date ||
      event.registration_last_date
    );
  }

  return (
    <main className="utkarsh-page">
      <div className="utkarsh-ribbon-field" aria-hidden="true">
        <span className="utkarsh-ribbon ribbon-one" />
        <span className="utkarsh-ribbon ribbon-two" />
        <span className="utkarsh-ribbon ribbon-three" />
        <span className="utkarsh-ribbon ribbon-four" />
        <span className="utkarsh-ribbon ribbon-five" />
        <span className="utkarsh-ribbon ribbon-six" />
        <span className="utkarsh-ribbon ribbon-seven" />
        <span className="utkarsh-ribbon ribbon-eight" />
      </div>
      <header className="utkarsh-header">
        <button
          type="button"
          className="utkarsh-back-button"
          onClick={onBack}
        >
          <span aria-hidden="true">←</span> Back to Festify
        </button>

        <button
          type="button"
          className="utkarsh-brand"
          onClick={onBack}
          aria-label="Festify home"
        >
          FESTIFY<span>.</span>
        </button>

        <button
          type="button"
          className="utkarsh-login-button"
          onClick={onLogin}
        >
          Login <span aria-hidden="true">↗</span>
        </button>
      </header>

      <section className="utkarsh-hero">
        <div className="utkarsh-hero-inner">
          <div className="utkarsh-hero-copy">
            <span className="utkarsh-kicker">
              UTKARSH · THE CULTURAL FEST OF ADGIPS
            </span>

            <h1>
              Find your
              <br />
              next <span>moment</span>
            </h1>

            <p>
              Discover competitions, showcase your talent, and be part
              of the experiences that make Utkarsh unforgettable.
            </p>

            <div className="utkarsh-actions">
              <button
                type="button"
                className="utkarsh-primary-action"
                onClick={() =>
                  document
                    .getElementById("utkarsh-lineup")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
              >
                EXPLORE COMPETITIONS <span aria-hidden="true">↓</span>
              </button>

              <button
                type="button"
                className="utkarsh-secondary-action"
                onClick={onSignup}
              >
                JOIN FESTIFY <span aria-hidden="true">↗</span>
              </button>
            </div>
          </div>

          <div className="utkarsh-hero-art" aria-hidden="true">
            <div className="utkarsh-art-orbit utkarsh-orbit-one" />
            <div className="utkarsh-art-orbit utkarsh-orbit-two" />
            <div className="utkarsh-art-center">
              <span>U</span>
            </div>
            <span className="utkarsh-art-star utkarsh-star-one">✳</span>
            <span className="utkarsh-art-star utkarsh-star-two">✦</span>
            <span className="utkarsh-art-caption">CREATE · COMPETE · CELEBRATE</span>
          </div>
        </div>

        <div className="utkarsh-hero-bottom">
          <span>YOUR CAMPUS. YOUR STAGE.</span>
          <a
            href="#utkarsh-lineup"
            onClick={(event) => {
              event.preventDefault();
              document
                .getElementById("utkarsh-lineup")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            DISCOVER THE LINEUP ↓
          </a>
        </div>
      </section>

      <section className="utkarsh-about">
        <div className="utkarsh-about-copy">
          <span className="utkarsh-eyebrow">MORE THAN A FEST</span>
          <h2>
            Where campus talent takes the <em>stage.</em>
          </h2>

          <p>
            Utkarsh is the flagship cultural fest of ADGIPS — a celebration
            of creativity, performance, student communities, and the energy
            that makes college life unforgettable. From stage performances
            and dance battles to literary, artistic, and team competitions,
            it brings students together to share their talent, discover
            new passions, and make memories across campus.
          </p>

          <p>
            Explore the approved lineup below, review each event's details,
            and sign in to register. Event-specific timings and venues will
            be shown when confirmed by the organizers.
          </p>
        </div>

        <div className="utkarsh-about-stats">
          <div>
            <span className="utkarsh-stat-icon">✳</span>
            <strong>Culture</strong>
            <span>Celebrate talent</span>
          </div>
          <div>
            <span className="utkarsh-stat-icon">◎</span>
            <strong>Community</strong>
            <span>Meet your people</span>
          </div>
          <div>
            <span className="utkarsh-stat-icon">✦</span>
            <strong>Competition</strong>
            <span>Show what you can do</span>
          </div>
        </div>
      </section>

      <section className="utkarsh-schedule">
        <div className="utkarsh-section-heading">
          <span className="utkarsh-eyebrow">YOUR FESTIVAL JOURNEY</span>
          <h2>
            Make every <em>moment count</em>
          </h2>
          <p>
            Find your event, bring your energy, and make the most of
            your festival experience.
          </p>
        </div>

        <div className="utkarsh-schedule-grid">
          <article>
            <span className="utkarsh-step-number">01</span>
            <div>
              <span className="utkarsh-step-label">STEP ONE</span>
              <h3>Discover</h3>
              <p>
                Browse the approved lineup and find competitions that
                match your interests.
              </p>
            </div>
          </article>

          <article>
            <span className="utkarsh-step-number">02</span>
            <div>
              <span className="utkarsh-step-label">STEP TWO</span>
              <h3>Take the stage</h3>
              <p>
                Sign in to register and get ready to showcase your
                skills and creativity.
              </p>
            </div>
          </article>

          <article>
            <span className="utkarsh-step-number">03</span>
            <div>
              <span className="utkarsh-step-label">STEP THREE</span>
              <h3>Make memories</h3>
              <p>
                Meet your community, cheer for your friends, and
                enjoy every campus moment.
              </p>
            </div>
          </article>
        </div>
      </section>

      <section className="utkarsh-lineup" id="utkarsh-lineup">
        <div className="utkarsh-lineup-top">
          <div className="utkarsh-section-heading">
            <span className="utkarsh-eyebrow">EXPLORE · DISCOVER · COMPETE</span>
            <h2>
              The event <em>lineup</em>
            </h2>
            <p>
              Find your competition. Your next big moment starts here.
            </p>
          </div>

          <div className="utkarsh-event-count">
            <strong>{filteredEvents.length.toString().padStart(2, "0")}</strong>
            <span>
              {filteredEvents.length === 1 ? "EVENT" : "EVENTS"}
              <br />
              FOUND
            </span>
          </div>
        </div>

        <div className="utkarsh-discovery-tools">
          <label className="utkarsh-search-box">
            <span className="utkarsh-search-icon" aria-hidden="true">
              ⌕
            </span>
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search competitions, categories, venues..."
              aria-label="Search events"
            />
            {searchTerm && (
              <button
                type="button"
                onClick={() => setSearchTerm("")}
                aria-label="Clear search"
              >
                ×
              </button>
            )}
          </label>

          <div
            className="utkarsh-category-filters"
            aria-label="Filter events by category"
          >
            {categories.map((category) => (
              <button
                type="button"
                key={category}
                className={
                  activeCategory === category ? "active" : ""
                }
                aria-pressed={activeCategory === category}
                onClick={() => setActiveCategory(category)}
              >
                {category === "All" ? "All events" : category}
              </button>
            ))}
          </div>
        </div>

        {loading && (
          <div className="utkarsh-state" role="status">
            <span className="utkarsh-loader" />
            <span>Discovering the event lineup...</span>
          </div>
        )}

        {!loading && error && (
          <div className="utkarsh-state utkarsh-error" role="alert">
            <strong>We couldn't load the lineup.</strong>
            <p>{error}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
            >
              Reload page ↻
            </button>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="utkarsh-state">
            <span className="utkarsh-empty-icon">✳</span>
            <strong>The lineup is taking shape.</strong>
            <p>
              No approved events are available yet. Check back soon!
            </p>
          </div>
        )}

        {!loading && !error && events.length > 0 &&
          filteredEvents.length === 0 && (
            <div className="utkarsh-state">
              <span className="utkarsh-empty-icon">⌕</span>
              <strong>No matching competitions.</strong>
              <p>Try another search term or select a different category.</p>
              <button
                type="button"
                onClick={() => {
                  setSearchTerm("");
                  setActiveCategory("All");
                }}
              >
                Clear all filters ↗
              </button>
            </div>
          )}

        {!loading && !error && filteredEvents.length > 0 && (
          <div className="utkarsh-event-grid">
            {filteredEvents.map((event, index) => (
              <article
                className="utkarsh-event-card"
                key={event.event_id}
              >
                <div className="utkarsh-event-visual">
                  {event.event_image ? (
                    <img
                      className="utkarsh-event-image"
                      src={event.event_image}
                      alt={event.event_name || "Festival event"}
                      loading="lazy"
                    />
                  ) : (
                    <div
                      className="utkarsh-event-image-fallback"
                      aria-hidden="true"
                    >
                      <span>EVENT</span>
                      <strong>{String(index + 1).padStart(2, "0")}</strong>
                      <i>✳</i>
                    </div>
                  )}

                  <span className="utkarsh-card-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>

                <div className="utkarsh-event-content">
                  <div className="utkarsh-event-card-top">
                    <span className="utkarsh-event-category">
                      {event.category || "CAMPUS EVENT"}
                    </span>
                    <span className="utkarsh-event-mark" aria-hidden="true">
                      ↗
                    </span>
                  </div>

                  <h3>{event.event_name || "Untitled event"}</h3>

                  <p className="utkarsh-event-description">
                    {event.description ||
                      "Get ready to participate, showcase your talent, and make your mark at Utkarsh."}
                  </p>

                  <div className="utkarsh-event-meta">
                    <div>
                      <span className="utkarsh-meta-icon" aria-hidden="true">
                        ◷
                      </span>
                      <span>
                        <strong>DATE & TIME</strong>
                        <span>{formatDate(event.event_date)}</span>
                        <span>{formatTime12(event.start_time)}</span>
                      </span>
                    </div>

                    <div>
                      <span className="utkarsh-meta-icon" aria-hidden="true">
                        ⌖
                      </span>
                      <span>
                        <strong>VENUE</strong>
                        <span>{event.venue_name || "To be announced"}</span>
                      </span>
                    </div>
                  </div>

                  <details className="utkarsh-event-details">
                    <summary>
                      Rules & eligibility <span aria-hidden="true">＋</span>
                    </summary>
                    <div>
                      <strong>Description</strong>
                      <p>
                        {event.description || "Details will be announced soon."}
                      </p>

                      <strong>Rules & regulations</strong>
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
                          "Check with the organizer for eligibility details."}
                      </p>

                      <strong>Registration deadline</strong>
                      <p>{formatDate(getRegistrationDeadline(event))}</p>

                      {event.end_time && (
                        <>
                          <strong>End time</strong>
                          <p>{formatTime12(event.end_time)}</p>
                        </>
                      )}
                    </div>
                  </details>

                  <div className="utkarsh-event-card-footer">
                    <span>
                      <span className="utkarsh-status-dot" />
                      LINEUP APPROVED
                    </span>
                    <button
                      type="button"
                      onClick={onLogin}
                      aria-label={`Login to register for ${event.event_name}`}
                    >
                      Register <span aria-hidden="true">↗</span>
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}

        {!loading && !error && events.length > 0 && (
          <p className="utkarsh-login-hint">
            <span aria-hidden="true">✦</span>
            Ready to participate? Sign in to register for your favourite
            events and access your QR pass.
            <button type="button" onClick={onLogin}>
              Login to continue ↗
            </button>
          </p>
        )}
      </section>

      <section className="utkarsh-closing">
        <span className="utkarsh-eyebrow">THE STAGE IS YOURS</span>
        <h2>
          Your moment.
          <br />
          Your <em>Utkarsh.</em>
        </h2>
        <p>Join the community. Discover what you're capable of.</p>
        <button type="button" onClick={onSignup}>
          CREATE YOUR ACCOUNT ↗
        </button>
      </section>

      <footer className="utkarsh-footer">
        <button
          className="intro-brand dashboard-home-brand"
          onClick={() => showPage("Explore Events")}
          aria-label="Festify home"
        >
          <span className="brand-symbol">F</span>
          FESTIFY
        </button>
        <span>
          © {new Date().getFullYear()} FESTIFY · MADE FOR CAMPUS MOMENTS ✦
        </span>
        <button type="button" onClick={onLogin}>
          STUDENT LOGIN ↗
        </button>
      </footer>
    </main>
  );
}

export default UtkarshPage;
