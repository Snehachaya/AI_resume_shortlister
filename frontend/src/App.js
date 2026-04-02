import React, { useState } from "react";
import axios from "axios";

function App() {
  const [jd, setJd] = useState("");
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!jd || files.length === 0) {
      alert("Please add JD and resumes");
      return;
    }

    const formData = new FormData();
    formData.append("jd", jd);

    for (let file of files) {
      formData.append("resumes", file);
    }

    try {
      setLoading(true);
      const res = await axios.post("http://localhost:5000/upload", formData);
      setResults(res.data);
    } catch (err) {
      alert("Error connecting to server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      
      {/* MAIN CARD */}
      <div style={styles.card}>
        <h1 style={styles.title}>AI Resume Shortlister</h1>

        <label style={styles.label}>Job Description</label>
        <textarea
          style={styles.textarea}
          placeholder="Paste Job Description here..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />

        <label style={styles.label}>Upload Resumes</label>
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.zip"
          onChange={(e) => setFiles([...e.target.files])}
        />

        {/* ✨ Show Selected Files */}
        {files.length > 0 && (
          <div style={{ marginTop: "20px" }}>
            <h3>Selected Files:</h3>
            <ul>
              {files.map((file, index) => (
                <li key={index}>
                  📄 {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* BUTTON */}
        <button style={styles.button} onClick={handleSubmit}>
          {loading ? "Analyzing..." : "Analyze Resumes"}
        </button>
      </div>

      {/* RESULTS SECTION */}
      {results.length > 0 && (
        <div style={styles.resultCard}>
          <h2>Results</h2>
          {results.map((r, index) => (
            <div key={index} style={styles.resultItem}>
              <span>{r.name}</span>
              <span style={styles.score}>{r.score}%</span>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

export default App;

/* 🎨 STYLES */
const styles = {
  container: {
    minHeight: "100vh",
    background: "linear-gradient(to right, #667eea, #764ba2)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px",
    fontFamily: "Segoe UI",
  },
  card: {
    background: "#fff",
    padding: "30px",
    borderRadius: "12px",
    width: "400px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.2)",
    marginBottom: "20px",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
  },
  label: {
    fontWeight: "bold",
    marginTop: "10px",
    display: "block",
  },
  textarea: {
    width: "100%",
    height: "100px",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    marginTop: "5px",
  },
  button: {
    width: "100%",
    marginTop: "20px",
    padding: "12px",
    background: "#667eea",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    cursor: "pointer",
  },
  resultCard: {
    background: "#fff",
    padding: "20px",
    borderRadius: "12px",
    width: "400px",
    boxShadow: "0 8px 20px rgba(0,0,0,0.2)",
  },
  resultItem: {
    display: "flex",
    justifyContent: "space-between",
    padding: "10px 0",
    borderBottom: "1px solid #eee",
  },
  score: {
    fontWeight: "bold",
    color: "#667eea",
  },
};