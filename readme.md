---
title: Multilingual AI Story & Poem Generator
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.36.1"
app_file: app.py
pinned: false
---

# 🌍 Multilingual AI Story & Poem Generator

An AI-powered creative writing tool built with **Google Gemini 1.5 Flash**, **Gradio**, and **gTTS**.  
It can generate short stories or poems in **20+ languages** with customizable genre, tone, and creativity level — plus voice narration and HTML export.

---

## ✨ Features

- **20+ Supported Languages** (English, Hindi, Telugu, Tamil, French, Spanish, Russian, Japanese, Arabic, and more).
- **Tone & Genre Control** — Fantasy, Thriller, Haiku, Sonnet, etc.
- **Voice Narration** — Uses `gTTS` to narrate in the selected language.
- **HTML Export** — Print-ready formatting for PDF creation.
- **Creativity Levels** — From structured storytelling to experimental outputs.
- **Outline Generator** — Get a plot or poem structure before generating full content.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Google Gemini API (`gemini-1.5-flash`)
- **Frontend:** Gradio Blocks UI
- **Audio:** Google Text-to-Speech (`gTTS`)
- **Deployment:** Hugging Face Spaces

---

## 🚀 Usage

1. Select:
   - **Content Type**: Story or Poem
   - **Genre**: Fantasy, Sci-Fi, etc.
   - **Language**
   - **Tone**
   - **Creativity Level**
2. Enter a **Theme** and **Characters**.
3. Click **Generate Story/Poem**.
4. Listen to the narration or download as HTML.
5. To save as PDF:
   - Open the downloaded HTML file in a browser.
   - Press `Ctrl+P` (or `Cmd+P` on Mac).
   - Change destination to **Save as PDF**.

---

## 📦 Installation (Local)

```bash
git clone https://github.com/ubaidshaik/ai-story-poem-generator.git
cd ai-story-poem-generator
pip install -r requirements.txt
export GOOGLE_API_KEY=your_api_key_here
python app.py
```

---

## 📜 License

MIT License.

---

## 🙏 Acknowledgements

Special thanks to **Saredufy Web Plus Academy Private Limited** for guidance and mentorship during development.
