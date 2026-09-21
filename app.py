
import streamlit as st
import io
import base64
 
from crypto_utils import encrypt_message, decrypt_message
from stego import hide_data, extract_data
from passphrase_utils import generate_passphrase
from keys_utils import (
    generate_key_pair, serialize_private_key, serialize_public_key,
    load_public_key, load_private_key, rsa_encrypt, rsa_decrypt
)
import qrcode
 
st.set_page_config(page_title="Vault - Secret Messages in Images", page_icon="🔒")
 
# ===========================================================
# THEME / STYLING
# ===========================================================
st.markdown("""
<style>
 
@keyframes fade-in {
  0% { opacity: 0; transform: translateY(-12px); }
  100% { opacity: 1; transform: translateY(0); }
}
 
@keyframes scale-in-center {
  0% { transform: scale(0.92); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
 
@keyframes pulse-glow {
  0% { box-shadow: 0 0 0 0 rgba(168, 130, 255, 0.45); }
  70% { box-shadow: 0 0 0 12px rgba(168, 130, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(168, 130, 255, 0); }
}
 
@keyframes float-symbol {
  0%   { transform: translateY(0px) rotate(0deg); opacity: 0.15; }
  50%  { transform: translateY(-25px) rotate(8deg); opacity: 0.3; }
  100% { transform: translateY(0px) rotate(0deg); opacity: 0.15; }
}
 
.stApp {
  background: linear-gradient(90deg, #2d1a4b 0.000%, #2d1a4b 7.692%, #2e1642 calc(7.692% + 1px), #2e1642 15.385%, #30133b calc(15.385% + 1px), #30133b 23.077%, #351236 calc(23.077% + 1px), #351236 30.769%, #3b1435 calc(30.769% + 1px), #3b1435 38.462%, #431836 calc(38.462% + 1px), #431836 46.154%, #4c1f39 calc(46.154% + 1px), #4c1f39 53.846%, #54273f calc(53.846% + 1px), #54273f 61.538%, #5d3148 calc(61.538% + 1px), #5d3148 69.231%, #653c52 calc(69.231% + 1px), #653c52 76.923%, #6b485f calc(76.923% + 1px), #6b485f 84.615%, #6f546d calc(84.615% + 1px), #6f546d 92.308%, #71617c calc(92.308% + 1px) 100.000%);
  color: #f1e9ff;
}
 
/* ===========================================================
   SOFT TYPOGRAPHY — UI ONLY
   =========================================================== */
 
html, body, [class*="st-"] {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
}
 
/* Main text */
p, label, .stMarkdown, .stCaption {
    font-size: 1rem !important;
    line-height: 1.55 !important;
}
 
/* Headings */
h1 {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
}
 
h2 {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 650 !important;
}
 
h3 {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 600 !important;
}
 
/* Buttons */
div[data-testid="stButton"] button {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 1rem !important;
}
 
/* Text inputs / text areas */
input, textarea {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 1rem !important;
}
 
/* Radio buttons / file uploader */
div[data-testid="stRadio"],
div[data-testid="stFileUploader"] {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: 1rem !important;
}
 
/* Keep Streamlit's icon font intact (prevents "upload" text overlapping the button label) */
span[data-testid="stIconMaterial"],
span[class*="material-symbols"],
.material-symbols-rounded,
.material-symbols-outlined {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
}
 
.floating-symbols {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
 
.floating-symbols span {
  position: absolute;
  font-size: 2.2rem;
  animation: float-symbol 6s ease-in-out infinite;
  opacity: 0.15;
}
 
.floating-symbols span:nth-child(1) { top: 8%;  left: 6%;  animation-delay: 0s; }
.floating-symbols span:nth-child(2) { top: 20%; left: 85%; animation-delay: 1.2s; }
.floating-symbols span:nth-child(3) { top: 70%; left: 10%; animation-delay: 2.1s; }
.floating-symbols span:nth-child(4) { top: 80%; left: 80%; animation-delay: 0.7s; }
.floating-symbols span:nth-child(5) { top: 45%; left: 92%; animation-delay: 1.8s; }
.floating-symbols span:nth-child(6) { top: 55%; left: 3%;  animation-delay: 2.6s; }
.floating-symbols span:nth-child(7) { top: 5%;  left: 45%; animation-delay: 1.4s; }
.floating-symbols span:nth-child(8) { top: 90%; left: 48%; animation-delay: 0.3s; }
 
.main .block-container {
  position: relative;
  z-index: 1;
}
 
h1 {
  animation: fade-in 0.8s ease-out;
  background: linear-gradient(90deg, #c8a8ff, #ff9ecf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800 !important;
  letter-spacing: 0.5px;
}
 
.stCaption, p, label {
  animation: fade-in 1s ease-out;
}
 
div[data-testid="stButton"] button {
  background: linear-gradient(90deg, #7c3aed, #db2777);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.55em 1.4em;
  font-weight: 600;
  letter-spacing: 0.3px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  width: 100%;
}
 
div[data-testid="stButton"] button:hover {
  transform: translateY(-2px);
  animation: pulse-glow 1.6s infinite;
}
 
div[data-testid="stAlert"] {
  animation: scale-in-center 0.4s ease-out;
  border-radius: 14px;
  backdrop-filter: blur(6px);
}
 
div[data-testid="stImage"] img {
  animation: scale-in-center 0.5s ease-out;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.45);
}
 
div[data-testid="stFileUploader"], div[data-testid="stTextInput"], div[data-testid="stTextArea"] {
  animation: fade-in 0.6s ease-out;
  background: rgba(255,255,255,0.04);
  border-radius: 14px;
  padding: 0.4em;
  backdrop-filter: blur(4px);
}
 
/* Ensure only Streamlit's native file-upload label is displayed. */
div[data-testid="stFileUploader"] button::before,
div[data-testid="stFileUploader"] button::after {
  content: none !important;
  display: none !important;
}
 
hr { border-color: rgba(255,255,255,0.15) !important; }
 
.hero-card {
  background: rgba(255,255,255,0.06);
  border-radius: 20px;
  padding: 2em;
  backdrop-filter: blur(8px);
  animation: fade-in 0.8s ease-out;
  margin-bottom: 1.5em;
}
 
</style>
 
<div class="floating-symbols">
  <span>🔒</span><span>🔑</span><span>✦</span><span>🛡️</span>
  <span>🔒</span><span>🔑</span><span>✦</span><span>👾</span>
</div>
""", unsafe_allow_html=True)
 
