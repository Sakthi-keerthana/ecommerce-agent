document.getElementById("ask-form").addEventListener("submit", async function(e) {
  e.preventDefault();
  const question = document.getElementById("question").value;

  const responseArea = document.getElementById("response");
  responseArea.textContent = "Loading...";

  try {
    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    }); 

    const data = await res.json();
    responseArea.textContent = JSON.stringify(data.result, null, 2);
  } catch (err) {
    responseArea.textContent = "Error: " + err.message;
  }
});
