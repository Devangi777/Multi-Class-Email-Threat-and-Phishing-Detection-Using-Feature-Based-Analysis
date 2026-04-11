let jwtToken = null;

async function getAuthToken() {
    if (jwtToken) return jwtToken;
    try {
        const response = await fetch("http://127.0.0.1:5000/auth", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: "aegis-extension-key-123" })
        });
        if (!response.ok) throw new Error("Auth failed");
        const data = await response.json();
        jwtToken = data.access_token;
        return jwtToken;
    } catch (e) {
        console.error("Auth Error:", e);
        return null;
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzePayload") {
        getAuthToken().then(token => {
            if (!token) {
                sendResponse({success: false, error: "Failed to authenticate with security gateway."});
                return;
            }
            
            fetch("http://127.0.0.1:5000/predict", {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: JSON.stringify(request.payload)
            })
            .then(res => {
                if (res.status === 401) { 
                    jwtToken = null; // Clear token on unauthorized access
                    throw new Error("HTTP error 401: Unauthorized");
                }
                if (!res.ok) throw new Error("HTTP error " + res.status);
                return res.json();
            })
            .then(data => sendResponse({success: true, data: data}))
            .catch(err => {
                console.error("Fetch Error:", err);
                sendResponse({success: false, error: err.toString()});
            });
        });
        return true; 
    }
});