# ===========================================================
# PAGE ROUTER
# ===========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
 
def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()
 
# ===========================================================
# HOME PAGE
# ===========================================================
if st.session_state.page == "home":
    st.title("🔒 Vault")
    st.markdown("""
    <div class="hero-card">
    <h3>Welcome to Vault</h3>
    <p>Hide encrypted messages inside ordinary images — combining real cryptography,
    image steganography, and public-key security, all in one tool.</p>
    <p>Your secret stays invisible to the eye and unreadable without the right key.</p>
    </div>
    """, unsafe_allow_html=True)
 
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔑 Generate My Keys", use_container_width=True):
            go_to("keys")
    with col2:
        if st.button("🖼️ Hide a Message", use_container_width=True):
            go_to("hide")
    with col3:
        if st.button("🔓 Reveal a Message", use_container_width=True):
            go_to("reveal")
 
# ===========================================================
# GENERATE KEYS PAGE
# ===========================================================
elif st.session_state.page == "keys":
    if st.button("← Back to Home"):
        go_to("home")
 
    st.subheader("Generate your key pair (do this once, as the receiver)")
    st.write("Share your **public key** with anyone who wants to send you a secret. "
             "Keep your **private key** safe — never share it.")
 
    if st.button("Generate key pair"):
        priv, pub = generate_key_pair()
        st.session_state.priv_pem = serialize_private_key(priv)
        st.session_state.pub_pem = serialize_public_key(pub)
 
    if "pub_pem" in st.session_state:
        st.success("Key pair generated!")
        st.text_area("Your public key (share this)",
                      st.session_state.pub_pem.decode(), height=150)
        st.download_button("Download public key", st.session_state.pub_pem,
                            file_name="public_key.pem")
        st.download_button("Download private key (KEEP SECRET)",
                            st.session_state.priv_pem,
                            file_name="private_key.pem")
        st.warning("Download both files now — they won't be shown again after you leave this page.")
 
