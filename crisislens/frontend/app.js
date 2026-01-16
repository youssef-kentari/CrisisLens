const form = document.getElementById("analyze-form");
const imageInput = document.getElementById("image-input");
const textInput = document.getElementById("text-input");
const statusBadge = document.getElementById("status");
const resultOutput = document.getElementById("result-output");

const setStatus = (message, type = "idle") => {
  statusBadge.textContent = message;
  statusBadge.className = `status status-${type}`;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!imageInput.files.length) {
    setStatus("Please upload an image.", "error");
    return;
  }

  setStatus("Analyzing...", "loading");
  resultOutput.textContent = "Analyzing crisis context with Gemini 3...";

  const formData = new FormData();
  formData.append("image", imageInput.files[0]);
  formData.append("text", textInput.value.trim());

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Analysis failed");
    }

    const data = await response.json();
    resultOutput.textContent = JSON.stringify(data, null, 2);
    setStatus("Analysis ready", "success");
  } catch (error) {
    resultOutput.textContent = `Error: ${error.message}`;
    setStatus("Error", "error");
  }
});
