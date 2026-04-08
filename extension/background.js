chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzePayload") {
        fetch("http://127.0.0.1:5000/predict", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request.payload)
        })
        .then(res => {
            if (!res.ok) throw new Error("HTTP error " + res.status);
            return res.json();
        })
        .then(data => sendResponse({success: true, data: data}))
        .catch(err => {
            console.error("Fetch Error:", err);
            sendResponse({success: false, error: err.toString()});
        });
        
        return true; // Keep the message channel open for async fetch
    }
});
