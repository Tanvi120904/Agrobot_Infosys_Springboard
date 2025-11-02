document.addEventListener('DOMContentLoaded', () => {
  console.log('script loaded');
  const messages = document.getElementById('messages');
  const input = document.getElementById('msg');
  const sendBtn = document.getElementById('sendBtn');
  function addMessage(who, text) {
    const el = document.createElement('div');
    el.className = 'message ' + who;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    el.appendChild(bubble);
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }
  async function sendMessage() {
    const msg = input.value.trim();
    if (!msg) return;
    addMessage('user', msg);
    input.value = '';
    sendBtn.disabled = true;
    try {
      const res = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message: msg})});
      if (!res.ok) throw new Error('Network response not ok');
      const data = await res.json();
      addMessage('bot', data.response || 'No response');
    } catch (err) {
      console.error(err);
      addMessage('bot', 'Error connecting to server');
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }
  sendBtn && sendBtn.addEventListener('click', sendMessage);
  input && input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
});
// === Chatbot Frontend Engine ===

// Send text message
async function sendMessage(event) {
  event.preventDefault();
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  input.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    addMessage("bot", data.reply || "🤖 Sorry, no response received.");
  } catch (error) {
    console.error("Chat error:", error);
    addMessage("bot", "❌ Connection error. Please try again.");
  }
}

// Handle image upload click
document.addEventListener("DOMContentLoaded", function () {
  const imageBtn = document.getElementById("image-btn");
  const imageInput = document.getElementById("image-upload");

  imageBtn.addEventListener("click", () => {
    imageInput.click();
  });

  // When user selects image
  imageInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Preview uploaded image
    const imageURL = URL.createObjectURL(file);
    addMessage("user", "<em>📷 Uploaded image:</em>", imageURL);

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch("/api/image-analyze", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      const reply = data.label
        ? `<b>${data.label}</b><br>${data.advice}`
        : "⚠️ Could not analyze the image.";
      addMessage("bot", reply);
    } catch (error) {
      console.error("Image analyze error:", error);
      addMessage("bot", "❌ Image upload failed. Please retry.");
    }
  });
});

// Add message to chat
function addMessage(sender, text, imgURL = null) {
  const chatBox = document.getElementById("chat-box");
  const msg = document.createElement("div");
  msg.classList.add("msg", sender);
  msg.innerHTML = `<strong>${sender === "user" ? "You" : "AgriBot"}:</strong> ${text}`;

  // If image exists, show preview
  if (imgURL) {
    const img = document.createElement("img");
    img.src = imgURL;
    img.classList.add("chat-img");
    msg.appendChild(document.createElement("br"));
    msg.appendChild(img);
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}