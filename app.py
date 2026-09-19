# app.py

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

st.title("🔒 Vault")
st.caption("Hide encrypted messages inside ordinary images.")

mode = st.radio("Choose an action:", ["Generate my keys", "Hide a message", "Reveal a message"])

# ===========================================================
if mode == "Generate my keys":
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
elif mode == "Hide a message":
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

        st.image(st.session_state.qr_bytes, caption="QR code (send this separately from the image)")
        st.download_button("Download QR code", st.session_state.qr_bytes,
                            file_name="passphrase_qr.png")

# ===========================================================
else:
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