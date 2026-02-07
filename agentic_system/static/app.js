async function submitComplaint() {
    const text = document.getElementById("complaint").value;
    const resultDiv = document.getElementById("result");

    if (!text.trim()) {
        resultDiv.innerHTML = `<div class="error">⚠️ Please enter a complaint.</div>`;
        return;
    }

    resultDiv.innerHTML = "⏳ Submitting complaint...";

    const response = await fetch("/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction: text })
    });

    const data = await response.json();

    if (data.status === "SUBMITTED") {
        resultDiv.innerHTML = `
            <div class="success">
                <span class="tick">✔️</span>
                Complaint submitted successfully
            </div>
        `;
    } else if (data.status === "NEEDS_MORE_INFO") {
        resultDiv.innerHTML = `
            <div class="error">⚠️ ${data.message}</div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="error">❌ Something went wrong</div>
        `;
    }
}
