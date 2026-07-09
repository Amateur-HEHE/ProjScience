import time
import cv2
import av
import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoProcessorBase

from gesture_utils import (
    get_hands_detector,
    mp_hands,
    mp_drawing,
    mp_drawing_styles,
    classify_gesture,
    classify_two_hand_gesture,
)
from style_utils import inject_custom_css

st.set_page_config(
    page_title="GestureSpeak | Live Detection",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_custom_css()

st.markdown('<div class="hero-title">🖐️ GestureSpeak — Live Detection</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Click START, allow camera access, and show a gesture.</div>',
    unsafe_allow_html=True,
)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

top_col1, top_col2 = st.columns(2)
with top_col1:
    voice_enabled = st.toggle("🔊 Speak detected gesture", value=True)
with top_col2:
    mirror = st.toggle("🪞 Mirror view (selfie mode)", value=True)


class GestureProcessor(VideoProcessorBase):
    def __init__(self):
        self.hands = get_hands_detector(max_num_hands=2)
        self.latest_gesture = "No hand detected"
        self.mirror = True

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        if self.mirror:
            img = cv2.flip(img, 1)

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture_text = "No hand detected"

        if results.multi_hand_landmarks and results.multi_handedness:
            all_landmarks = []
            handedness_labels = []

            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                mp_drawing.draw_landmarks(
                    img,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
                all_landmarks.append(hand_landmarks.landmark)
                handedness_labels.append(handedness.classification[0].label)

            two_hand_label = classify_two_hand_gesture(all_landmarks, handedness_labels)
            if two_hand_label:
                gesture_text = two_hand_label
            else:
                gesture_text = classify_gesture(all_landmarks[0], handedness_labels[0])

        self.latest_gesture = gesture_text

        cv2.rectangle(img, (0, 0), (img.shape[1], 60), (10, 10, 16), -1)
        cv2.putText(
            img, f"Gesture: {gesture_text}", (15, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (74, 222, 222), 2, cv2.LINE_AA
        )

        return av.VideoFrame.from_ndarray(img, format="bgr24")


col_video, col_info = st.columns([2, 1])

with col_video:
    webrtc_ctx = webrtc_streamer(
        key="gesture-speak",
        video_processor_factory=GestureProcessor,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col_info:
    st.markdown("#### Detected gesture")
    label_placeholder = st.empty()
    tts_placeholder = st.empty()


if webrtc_ctx.video_processor:
    webrtc_ctx.video_processor.mirror = mirror

last_spoken = None

if webrtc_ctx.state.playing:
    while webrtc_ctx.state.playing:
        if webrtc_ctx.video_processor:
            gesture = webrtc_ctx.video_processor.latest_gesture
        else:
            gesture = "No hand detected"

        label_placeholder.markdown(
            f'<div class="detected-banner">{gesture}</div>', unsafe_allow_html=True
        )

        if (
            voice_enabled
            and gesture not in ("No hand detected", "Unknown")
            and gesture != last_spoken
        ):
            spoken_text = " ".join(gesture.split(" ")[:-1]) or gesture
            js = f"""
            <script>
            var msg = new SpeechSynthesisUtterance({spoken_text!r});
            msg.rate = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
            </script>
            """
            with tts_placeholder:
                components.html(js, height=0, width=0)
            last_spoken = gesture

        time.sleep(0.35)
else:
    label_placeholder.markdown(
        '<div class="detected-banner">Click START above to begin</div>',
        unsafe_allow_html=True,
    )
