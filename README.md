# 📬 MailMind: AI-Powered Email Draft Assistant for Zoho Mail

**MailMind** is a Python-based tool that reads incoming emails from your Zoho Mail account and uses OpenAI’s GPT models to generate smart, contextual replies. It creates draft responses directly in your inbox so you can review and send with confidence.

---

## ✨ Features

* 🔐 Secure OAuth2-based Zoho Mail integration
* 📥 Automatically fetches unread emails
* 💡 Uses GPT-4o or GPT-4o-mini to generate contextual replies
* 📝 Saves replies as drafts — never sends without your review
* 🧠 Keeps the tone helpful, polite, and human-like
* 🔄 Marks emails as read after processing

---

## 📽️ Demo Video

[![Watch the demo](https://user-images.githubusercontent.com/122913805/276920425-1a7e6483-9a83-4930-80d5-9df1cf42c97e.png)](https://drive.google.com/file/d/1Q9-GtvmsatePwTXJL5ZsC1HopcrYq3zy/view?usp=sharing)

> 🔗 Click the image above to watch the demo video on **Google Drive**

---

## 📌 Use Cases

Perfect for:

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
* `python-dotenv` for config
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

```env
ZOHO_OAUTH_TOKEN=your_zoho_token
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4o-mini  # or gpt-4o
```

### 4. Run the replier

```bash
python main.py
```

---

## 🧪 Example Output

Once you run the script, you’ll find GPT-powered **draft replies** in Zoho Mail under the same thread as each unread message. Every draft is:

* Contextually aware
* Friendly and professional
* Ready for your review and manual send

---

## 🤖 How It Works

1. Authenticates with Zoho and retrieves unread messages
2. Extracts content, sender info, and subject
3. Passes it to the GPT model with tailored prompts
4. Creates a contextual draft reply in your inbox
5. Marks the email as read after processing

---

## 📷 Screenshots

*Coming soon – before/after examples of Zoho Mail draft replies*

---

## ✅ To-Do / Improvements

* [ ] Add UI for manual review
* [ ] Scheduled background tasks
* [ ] Gmail & Outlook support
* [ ] Style and tone customization

---

## 🧠 License

MIT – Use it freely, improve it as needed, and contribute back!

---