# ===========================================================
# HIDE PAGE
# ===========================================================
elif st.session_state.page == "hide":
    if st.button("← Back to Home"):
        go_to("home")
 
    st.subheader("Hide a secret message inside an image")
 
    uploaded_image = st.file_uploader("Upload a PNG image", type=["png"])
    message = st.text_area("Secret message")
    receiver_pub_file = st.file_uploader("Upload receiver's public key (.pem) — required", type=["pem"], key="recv_pub")
 
    hide_method = st.radio(
        "Passphrase sharing preference:",
        ["Secure mode — passphrase hidden, only QR + receiver's private key can unlock",
         "Convenience mode — show me the passphrase so I can share it myself too"]
    )
 
    show_passphrase = hide_method.startswith("Convenience")
 
    if "generated_pw" not in st.session_state or st.session_state.get("regen"):
        st.session_state.generated_pw = generate_passphrase()
        st.session_state.regen = False
 
    if st.button("🎲 Regenerate passphrase"):
        st.session_state.regen = True
        st.rerun()
 
    passphrase = st.session_state.generated_pw
 
    if show_passphrase:
        st.caption(f"Passphrase (save this — share it with the receiver!): `{passphrase}`")
    else:
        st.caption("Passphrase generated — kept hidden. Only recoverable via QR + receiver's private key.")
 
    st.divider()
    if st.button("Hide message"):
        if not uploaded_image or not message:
            st.error("Please provide an image and a message.")
        elif not receiver_pub_file:
            st.error("Please upload the receiver's public key — required to generate the QR code.")
        else:
            with open("temp_input.png", "wb") as f:
                f.write(uploaded_image.getbuffer())
            try:
                encrypted = encrypt_message(message, passphrase)
                hide_data("temp_input.png", encrypted, "temp_output.png")
 
                with open("temp_output.png", "rb") as f:
                    st.session_state.output_image_bytes = f.read()
 
                pub_key = load_public_key(receiver_pub_file.read())
                encrypted_pw = rsa_encrypt(pub_key, passphrase.encode())
                qr_payload = base64.b64encode(encrypted_pw).decode()
                qr_img = qrcode.make(qr_payload)
 
                buf = io.BytesIO()
                qr_img.save(buf, format="PNG")
                st.session_state.qr_bytes = buf.getvalue()
 
                st.session_state.hide_success = True
 
            except ValueError as e:
                st.error(str(e))
                st.session_state.hide_success = False
 
    if st.session_state.get("hide_success"):
        st.success("Message hidden successfully!")
 
        st.image(st.session_state.output_image_bytes, caption="Your image with the hidden message")
        st.download_button("Download image", st.session_state.output_image_bytes,
                            file_name="secret_image.png", mime="image/png")
 
        qr_caption = (
            "QR code — the more secure option; requires the receiver's private key to unlock"
            if not show_passphrase else
            "QR code (optional secure alternative — receiver can also use this instead of the passphrase above)"
        )
        st.image(st.session_state.qr_bytes, caption=qr_caption)
        st.download_button("Download QR code", st.session_state.qr_bytes,
                            file_name="passphrase_qr.png")
 
# ===========================================================
# REVEAL PAGE
# ===========================================================
elif st.session_state.page == "reveal":
    if st.button("← Back to Home"):
        go_to("home")
 
    st.subheader("Reveal a hidden message from an image")
 
    uploaded_image = st.file_uploader("Upload the image containing a hidden message", type=["png"])
 
    reveal_method = st.radio(
        "How was the passphrase shared with you?",
        ["I have the passphrase directly", "I have a QR code + my private key"]
    )
 
    passphrase = None
 
    if reveal_method == "I have the passphrase directly":
        passphrase = st.text_input("Passphrase", type="password", key="reveal_pw_direct")
 
    else:
        qr_file = st.file_uploader("Upload the QR code image", type=["png"], key="qr_upload")
        private_key_file = st.file_uploader("Upload your private key (.pem)", type=["pem"], key="priv_upload")
 
        if qr_file and private_key_file:
            try:
                import cv2
                import numpy as np
 
                file_bytes = np.asarray(bytearray(qr_file.read()), dtype=np.uint8)
                img_cv = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
 
                detector = cv2.QRCodeDetector()
                qr_payload, points, _ = detector.detectAndDecode(img_cv)
 
                if not qr_payload:
                    st.error("Could not read the QR code image.")
                else:
                    encrypted_pw = base64.b64decode(qr_payload)
                    priv_key = load_private_key(private_key_file.read())
                    passphrase = rsa_decrypt(priv_key, encrypted_pw).decode()
                    st.success("Passphrase decrypted from QR code.")
            except Exception as e:
                st.error(f"Could not decrypt QR/private key: {e}")
 
    st.divider()
    if st.button("Reveal message"):
        if not uploaded_image or not passphrase:
            st.error("Please provide the image and a valid passphrase (directly or via QR).")
        else:
            try:
                with open("temp_reveal.png", "wb") as f:
                    f.write(uploaded_image.getbuffer())
                extracted_bytes = extract_data("temp_reveal.png")
                message = decrypt_message(extracted_bytes, passphrase)
                st.success("Message revealed!")
                st.text_area("Hidden message:", value=message, disabled=True)
            except ValueError:
                st.error("No hidden data found in this image.")
            except Exception:
                st.error("Incorrect passphrase, or the image/data is corrupted.")
 
