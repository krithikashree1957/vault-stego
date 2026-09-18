# app.py

import streamlit as st
from PIL import Image
import io

from crypto_utils import encrypt_message, decrypt_message
from stego import hide_data, extract_data
from passphrase_utils import generate_passphrase

st.set_page_config(page_title="Vault - Secret Messages in Images", page_icon="🔒")

st.title("🔒 Vault")
st.caption("Hide encrypted messages inside ordinary images.")

mode = st.radio("Choose an action:", ["Hide a message", "Reveal a message"])

# ---------------------------------------------------------
if mode == "Hide a message":
    st.subheader("Hide a secret message inside an image")

    uploaded_image = st.file_uploader("Upload a PNG image", type=["png"])
    message = st.text_area("Secret message")

    if "generated_pw" not in st.session_state:
        st.session_state.generated_pw = ""

    col1, col2 = st.columns([3, 1])
    with col1:
        passphrase = st.text_input(
            "Passphrase",
            value=st.session_state.generated_pw,
            type="password"
        )
    with col2:
        if st.button("🎲 Generate"):
            st.session_state.generated_pw = generate_passphrase()
            st.rerun()

    if st.session_state.generated_pw:
        st.caption(f"Generated passphrase (save this!): `{st.session_state.generated_pw}`")

    if st.button("Hide message"):
        if not uploaded_image or not message or not passphrase:
            st.error("Please provide an image, a message, and a passphrase.")
        else:
            with open("temp_input.png", "wb") as f:
                f.write(uploaded_image.getbuffer())

            try:
                encrypted = encrypt_message(message, passphrase)
                hide_data("temp_input.png", encrypted, "temp_output.png")

                st.success("Message hidden successfully!")
                st.image("temp_output.png", caption="Your image with the hidden message")

                with open("temp_output.png", "rb") as f:
                    st.download_button(
                        "Download image",
                        f,
                        file_name="secret_image.png",
                        mime="image/png"
                    )
            except ValueError as e:
                st.error(str(e))

# ---------------------------------------------------------
else:
    st.subheader("Reveal a hidden message from an image")

    uploaded_image = st.file_uploader("Upload the image containing a hidden message", type=["png"])
    passphrase = st.text_input("Passphrase", type="password", key="reveal_pw")

    if st.button("Reveal message"):
        if not uploaded_image or not passphrase:
            st.error("Please provide an image and a passphrase.")
        else:
            with open("temp_reveal.png", "wb") as f:
                f.write(uploaded_image.getbuffer())

            try:
                extracted_bytes = extract_data("temp_reveal.png")
                message = decrypt_message(extracted_bytes, passphrase)
                st.success("Message revealed!")
                st.text_area("Hidden message:", value=message, disabled=True)
            except ValueError:
                st.error("No hidden data found in this image.")
            except Exception:
                st.error("Incorrect passphrase, or the image/data is corrupted.")