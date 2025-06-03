# 📬 MailMind: AI-Powered Email Draft Assistant for Zoho Mail

**MailMind** is a Python-based tool that reads incoming emails from your Zoho Mail account and uses OpenAI’s GPT models to generate smart, contextual replies. It creates draft responses directly in your inbox so you can review and send with confidence.

---

## ✨ Features

* 🔐 Secure OAuth2-based Zoho Mail integration
* 📥 Automatically fetches unread emails
* 💡 Uses GPT-4o or GPT-4o-mini to generate contextual replies
* 📝 Saves replies as drafts, never sends without your review
* 🧠 Keeps the tone helpful, polite, and human-like
* 🔄 Marks emails as read after processing

---

## 📌 Use Case

Great for:

* Virtual assistants and support teams
* Busy professionals needing smart auto-drafts
* Customer service inboxes
* Anyone looking to streamline routine email replies

---

## 🛠️ Tech Stack

* Python 3.9+
* [Zoho Mail API](https://www.zoho.com/mail/help/api/)
* OpenAI GPT API (`gpt-4o`, `gpt-4o-mini`)
* Requests + LangChain
* dotenv for config
* Logging for traceability

---

## 🚀 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/aimaster-dev/mailmind.git
cd mailmind
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the root directory:

```
ZOHO_OAUTH_TOKEN=your_zoho_token
OPENAI_API_KEY=your_openai_key
```

Optionally include:

```
MODEL_NAME=gpt-4o-mini  # or gpt-4o
```

### 4. Run the replier

```bash
python main.py
```

---

## 🧪 Example Output

After running, you’ll find draft responses in your Zoho Mail under the same thread as the incoming email. Drafts include polite, accurate responses based on the context of each message.

---

## 🤖 How It Works

1. Authenticates with Zoho and retrieves unread messages
2. Extracts the content and metadata
3. Passes it to the GPT model with tailored prompts
4. Creates a draft reply in your inbox
5. Optionally marks the message as read

---

## 📷 Screenshots

*(Add screenshots showing a before/after of email + draft reply in Zoho Mail)*

---

## ✅ To-Do / Improvements

* Add UI for manual review
* Scheduled background tasks
* Gmail & Outlook support
* Language style customization

---

## 🧠 License

MIT – Use it freely and improve it as needed.

---
