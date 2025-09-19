import { animate } from "./background.js";
animate();

// Welcome animation functionality
function initWelcomeAnimation() {
    const welcomeContainer = document.getElementById("welcomeAnimation");
    const welcomeText1 = "WEL";
    const welcomeText2 = "COME TO";
    const welcomeText3 = " WALLGRAPH";
    showWelcomeAnimation();
    
    function showWelcomeAnimation() {
        welcomeContainer.innerHTML = ""; // clear content
    
        const cursor = document.createElement("span");
        cursor.classList.add("typing-cursor");
        cursor.textContent = "|";
        welcomeContainer.appendChild(cursor);
    
        let i = 0;
        let typingspeed1= 350;
        let typingspeed2= 200;
        let typingspeed3= 120;
        const typingInterval1 = setInterval(() => {
            if (i < welcomeText1.length) {
                const char = welcomeText1[i] === " " ? "\u00A0" : welcomeText1[i]; 
                cursor.insertAdjacentHTML("beforebegin", `<span class="typed-char">${char}</span>`);
                i++;
            } else {
                clearInterval(typingInterval1);
                i=0;
                const typingInterval2 = setInterval(() => {
                    if (i < welcomeText2.length) {
                        const char = welcomeText2[i] === " " ? "\u00A0" : welcomeText2[i]; 
                        cursor.insertAdjacentHTML("beforebegin", `<span class="typed-char">${char}</span>`);
                        i++;
                    } else {
                        clearInterval(typingInterval2);
                        i=0;
                        const typingInterval3 = setInterval(() => {
                            if (i < welcomeText3.length) {
                                const char = welcomeText3[i] === " " ? "\u00A0" : welcomeText3[i]; 
                                cursor.insertAdjacentHTML("beforebegin", `<span class="typed-char">${char}</span>`);
                                i++;
                            } else {
                                clearInterval(typingInterval3);
                                cursor.classList.add("finished");
                            }
                        }, typingspeed3);
                    }
                }, typingspeed2);

            }
        }, typingspeed1);
        
        
        
    }
    
}

// Chat functionality
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatResponse = document.getElementById("chatResponse");

// Auto-resize textarea
function autoResize() {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 500) + 'px';
}

chatInput.addEventListener('input', autoResize);

// Mock AI response for testing
function getMockResponse(input) {
    return `Based on the analysis of stocks in the Communication Services sector, here are the key trading insights:
**TTD (The Trade Desk, Inc.) shows the strongest investment signals.**`;
}

async function getAIResponse(input) {
    try {
        const response = await fetch("http://localhost:8327/api/v1/agents/call_marketmind", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: input })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.agent_response || "No response from AI.";
    } catch (error) {
        console.error("Error fetching AI response:", error);
        return "⚠️ Error: Could not get a response from AI.";
    }
}

async function sendMessage() {
    const userInput = chatInput.value.trim();
    if (!userInput) return;

    autoResize();
    
    chatResponse.innerHTML = `
                <div class="typing-indicator">
                    <span class="typing-text">Thinking</span>
                    <div class="bullish-chart">
                        <div class="chart-line chart-vertical"></div>
                        <div class="chart-line chart-horizontal"></div>
                        <div class="chart-arrow"></div>
                        <div class="chart-dots">
                            <div class="chart-dot"></div>
                            <div class="chart-dot"></div>
                            <div class="chart-dot"></div>
                            <div class="chart-dot"></div>
                        </div>
                        
                    </div>
                </div>
            `;
    
    

    const aiResponse = await getAIResponse(userInput);
    chatResponse.innerHTML = marked.parse(aiResponse);
}

// Enter key (Ctrl+Enter or Shift+Enter for new line)
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendButton.addEventListener("click", sendMessage);

// Initialize welcome animation when page loads
document.addEventListener("DOMContentLoaded", initWelcomeAnimation);