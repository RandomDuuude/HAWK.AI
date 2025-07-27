import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const CLOUD_FUNCTION_URL =
  "https://asia-south1-hawkai-467107.cloudfunctions.net/hawkai-handler"; // replace with your function endpoint

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  // Convert uploaded file to base64
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setImage(reader.result.split(",")[1]); // strip "data:image/...;base64,"
    };
    reader.readAsDataURL(file);
  };

  const sendMessage = async () => {
    if (!input.trim() && !image) return;

    const newMessages = [
      ...messages,
      { sender: "user", text: input || "[Image Uploaded]" },
    ];
    setMessages(newMessages);
    setInput("");
    setImage(null);
    setLoading(true);

    try {
      const body = { query: input };
      if (image) body.image = image; // send base64 image data

      const res = await fetch(CLOUD_FUNCTION_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      const botText =
        data.fulfillment_response?.messages?.[0]?.text?.text?.[0] ||
        "⚠️ No response";

      setMessages([...newMessages, { sender: "bot", text: botText }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { sender: "bot", text: `⚠️ Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.sender}`}>
            {m.sender === "bot" ? (
              <ReactMarkdown>{m.text}</ReactMarkdown>
            ) : (
              m.text
            )}
          </div>
        ))}
        {loading && <div className="message bot">...</div>}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
        />
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ marginRight: "0.5rem" }}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
