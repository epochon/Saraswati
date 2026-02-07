function submitComplaint() {
  const text = document.getElementById("complaint").value;

  fetch("/submit", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({complaint: text})
  }).then(() => loadStats());
}

function loadStats() {
  fetch("/stats")
    .then(res => res.json())
    .then(data => {
      for (let key in data) {
        document.getElementById(key).innerText =
          document.getElementById(key).innerText.split(":")[0] + ": " + data[key];
      }
    });
}

loadStats();
