import { useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const SAMPLE_JD =
  "We are hiring a Python backend developer to build AI-powered assessment applications. The candidate should have experience with FastAPI, React, REST API design, SQL, Git, Docker, machine learning, embeddings, scikit-learn, LangGraph, LLMs, and RAG. Strong communication and problem solving skills are required.";

function SkillList({ title, skills, emptyText, tone = "default" }) {
  return (
    <div className={`skill-panel ${tone}`}>
      <div className="panel-title">
        <h3>{title}</h3>
        <span>{skills.length}</span>
      </div>
      <div className="chips">
        {skills.length > 0 ? (
          skills.map((skill) => <span key={skill}>{skill}</span>)
        ) : (
          <p className="muted">{emptyText}</p>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value, helper }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{helper}</small>
    </article>
  );
}

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [answers, setAnswers] = useState({});
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const finalPlan = evaluation?.learning_plan || analysis?.learning_plan || [];

  const readinessLabel = useMemo(() => {
    if (!analysis) return "Ready for analysis";
    if (analysis.match_score >= 75) return "Strong fit";
    if (analysis.match_score >= 45) return "Developing fit";
    return "Early fit";
  }, [analysis]);

  const handleAnalyze = async () => {
    if (!resumeFile) {
      setError("Please upload a resume first.");
      return;
    }

    if (!jdFile && !jdText.trim()) {
      setError("Please upload or paste a job description.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setEvaluation(null);

      const formData = new FormData();
      formData.append("resume_file", resumeFile);
      formData.append("jd_text", jdText);

      if (jdFile) {
        formData.append("jd_file", jdFile);
      }

      const response = await axios.post(`${API_URL}/analyze-candidate`, formData);
      setAnalysis(response.data);

      const initialAnswers = {};
      response.data.questions.forEach((question) => {
        initialAnswers[question.skill] = "";
      });
      setAnswers(initialAnswers);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Analysis failed. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = () => {
    setJdText(SAMPLE_JD);
    setJdFile(null);
    setError("");
  };

  const handleAnswerChange = (skill, value) => {
    setAnswers((current) => ({
      ...current,
      [skill]: value,
    }));
  };

  const handleEvaluate = async () => {
    const filledAnswers = Object.fromEntries(
      Object.entries(answers).filter(([, answer]) => answer.trim())
    );

    if (Object.keys(filledAnswers).length === 0) {
      setError("Please answer at least one assessment question.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await axios.post(`${API_URL}/evaluate-assessment`, {
        answers: filledAnswers,
        missing_skills: analysis?.missing_skills || [],
      });

      setEvaluation(response.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Evaluation failed. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <h1>AI Skill Assessment Agent</h1>
          <p>
            Resume-to-role fit analysis, proficiency checks, and a personalized
            learning plan in one place.
          </p>
        </div>
        <div className="hero-verdict">
          <span>Candidate readiness</span>
          <strong>{readinessLabel}</strong>
        </div>
      </header>

      <section className="input-dashboard">
        <div className="input-card">
          <div className="section-heading">
            <span>1</span>
            <div>
              <h2>Candidate And Role</h2>
              <p>Upload a resume, then paste or upload the target job description.</p>
            </div>
          </div>

          <div className="file-grid">
            <label className="file-field">
              <span>Resume PDF/DOCX</span>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(event) => setResumeFile(event.target.files[0])}
              />
              <strong>{resumeFile?.name || "Choose resume"}</strong>
            </label>

            <label className="file-field">
              <span>Job description PDF/DOCX</span>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(event) => setJdFile(event.target.files[0])}
              />
              <strong>{jdFile?.name || "Optional upload"}</strong>
            </label>
          </div>

          <textarea
            value={jdText}
            onChange={(event) => setJdText(event.target.value)}
            placeholder="Paste the job description here if you are not uploading a JD file."
          />

          <div className="action-row">
            <button className="secondary-action" type="button" onClick={handleLoadSample}>
              Load Sample JD
            </button>
            <button className="primary-action" onClick={handleAnalyze} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Candidate"}
            </button>
          </div>

          {error && <p className="error">{error}</p>}
        </div>

        <div className="metrics-grid">
          <MetricCard
            label="Skill Match"
            value={analysis ? `${analysis.match_score}%` : "--"}
            helper="Required skills found in resume"
          />
          <MetricCard
            label="Semantic Fit"
            value={analysis ? `${analysis.semantic_similarity}%` : "--"}
            helper="Embedding similarity between JD and resume"
          />
          <MetricCard
            label="Assessment"
            value={evaluation ? `${evaluation.average_score}/5` : "--"}
            helper="Answer quality after proficiency check"
          />
          <MetricCard
            label="Skill Gaps"
            value={analysis ? analysis.missing_skills.length : "--"}
            helper="Priority areas to prepare"
          />
        </div>
      </section>

      {analysis && (
        <>
          <section className="skill-grid">
            <SkillList
              title="Required Skills"
              skills={analysis.required_skills}
              emptyText="No required skills detected"
            />
            <SkillList
              title="Candidate Skills"
              skills={analysis.candidate_skills}
              emptyText="No candidate skills detected"
            />
            <SkillList
              title="Matched Skills"
              skills={analysis.matched_skills}
              emptyText="No matches yet"
              tone="positive"
            />
            <SkillList
              title="Skill Gaps"
              skills={analysis.missing_skills}
              emptyText="No major gaps detected"
              tone="warning"
            />
          </section>

          <section className="assessment-section">
            <div className="section-heading">
              <span>2</span>
              <div>
                <h2>Skill Proficiency Check</h2>
                <p>Questions target the role gaps and matched strengths.</p>
              </div>
            </div>

            <div className="question-list">
              {analysis.questions.map((question) => (
                <div className="question-card" key={question.id}>
                  <div className="question-head">
                    <span>{question.skill}</span>
                    <small>{question.difficulty}</small>
                  </div>
                  <h3>{question.question}</h3>
                  <div className="answer-guide">
                    {(question.what_good_answer_covers || []).map((item) => (
                      <span key={item}>{item}</span>
                    ))}
                  </div>
                  <textarea
                    value={answers[question.skill] || ""}
                    onChange={(event) =>
                      handleAnswerChange(question.skill, event.target.value)
                    }
                    placeholder="Type the candidate answer here."
                  />
                </div>
              ))}
            </div>

            <button className="primary-action full-action" onClick={handleEvaluate} disabled={loading}>
              {loading ? "Scoring..." : "Score Answers"}
            </button>
          </section>
        </>
      )}

      {evaluation && (
        <section className="evaluation-section">
          <div className="section-heading">
            <span>3</span>
            <div>
              <h2>Assessment Result</h2>
              <p>Skill-level scoring with the next interview probe.</p>
            </div>
          </div>

          <div className="evaluation-grid">
            {evaluation.results.map((result) => (
              <article className="evaluation-card" key={result.skill}>
                <div>
                  <span>{result.skill}</span>
                  <strong>{result.score}/5</strong>
                </div>
                <p>{result.level}</p>
                <small>{result.feedback}</small>
                <em>{result.next_probe}</em>
              </article>
            ))}
          </div>
        </section>
      )}

      {finalPlan.length > 0 && (
        <section className="plan-section">
          <div className="section-heading">
            <span>4</span>
            <div>
              <h2>Personalized Learning Plan</h2>
              <p>Prioritized preparation steps tied to the candidate's gaps.</p>
            </div>
          </div>

          <div className="plan-list">
            {finalPlan.map((item) => (
              <article className="plan-card" key={`${item.week}-${item.skill}`}>
                <div className="plan-topline">
                  <span>{item.priority} Priority</span>
                  <strong>{item.time_estimate}</strong>
                </div>
                <h3>{item.skill}</h3>
                <p className="why-text">{item.why_it_matters}</p>
                <p>{item.goal}</p>
                <p className="mini-project">{item.mini_project}</p>
                <ul>
                  {item.resources.map((resource) => (
                    <li key={resource}>{resource}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
