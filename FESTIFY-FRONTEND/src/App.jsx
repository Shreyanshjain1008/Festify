import { useEffect, useRef, useState } from "react";
import "./App.css";
import Signup from "./Signup";
import Login from "./Login";
import OrganizerDashboard from "./OrganizerDashboard";
import AdminDashboard from "./AdminDashboard";
import StudentDashboard from "./StudentDashboard";
import UtkarshPage from "./UtkarshPage";

const events = [
  {
    number: "01",
    category: "CULTURE",
    title: "Utkarsh",
    description:
      "Step into the spirit of campus life with Utkarsh. Discover cultural showcases, exciting competitions, student talent, and moments that bring the entire college together.",
    date: "EXPLORE THE LINEUP",
    symbol: "✦",
    image:
      "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?auto=format&fit=crop&w=1000&q=85",
    color: "pink",
    action: "utkarsh",
  },
  {
    number: "02",
    category: "CULTURE",
    title: "Dandiya Nights",
    description:
      "Get ready for a night of rhythmic beats, colourful traditions, energetic dance, and festive spirit. Bring your friends and get ready to make the dance floor yours.",
    date: "COMING SOON",
    symbol: "✺",
    image:
      "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?auto=format&fit=crop&w=1000&q=85",
    color: "orange",
    action: "coming-soon",
  },
  {
    number: "03",
    category: "TECHNOLOGY",
    title: "Tech Fest",
    description:
      "For curious minds and ambitious creators. Get ready for technology challenges, problem-solving, fresh ideas, and opportunities to turn imagination into innovation.",
    date: "COMING SOON",
    symbol: "⌘",
    image:
      "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1000&q=85",
    color: "blue",
    action: "coming-soon",
  },
];



const highlights = [
  { number: "06+", label: "Experience zones" },
  { number: "∞", label: "Ways to create" },
  { number: "✦", label: "Memories to keep" },
];

