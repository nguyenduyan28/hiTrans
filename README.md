# HiTrans - Translate Text in Google Docs

This is a small project I built to translate text in Google Docs using Google’s Gemini AI. It detects languages, translates highlighted text or the full doc—your call. You’ve already got `api.py` deployed on Render, so this guide focuses on getting the Apps Script part (`Code.gs` and `Sidebar.html`) deployed properly to work with your Render site.

## Basic Files

### 1. `api.py`
- **What it does**: The backend server that talks to Gemini AI for language detection and translation.
- **What’s inside**: 
  - Flask app with `/detect-language` and `/translate` endpoints.
  - Handles long text by splitting into chunks (max 10k chars).
  - Returns plain text, no JSON or markdown nonsense.
- **Where it’s at**: Already deployed on your Render site (e.g., `https://hitrans.onrender.com`).
- **Setup**: Done! Just make sure your Render URL is correct in `Code.gs`.

### 2. `Code.gs`
- **What it does**: The Google Apps Script that connects Docs to your Render API.
- **What’s inside**: 
  - Grabs text from Docs (highlighted or full, max 10k chars).
  - Sends requests to your Render API and gets plain text back.
  - Adds a “Text Tools” menu in Docs.
- **Where to put it**: In an Apps Script project tied to a Google Doc (you’ve run it once, now let’s deploy).
- **Deploy Steps** (since you’ve only run it):
  1. Open your Google Doc where you tested it.
  2. Go to **Extensions > Apps Script**.
  3. Paste or check `Code.gs` is there.
  4. Update the `url` in `translateText` to your Render site (e.g., `var url = 'https://hitrans.onrender.com/translate'`).
  5. Deploy it:
     - Click **Deploy > New Deployment**.
     - Pick **Type: Web App**.
     - Set **Execute as: Me** (your account).
     - Set **Who has access: Anyone** (or “Anyone with Google account” if you want tighter control).
     - Hit **Deploy**, copy the deployment URL (you won’t need it much, but keep it handy).
  6. Save and close.

### 3. `Sidebar.html`
- **What it does**: The sidebar UI in Docs for picking languages, models, styles, etc.
- **What’s inside**: 
  - Dropdowns for target language, Gemini model, style (academic, pro, casual).
  - Temperature slider, checkbox for full-doc translation.
  - Shows plain translated text.
- **Where to put it**: In the same Apps Script project as `Code.gs`.
- **Setup**:
  1. In the Apps Script editor, click **+** next to “Files” > **HTML** > name it `Sidebar.html`.
  2. Paste the `Sidebar.html` code in.
  3. Save it—deploy step above covers this too.

## How to Use It
Since your API’s on Render, here’s how to roll with the Apps Script:

1. Prep:
- Confirm  Render URL (e.g., `https://hitrans.onrender.com`) works. Test it with a POST request (e.g., via Postman) to `/translate` with:
  ```json
  {
    "text": "Hello",
    "source_lang": "en",
    "target_lang": "vi",
    "model": "gemini-2.0-flash"
  }
- Should return plain text like “Xin chào”.

- In Code.gs, ensure var url matches your Render URL.

2. Deploy Apps Script:
- Follow the deploy steps under Code.gs above.
- After deploying, reload your Google Doc (F5). You’ll see Text Tools in the menu.

3. Run It:
- Open any Google Doc (you might need to share the script—see below).
- Click Text Tools > Open Sidebar.
- Highlight text (e.g., “Reserving judgments is a matter of infinite hope”) or tick “Translate full document”.
- Pick a target language (e.g., “Vietnamese”), model (e.g., “gemini-2.0-flash”), style, hit Submit.
- Check “Text translated”—it’ll show plain text (e.g., “Việc giữ lại phán xét là vấn đề của hy vọng vô hạn”).

4. It has a video demo, use it for more demo information, check at [here](https://drive.google.com/file/d/1N7JF1LDjnbZevfphzon1fuNVWLtrhKvW/view?usp=sharing).

