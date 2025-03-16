/* ===============================
   1) UI-based Document Analyzer
   =============================== */

// Document Upload
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("documentFile");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
    });
    const result = await response.json();
    document.getElementById("response").innerText = JSON.stringify(result, null, 2);
  } catch (error) {
    document.getElementById("response").innerText = `Error: ${error}`;
  }
});

// Legal Query (UI-based index)
document.getElementById("queryForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = document.getElementById("queryInput").value;
  
  const data = {
    query: query,
    context_documents: []
  };

  try {
    const response = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    document.getElementById("queryResponse").innerText = result.answer || JSON.stringify(result, null, 2);
  } catch (error) {
    document.getElementById("queryResponse").innerText = `Error: ${error}`;
  }
});

/* ===============================
   2) Case Law Analyzer
   =============================== */

// Ingest Case Law Data
document.getElementById("ingestCaselawButton").addEventListener("click", async () => {
  try {
    const response = await fetch("http://localhost:8000/ingest-caselaw", {
      method: "POST"
    });
    const result = await response.json();
    document.getElementById("ingestCaselawResponse").innerText = JSON.stringify(result, null, 2);
  } catch (error) {
    document.getElementById("ingestCaselawResponse").innerText = `Error: ${error}`;
  }
});

// Case Law Query
document.getElementById("caselawQueryButton").addEventListener("click", async () => {
  const query = document.getElementById("caselawQueryInput").value;
  const data = {
    query: query,
    size: 3
  };

  try {
    const response = await fetch("http://localhost:8000/query-caselaw", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    document.getElementById("caselawQueryResponse").innerText = result.answer || JSON.stringify(result, null, 2);
  } catch (error) {
    document.getElementById("caselawQueryResponse").innerText = `Error: ${error}`;
  }
});
