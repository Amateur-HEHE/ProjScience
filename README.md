# 🖐️ GestureSpeak — Real-Time Hand Gesture Recognition

A single-page, dark-themed Streamlit app that detects hand gestures live
from your webcam, overlays the hand skeleton, shows the gesture name on
screen, and speaks it out loud.

**Tech stack:** Python · OpenCV · MediaPipe (Tasks API) · Streamlit · streamlit-webrtc

---

## 📁 Project Structure

```
gesture_app/
├── app.py                 # The entire app (single page, no sidebar)
├── gesture_utils.py        # MediaPipe hand tracking + gesture classification rules
├── style_utils.py          # Dark theme CSS (sidebar hidden)
├── local_desktop_app.py     # Optional: plain OpenCV window, no browser
├── requirements.txt
├── packages.txt             # System library needed by OpenCV (libgl1)
└── .streamlit/config.toml   # Dark theme config
```

## ✋ Supported Gestures

**Single hand:**
Open Palm ✋ · Fist ✊ · Thumbs Up 👍 · Thumbs Down 👎 · Peace ✌️ · Point ☝️ ·
OK 👌 · I Love You 🤟 · Call Me 🤙🏻 · Pinched Fingers 🤌🏻 · 🖕

**Two hands together:**
Heart Hands 🫶🏻 · Shy 👉🏻👈🏻

Add more anytime by editing the rules in `classify_gesture()` (single hand)
or `classify_two_hand_gesture()` (two hands) in `gesture_utils.py`.

---

## 🚀 Run Locally

1. **Python 3.9–3.13** works (this app uses MediaPipe's current Tasks API,
   which is not tied to the older, removed Solutions API).

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   Click **Start**, allow camera access, and show a gesture. The first run
   will download a small (~a few MB) hand-tracking model automatically.

5. **(Optional) Run the simple desktop version instead** (no browser,
   guaranteed offline voice via `pyttsx3`):
   ```bash
   python local_desktop_app.py
   ```
   Press `q` in the video window to quit.

### 🔊 About the voice
The app speaks using your **browser's** built-in text-to-speech
(`speechSynthesis`), so it works both locally and when deployed online.
Browsers block auto-playing audio until you've interacted with the page
once — just click anywhere on the page first.

---

## ☁️ Deploy on Streamlit Community Cloud (via GitHub)

1. Push this project to a GitHub repo:
   ```bash
   cd gesture_app
   git init
   git add .
   git commit -m "GestureSpeak"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub → **New app**.

3. Select your repo, branch `main`, main file `app.py` → **Deploy**.

4. Streamlit Cloud installs `requirements.txt` and `packages.txt` automatically.

### Notes
- `streamlit-webrtc` uses a public STUN server (already configured in
  `app.py`) so the visitor's own webcam works once deployed.
- If you ever hit a MediaPipe import error on deploy, it almost always
  means the platform's Python version and the installed MediaPipe version
  are mismatched — check the deploy logs for which MediaPipe version was
  actually installed, since Streamlit Cloud's default Python version can
  change over time.

---

## 🛠️ Customization Ideas
- Add new gestures: extend `classify_gesture()` or `classify_two_hand_gesture()` in `gesture_utils.py`.
- Adjust colors/theme in `style_utils.py` and `.streamlit/config.toml`.
- Tune sensitivity thresholds (e.g. `0.06`, `0.09` distance values in `gesture_utils.py`) if detection feels too strict or too loose for your camera/lighting.

Enjoy! 🚀