function App() {
  const audioRef = useRef(null);
  const introTimer = useRef(null);
  const [showSignup, setShowSignup] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [introVisible, setIntroVisible] = useState(true);
  const [introLeaving, setIntroLeaving] = useState(false);
  const [musicOn, setMusicOn] = useState(false);
  const [volume, setVolume] = useState(0.35);
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [scrolled, setScrolled] = useState(false);
  const currentPath = window.location.pathname;
  const [showUtkarshPage, setShowUtkarshPage] = useState(false);

  if (currentPath === "/student-dashboard") {
    return <StudentDashboard />;
  }

  if (currentPath === "/organizer-dashboard") {
    return <OrganizerDashboard />;
  }

  if (currentPath === "/admin-dashboard") {
    return <AdminDashboard />;
  }

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.volume = volume;

    const tryPlayMusic = async () => {
      try {
        await audio.play();
        setMusicOn(true);
      } catch {
        // Browsers may require a click before playing audio.
        setMusicOn(false);
      }
    };

    tryPlayMusic();

    const enableMusic = () => {
      if (audio.paused) {
        audio.play()
          .then(() => setMusicOn(true))
          .catch(() => setMusicOn(false));
      }
    };

    document.addEventListener("click", enableMusic, { once: true });

    return () => {
      document.removeEventListener("click", enableMusic);
    };
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 35);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    introTimer.current = window.setTimeout(() => {
      leaveIntro();
    }, 5200);

    return () => window.clearTimeout(introTimer.current);
  }, []);

  function leaveIntro() {
    if (introLeaving) return;

    window.clearTimeout(introTimer.current);
    setIntroLeaving(true);

    window.setTimeout(() => {
      setIntroVisible(false);
    }, 1100);
  }

  async function toggleMusic() {
    const audio = audioRef.current;
    if (!audio) return;

    if (musicOn) {
      audio.pause();
      setMusicOn(false);
      return;
    }

    try {
      await audio.play();
      setMusicOn(true);
    } catch {
      alert(
        "Music could not start. Add your audio file at public/music/festify-theme.mp3 and try again."
      );
    }
  }

  function playIntroMusic() {
    const audio = audioRef.current;
    if (!audio || musicOn) return;

    audio.volume = volume;

    audio
      .play()
      .then(() => setMusicOn(true))
      .catch(() => { });
  }

  function enterFestival() {
    playIntroMusic();
    leaveIntro();
  }

  function scrollTo(id) {
    setMenuOpen(false);

    document.getElementById(id)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  const categories = [
    "ALL",
    "CULTURE",
    "TECHNOLOGY",
  ];

  const filteredEvents = events.filter((event) => {
    const matchesCategory =
      activeFilter === "ALL" || event.category === activeFilter;

    const query = searchTerm.trim().toLowerCase();

    const matchesSearch =
      !query ||
      event.title.toLowerCase().includes(query) ||
      event.category.toLowerCase().includes(query) ||
      event.description.toLowerCase().includes(query);

    return matchesCategory && matchesSearch;
  });

  if (showLogin) {
    return (
      <Login
        onBack={() => setShowLogin(false)}
        onSignup={() => {
          setShowLogin(false);
          setShowSignup(true);
        }}
      />
    );
  }

  if (showSignup) {
    return (
      <Signup
        onBack={() => setShowSignup(false)}
        onLogin={() => {
          setShowSignup(false);
          setShowLogin(true);
        }}
      />
    );
  }

  if (showUtkarshPage) {
    return (
      <UtkarshPage
        onBack={() => setShowUtkarshPage(false)}
        onLogin={() => {
          setShowUtkarshPage(false);
          setShowLogin(true);
        }}
        onSignup={() => {
          setShowUtkarshPage(false);
          setShowSignup(true);
        }}
      />
    );
  }

  return (
    <div className="festify">
      <audio
        ref={audioRef}
        src="/music/festify-theme.mp3"
        loop
        preload="auto"
      />

      {/* CINEMATIC INTRO */}

      {introVisible && (
        <section
          className={`intro-screen ${introLeaving ? "intro-exit" : ""}`}
          aria-label="Festify introduction"
        >
          <div className="intro-background" />
          <div className="intro-character">
            <img
              src="https://www.invictusdtu.in/figure1.png"
              alt="Golden festival guardian"
            />
            <img
              className="intro-lotus"
              src="https://www.invictusdtu.in/lotus.svg"
              alt=""
            />
          </div>
          <div className="intro-grain" />
          <div className="intro-grid" />

          <div className="intro-top">
            <a className="intro-brand" href="#home">
              <span className="brand-symbol">F</span>
              FESTIFY
            </a>

            <span className="intro-edition">THE FESTIVAL EXPERIENCE</span>

            <button className="intro-skip" onClick={enterFestival}>
              SKIP INTRO <span>↗</span>
            </button>
          </div>

          <div className="intro-orbit orbit-outer">
            <span className="orbit-star">✦</span>
          </div>
          <div className="intro-orbit orbit-middle" />
          <div className="intro-orbit orbit-inner" />

          <div className="intro-light intro-light-one" />
          <div className="intro-light intro-light-two" />

          <div className="intro-center">
            <p className="intro-overline">
              <span /> A CAMPUS FULL OF POSSIBILITIES <span />
            </p>

            <div className="intro-logo">
              <span className="intro-logo-small">WELCOME TO</span>
              <h1>
                FEST<span>IFY</span>
                <i>✦</i>
              </h1>
              <p>WHERE EVERY MOMENT BECOMES A LEGACY.</p>
            </div>

            <div className="intro-enter">
              <button className="enter-button" onClick={enterFestival}>
                <span>ENTER THE EXPERIENCE</span>
                <span className="enter-arrow">↗</span>
              </button>
            </div>

            <p className="intro-hint">
              <span className="hint-dot" /> MUSIC, CULTURE, IDEAS & UNFORGETTABLE MOMENTS
            </p>
          </div>

          <div className="intro-bottom">
            <span>YOUR CAMPUS · YOUR MOMENT</span>
            <span className="intro-counter">FESTIFY</span>
            <span>YOUR CAMPUS. YOUR MOMENT.</span>
          </div>

          <div className="intro-progress">
            <span />
          </div>
        </section>
      )}

      {/* AMBIENT BACKGROUND */}

      <div className="ambient ambient-pink" />
      <div className="ambient ambient-blue" />
      <div className="grain" />

      {/* NAVIGATION */}

      <header className={`navbar ${scrolled ? "navbar-scrolled" : ""}`}>
        <a className="brand" href="#home" onClick={() => setMenuOpen(false)}>
          <span className="brand-mark">F</span>
          <span>
            FESTIFY
          </span>
        </a>

        <button
          className="mobile-menu"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
          aria-expanded={menuOpen}
        >
          {menuOpen ? "✕" : "☰"}
        </button>

        <nav className={`nav-links ${menuOpen ? "nav-open" : ""}`}>
          <a href="#home" onClick={() => setMenuOpen(false)}>
            <span>01</span> Home
          </a>
          <a href="#events" onClick={() => setMenuOpen(false)}>
            <span>02</span> Events
          </a>
          <a href="#experience" onClick={() => setMenuOpen(false)}>
            <span>03</span> Experience
          </a>
          <a href="#about" onClick={() => setMenuOpen(false)}>
            <span>04</span> About
          </a>
        </nav>

        <div className="nav-actions">
          <button
            className="login-button"
            onClick={() => setShowLogin(true)}
          >
            Log in
          </button>
          <button
            className="signup-button"
            onClick={() => setShowSignup(true)}
          >
            Join Festify <span>↗</span>
          </button>
        </div>
      </header>

      <main>
        {/* HERO */}

        <section className="hero" id="home">
          <div className="hero-image" />
          <div className="hero-shade" />

          <div className="hero-stars" aria-hidden="true">
            {Array.from({ length: 45 }, (_, i) => (
              <span
                key={i}
                className={`hero-star star-${(i % 4) + 1}`}
                style={{
                  left: `${(i * 37 + 11) % 100}%`,
                  top: `${(i * 23 + 7) % 90}%`,
                  animationDelay: `${(i % 8) * 0.35}s`,
                }}
              />
            ))}
          </div>

          <div className="hero-topline">
            <span>THE COLLEGE FEST YOU MAKE YOUR OWN</span>
            <span className="hero-location">YOUR CAMPUS · YOUR MOMENT</span>
          </div>

          <div className="hero-content">
            
            <div className="hero-badge">
              <span className="hero-badge-dot"></span>
              THE CAMPUS FESTIVAL EXPERIENCE
            </div>

            <div className="hero-copy">
              <p className="hero-kicker">
                CULTURE. IDEAS. COMMUNITY.
              </p>

              <h1 className="hero-title">
                <span>INFINITE</span>
                <span className="hero-title-accent">STORIES.</span>
              </h1>

              <div className="hero-divider"></div>

              <p className="hero-description">
                Where culture finds its voice, ideas take flight, and
                every moment becomes a memory worth keeping.
                One campus. Countless ways to make it yours.
              </p>

              <div className="hero-actions">
                <button
                  className="btn-primary"
                  onClick={() => {
                    document
                      .getElementById("events")
                      ?.scrollIntoView({ behavior: "smooth" });
                  }}
                >
                  DISCOVER THE FEST <span>↗</span>
                </button>

                <button
                  className="btn-secondary"
                  onClick={() => setShowSignup(true)}
                >
                  JOIN THE EXPERIENCE
                </button>
              </div>
            </div>

            <div className="hero-bottom">
              <span>CULTURE · TECHNOLOGY · COMMUNITY</span>
              <span>YOUR STORY STARTS HERE ↗</span>
            </div>
          </div>

          <div className="hero-side hero-side-left">
            <span className="side-line" />
            <span>WHERE TALENT MEETS POSSIBILITY</span>
          </div>

          <div className="hero-side hero-side-right">
            <span>FESTIFY / VOL. 01</span>
          </div>

          <div className="hero-bottom">
            <span>YOUR FESTIVAL STARTS HERE</span>
            <button
              className="scroll-indicator"
              onClick={() => scrollTo("marquee")}
              aria-label="Scroll down"
            >
              <span />
            </button>
            <span>DISCOVER YOUR NEXT STORY ✦</span>
          </div>

          
        </section>

        {/* MOVING TEXT */}

        <section className="marquee-section" id="marquee">
          <div className="marquee-track">
            {Array.from({ length: 4 }, (_, i) => (
              <div className="marquee-content" key={i}>
                <span>CELEBRATE TOGETHER</span>
                <i>✳</i>
                <span>DISCOVER YOUR PASSION</span>
                <i>✦</i>
                <span>CREATE YOUR LEGACY</span>
                <i>✧</i>
                <span>MAKE EVERY MOMENT COUNT</span>
                <i>✳</i>
              </div>
            ))}
          </div>
        </section>

        {/* ABOUT */}

        <section className="about-section section-pad" id="about">
          <div className="about-visual">
            <div className="about-image" />

            <div className="about-image-overlay">
              <span className="image-label">WHERE CAMPUS LIFE COMES ALIVE</span>
            </div>

            <div className="about-sticker">
              <span>NOT JUST A FEST</span>
              <strong>A PLACE TO BELONG.</strong>
              <i>✦</i>
            </div>

            <div className="about-corner about-corner-one" />
            <div className="about-corner about-corner-two" />
          </div>

          <div className="about-copy">
            <p className="section-eyebrow">
              <span>✳</span> MORE THAN A CELEBRATION
            </p>

            <h2>
              Ordinary
              <br />
              is <em>overrated.</em>
            </h2>

            <p className="about-description">
              Festify brings the best of college life together in one place.
              It is a space to discover your interests, showcase your talent,
              cheer for your friends, and meet people who see the world a
              little differently.
            </p>

            <p className="about-description">
              From cultural performances and creative showcases to technology
              challenges and campus competitions, every experience gives you
              a new reason to step out, participate, and create a story of
              your own.
            </p>

            <button
              className="text-link"
              onClick={() => scrollTo("experience")}
            >
              FIND YOUR KIND OF MAGIC <span>↗</span>
            </button>

            <div className="highlight-stats">
              {highlights.map((item) => (
                <div className="highlight-stat" key={item.label}>
                  <strong>{item.number}</strong>
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* EVENTS */}

        <section className="events-section section-pad" id="events">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">
                <span>✳</span> YOUR NEXT ADVENTURE AWAITS
              </p>
              <h2>
                Find your
                <br />
                <em>kind of chaos.</em>
              </h2>
            </div>

            <p className="section-intro">
              Whether you live for the spotlight, love solving a challenge,
              or just want to experience something new, there is a place for
              you here. Explore the lineup and find what excites you.
            </p>
          </div>

          <div className="event-tools">
            <div className="event-filters">
              {categories.map((category) => (
                <button
                  key={category}
                  className={activeFilter === category ? "filter-active" : ""}
                  onClick={() => setActiveFilter(category)}
                >
                  {category}
                </button>
              ))}
            </div>

            <label className="event-search">
              <span>⌕</span>
              <input
                type="search"
                placeholder="Find your event..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </label>
          </div>

          <div className="event-grid">
            {filteredEvents.map((event) => (
              <article
                className={`event-card event-${event.color}`}
                key={event.number}
              >
                <div className="event-image-wrap">
                  <img
                    className="event-image"
                    src={event.image}
                    alt={event.title}
                    loading="lazy"
                  />

                  <div className="event-image-shade" />

                  <div className="event-image-top">
                    <span>FESTIFY · EXPERIENCE</span>
                    <span className="event-symbol">{event.symbol}</span>
                  </div>

                  <span className="event-category">{event.category}</span>

                  <span className="event-image-arrow">↗</span>
                </div>

                <div className="event-info">
                  <div className="event-date">{event.date}</div>
                  <h3>{event.title}</h3>
                  <p>{event.description}</p>

                  <button
                    type="button"
                    className="event-discover"
                    disabled={event.action === "coming-soon"}
                    onClick={() => {
                      if (event.action === "utkarsh") {
                        setShowUtkarshPage(true);
                      }
                    }}
                  >
                    {event.action === "utkarsh" ? (
                      <>
                        VIEW EVENT LINEUP <span>↗</span>
                      </>
                    ) : (
                      <>COMING SOON</>
                    )}
                  </button>
                </div>
              </article>
            ))}
          </div>

          {filteredEvents.length === 0 && (
            <div className="empty-events">
              <span>✳</span>
              <h3>No events found.</h3>
              <p>
                We couldn't find a match this time. Try another keyword or
                explore all categories to find your next adventure.
              </p>
              <button
                onClick={() => {
                  setActiveFilter("ALL");
                  setSearchTerm("");
                }}
              >
                SHOW ALL EVENTS
              </button>
            </div>
          )}

          <div className="events-footer">
            <span>EVERY GREAT MEMORY STARTS WITH A YES.</span>
            <span>MORE EXPERIENCES COMING SOON ↗</span>
          </div>
        </section>

        {/* FEATURE STRIP */}

        <section className="experience-section" id="experience">
          <div className="experience-background" />

          <div className="experience-header">
            <p className="section-eyebrow">
              <span>✳</span> COUNTLESS POSSIBILITIES.
            </p>
            <h2>
              Come for the fest.
              <br />
              Stay for the <em>feeling.</em>
            </h2>
          </div>

          <div className="experience-grid">
            <article className="experience-card experience-music">
              <div className="experience-card-number">01</div>
              <div className="experience-card-symbol">♫</div>
              <div>
                <span>FEEL THE ENERGY</span>
                <h3>Turn it up.</h3>
                <p>
                  Let the music take over, celebrate live talent, and share
                  the kind of moments that become your favourite memories.
                </p>
              </div>
            </article>

            <article className="experience-card experience-ideas">
              <div className="experience-card-number">02</div>
              <div className="experience-card-symbol">⌘</div>
              <div>
                <span>THINK DIFFERENT</span>
                <h3>Make it happen.</h3>
                <p>
                  Put your ideas to the test, solve challenges with your
                  team, and discover what you can create when curiosity leads.
                </p>
              </div>
            </article>

            <article className="experience-card experience-people">
              <div className="experience-card-number">03</div>
              <div className="experience-card-symbol">✺</div>
              <div>
                <span>FIND YOUR PEOPLE</span>
                <h3>Make history.</h3>
                <p>
                  Meet new faces, celebrate different talents, and build
                  friendships that last beyond the final day of the fest.
                </p>
              </div>
            </article>
          </div>
        </section>

        {/* BIG CTA */}

        <section className="join-section" id="join">
          <div className="join-background" />
          <div className="join-grain" />

          <span className="join-top-label">
            YOUR INVITATION TO THE EXTRAORDINARY
          </span>

          <div className="join-content">
            <p className="section-eyebrow">
              <span>✳</span> YOUR CAMPUS. YOUR STAGE.
            </p>

            <h2>
              Don't just
              <br />
              hear about it
              <br />
              <em>Be there</em>
            </h2>

            <p>
              New experiences. People worth meeting. Stories
              worth telling. Sign up for Festify, explore the event lineup,
              and get ready to make your time on campus count.
            </p>

            <button
              className="primary-cta join-cta"
              onClick={() => setShowSignup(true)}
            >
              I'M IN. LET'S GO. <span>↗</span>
            </button>
          </div>

          <div className="join-big-letter">F</div>

          <div className="join-bottom">
            <span>GOOD THINGS HAPPEN OUTSIDE THE ORDINARY.</span>
            <span>FESTIFY © {new Date().getFullYear()}</span>
          </div>
        </section>
      </main>

      {/* FOOTER */}

      <footer className="footer">
        <div className="footer-main">
          <a className="brand footer-brand" href="#home">
            <span className="brand-mark">F</span>
            <span>
              FESTIFY
            </span>
          </a>

          <p className="footer-tagline">
            YOUR MOMENT.
            <br />
            MEMORIES THAT LAST.
          </p>

          <div className="footer-links">
            <a href="#home">Home</a>
            <a href="#events">Events</a>
            <a href="#experience">Experience</a>
            <a href="#about">About</a>
          </div>

          <button className="back-top" onClick={() => scrollTo("home")}>
            BACK TO TOP ↑
          </button>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} FESTIFY. ALL RIGHTS RESERVED.</span>
          <span>BUILT FOR THE NEXT GENERATION ✦</span>
        </div>
      </footer>

      {/* FLOATING SOUND CONTROL */}

      <div className="music-control">
        <button
          className="music-button"
          onClick={toggleMusic}
          aria-label={musicOn ? "Pause music" : "Play music"}
        >
          <span className={musicOn ? "music-bars playing" : "music-bars"}>
            <i />
            <i />
            <i />
            <i />
          </span>

          <span>{musicOn ? "SOUND ON" : "SOUND OFF"}</span>
          <span className="music-toggle">{musicOn ? "Ⅱ" : "▶"}</span>
        </button>

        <input
          aria-label="Music volume"
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={volume}
          onChange={(e) => setVolume(Number(e.target.value))}
          className="volume-slider"
        />
      </div>
    </div>
  );
}

export default App;