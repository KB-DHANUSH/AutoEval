import { useState } from "react";
import "../brutalist.css";
import logo from "../assets/logo.png";
import { Link } from "react-router-dom";
function LandingPage() {
  const [email, setEmail] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeAccordion, setActiveAccordion] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Subscribed with: ${email}`);
    setEmail("");
  };

  const toggleAccordion = (index) => {
    setActiveAccordion(activeAccordion === index ? null : index);
  };

  const faqItems = [
    {
      question: "WHAT IS INKGRADER?",
      answer:
        "InkGrader is an AI-powered web app that reads and evaluates handwritten or typed papers using OCR and agentic AI—delivering fast, fair, and context-aware corrections.",
    },
    {
      question: "HOW DOES INKGRADER WORK?",
      answer:
        "Upload a photo or scan of a paper. Our OCR reads the content. Agentic AI evaluates grammar, logic, and structure—then generates instant corrections and feedback.",
    },
    {
      question: "WHAT TYPES OF PAPERS CAN IT GRADE?",
      answer:
        "Essays, short answers, handwritten reports, and typed documents. If it's readable, InkGrader can process it.",
    },
    {
      question: "IS INKGRADER ACCURATE?",
      answer:
        "Brutally. Our OCR is tuned for messy handwriting. The AI doesn’t just check spelling—it understands context and meaning.",
    },
    {
      question: "DO I NEED TO INSTALL ANYTHING?",
      answer:
        "Nope. InkGrader runs in your browser. No downloads. No dependencies. Just upload and grade.",
    },
    {
      question: "IS MY DATA SAFE?",
      answer:
        "Yes. Uploaded papers are encrypted in transit and deleted after processing. No lingering traces. No data mining.",
    },
  ];

  return (
    <div className="brutal-container">
      <header className="brutal-header">
        <div className="brutal-logo flex flex-row items-center justify-center gap-3">
          <img src={logo} width="50" height="auto"/>
          <div><span className="accent mt-2">Ink</span>Grader</div>
        </div>

        <button
          className="brutal-menu-button"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? "X" : "☰"}
        </button>

        <nav className={`brutal-nav ${menuOpen ? "open" : ""}`}>
          <ul>
            <li>
              <a href="#features">FEATURES</a>
            </li>
            <li>
              <a href="#faq">FAQ</a>
            </li>
            <li>
              <a href="#about">ABOUT</a>
            </li>
            <li>
             <Link to="/login"><button className="brutal-button login">LOGIN</button></Link>
            </li>
          </ul>
        </nav>
      </header>

      <main>
        <section className="brutal-hero">
          <div className="brutal-hero-content">
            <h1>
              EMBRACE THE <span className="glitch">INK</span>
            </h1>
            <h2>OCR + Agentic AI PAPER CORRECTION</h2>
            <p>
              No more manual marking. InkGrader reads every scribble, applies
              AI‑driven corrections, and spits out clear feedback—fast and
              fearless.
            </p>

            <div className="brutal-cta">
              <button className="brutal-button primary"><Link to="/login">GET STARTED </Link></button>
              <a href= "#about"><button className="brutal-button">LEARN MORE</button></a>
            </div>
          </div>
          <div className="brutal-hero-image">
            <div className="brutal-box hidden sm:block"></div>
            <div className="brutal-box accent hidden sm:block"></div>
            <div className="brutal-box dark hidden sm:block"></div>
          </div>
        </section>

        <section id="features" className="brutal-section">
          <h2 className="brutal-section-title">FEATURES</h2>
          <div className="brutal-grid">
            <div className="brutal-card">
              <h3>PRECISION OCR</h3>
              <p>Decipher every scribble with laser‑sharp accuracy.</p>
            </div>
            <div className="brutal-card accent">
              <h3>AGENTIC AI</h3>
              <p>
                Autonomous AI that reads, understands, and corrects
                contextually.
              </p>
            </div>
            <div className="brutal-card dark">
              <h3>INSTANT FEEDBACK</h3>
              <p>Receive corrections and comments the moment you upload.</p>
            </div>
            <div className="brutal-card">
              <h3>ACTIONABLE REPORTS</h3>
              <p>
                No‑fluff summaries highlighting strengths, weaknesses, and next
                steps.
              </p>
            </div>
            <div className="brutal-card accent">
              <h3>ZERO BIAS</h3>
              <p>
                Every paper judged by logic, not mood. Consistent. Fair.
                Unapologetic.
              </p>
            </div>
            <div className="brutal-card dark">
              <h3>NO-NONSENSE UI</h3>
              <p>
                Clean. Direct. Everything you need—nothing you don't. Built for
                speed and clarity.
              </p>
            </div>
          </div>
        </section>

        <section id="faq" className="brutal-section alt">
          <h2 className="brutal-section-title">FREQUENTLY ASKED QUESTIONS</h2>
          <div className="brutal-accordion">
            {faqItems.map((faq, index) => (
              <div
                key={index}
                className={`brutal-accordion-item ${
                  activeAccordion === index ? "active" : ""
                }`}
              >
                <button
                  className="brutal-accordion-header"
                  onClick={() => toggleAccordion(index)}
                >
                  <span>{faq.question}</span>
                  <span className="brutal-accordion-icon">
                    {activeAccordion === index ? "−" : "+"}
                  </span>
                </button>
                <div className="brutal-accordion-content">
                  <p>{faq.answer}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section id="about" className="brutal-section">
          <h2 className="brutal-section-title">MANIFESTO</h2>
          <div className="brutal-manifesto">
            <p className="brutal-large-text">
              We reject vague grades, biased marking, and slow feedback loops.
            </p>
            <p className="brutal-large-text">
              We embrace clarity, speed, and brutal honesty—powered by machines
              that never sleep.
            </p>
            <p className="brutal-large-text">
              Every mark should mean something. Every correction should teach.
            </p>
            <p className="brutal-large-text">This is the INKGRADER way.</p>
          </div>
        </section>

        <section className="brutal-section alt brutal-community">
          <h2 className="brutal-section-title">JOIN THE MOVEMENT</h2>
          <div className="brutal-community-content">
            <p className="brutal-medium-text">
              Connect with the developers who are rewriting the rules of
              grading— one paper at a time.
            </p>
            <div className="brutal-social-buttons">
              <button className="brutal-social-button">DISCORD</button>
              <button className="brutal-social-button">GITHUB</button>
              <button className="brutal-social-button">TWITTER</button>
            </div>
          </div>
        </section>
      </main>

      <footer className="brutal-footer">
        <div className="brutal-footer-content">
          <div className="brutal-logo">
            <span className="accent">Ink</span>Grader
          </div>
          <div className="brutal-footer-links">
            <div className="brutal-footer-column">
              <h4>SITE MAP</h4>
              <ul>
                <li>
                  <a href="#features">Features</a>
                </li>
                <li>
                  <a href="#faq">FAQ</a>
                </li>
                <li>
                  <a href="#about">About</a>
                </li>
                <li>
                  <a href="#">Community</a>
                </li>
              </ul>
            </div>
            <div className="brutal-footer-column">
              <h4>LEGAL</h4>
              <ul>
                <li>
                  <a href="#">Privacy</a>
                </li>
                <li>
                  <a href="#">Terms</a>
                </li>
                <li>
                  <a href="#">Cookies</a>
                </li>
              </ul>
            </div>
            <div className="brutal-footer-column">
              <h4>SOCIAL</h4>
              <ul>
                <li>
                  <a href="#">Twitter</a>
                </li>
                <li>
                  <a href="#">GitHub</a>
                </li>
                <li>
                  <a href="#">Discord</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="brutal-copyright">
          © 2025 INKGRADER. ALL RIGHTS RESERVED.
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;

// Now create a new file src/BrutalUI.css with these styles:
