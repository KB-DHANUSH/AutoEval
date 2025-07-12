import React, { useState } from "react";
import {
  Loader2,
  Upload,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import "./App.css";
import logo from "./assets/logo.png";

const App = () => {
  const [formData, setFormData] = useState({
    question: "",
    marks: 10,
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError("");
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile || !formData.question) {
      setError("Please fill in all fields and select an image");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const apiUrl = import.meta.env.VITE_BACKEND_URL+"/ocr/demo";
      const formDataToSend = new FormData();

      formDataToSend.append("image", selectedFile);
      formDataToSend.append("question", formData.question);
      formDataToSend.append("marks", formData.marks);

      const response = await fetch(apiUrl, {
        method: "POST",
        body: formDataToSend,
      });

      if (!response.ok) {
        const errorResponse = await response.json();
        throw new Error(errorResponse.error || "Error evaluating the answer");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="brutal-container">
      <div className="brutal-content">
        <header className="brutal-header">
          <div className="brutal-logo">
            <img src={logo} width="50" height="auto" alt="InkGrader Logo" />
            <h1>
              INK<span className="accent">GRADER</span>
            </h1>
          </div>
          <p className="brutal-tagline">INTELLIGENT ANSWER ASSESSMENT SYSTEM</p>
        </header>
        <main className="brutal-card">
          <h2 className="brutal-card-title">ASSESSMENT DETAILS</h2>
          <div className="brutal-form">
            <div className="brutal-form-group">
              <label className="brutal-label">QUESTION</label>
              <textarea
                name="question"
                value={formData.question}
                onChange={handleInputChange}
                className="brutal-input brutal-textarea"
                placeholder="ENTER THE QUESTION HERE..."
              />
            </div>
            <div className="brutal-form-group">
              <label className="brutal-label">MAXIMUM MARKS</label>
              <input
                type="number"
                name="marks"
                value={formData.marks}
                onChange={handleInputChange}
                min="0"
                step="0.5"
                className="brutal-input"
              />
            </div>
            <div className="brutal-form-group">
              <label className="brutal-label">STUDENT ANSWER</label>
              <div className="brutal-file-upload">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept="image/*"
                  className="brutal-file-input"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="brutal-file-label">
                  {selectedFile ? (
                    <div className="brutal-file-selected">
                      <CheckCircle className="brutal-icon-small" />
                      <span>{selectedFile.name}</span>
                    </div>
                  ) : (
                    <div className="brutal-file-prompt">
                      <Upload className="brutal-icon" />
                      <div>
                        <span className="brutal-highlight">
                          CLICK TO UPLOAD
                        </span>{" "}
                        OR DRAG AND DROP
                      </div>
                      <p>PNG, JPG UP TO 10MB</p>
                    </div>
                  )}
                </label>
              </div>
            </div>
            {error && (
              <div className="brutal-error">
                <AlertCircle className="brutal-icon-small" />
                <p>{error}</p>
              </div>
            )}
            <button
              className="brutal-button primary full-width"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="brutal-spinner" />
                  EVALUATING...
                </>
              ) : (
                "EVALUATE ANSWER"
              )}
            </button>

            {/* Results Display */}
            {result && (
              <div className="brutal-result">
                <h3 className="brutal-result-title">EVALUATION RESULTS</h3>
                <div className="brutal-result-content">
                  <div className="brutal-result-item">
                    <p className="brutal-result-label">SCORE:</p>
                    <p className="brutal-result-score">
                      {result.grading_result.total_marks} / {formData.marks}
                    </p>
                  </div>
                  <div className="brutal-result-item">
                    <p className="brutal-result-label">STATUS:</p>
                    <p className="brutal-result-text">{result.message}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>

        <footer className="brutal-footer">
          <p>© 2025 INKGRADER. ALL RIGHTS RESERVED.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;