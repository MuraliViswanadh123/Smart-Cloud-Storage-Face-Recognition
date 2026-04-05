import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image
from deepface import DeepFace

# =========================
# 📁 Create Folders
# =========================
os.makedirs("face_db", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

st.set_page_config(page_title="Smart Cloud Storage", layout="centered")
st.title("🔐 Smart Cloud Storage with Face Recognition")

menu = st.sidebar.selectbox("Menu", ["Register", "Login"])

# =========================
# SESSION INIT
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# CACHE MODEL (IMPORTANT)
# =========================
@st.cache_resource
def load_model():
    return True  # dummy cache trigger for DeepFace

load_model()

# =========================
# 👤 REGISTER
# =========================
if menu == "Register":
    st.header("👤 Register User")

    name = st.text_input("Enter Username")
    img_file = st.camera_input("Capture Face")

    if st.button("Register"):
        if not name:
            st.warning("⚠️ Please enter username")
        elif not img_file:
            st.warning("⚠️ Please capture image")
        else:
            image = Image.open(img_file)
            img = np.array(image)

            cv2.imwrite(f"face_db/{name}.jpg", img)

            st.success("✅ Face Registered Successfully")

# =========================
# 🔐 LOGIN
# =========================
elif menu == "Login":
    st.header("🔐 Login with Face")

    img_file = st.camera_input("Capture Face for Login")

    if st.button("Login"):
        if not img_file:
            st.warning("⚠️ Capture your face first")
        elif len(os.listdir("face_db")) == 0:
            st.error("❌ No registered users. Please register first.")
        else:
            image = Image.open(img_file)
            img = np.array(image)

            temp_path = "temp.jpg"
            cv2.imwrite(temp_path, img)

            authenticated_user = None

            with st.spinner("🔍 Verifying Face... Please wait"):
                for file in os.listdir("face_db"):
                    db_path = os.path.join("face_db", file)

                    try:
                        result = DeepFace.verify(
                            img1_path=temp_path,
                            img2_path=db_path,
                            model_name="SFace",  # 🔥 lighter & cloud-friendly
                            enforce_detection=False
                        )

                        if result["verified"]:
                            authenticated_user = file.split(".")[0]
                            break
                    except Exception as e:
                        st.warning(f"Skipping file: {file}")

            if authenticated_user:
                st.session_state.user = authenticated_user
                st.success(f"✅ Welcome {authenticated_user}")
            else:
                st.error("❌ Face Not Recognized")

    # =========================
    # AFTER LOGIN
    # =========================
    if st.session_state.user:
        user = st.session_state.user

        st.success(f"👋 Logged in as {user}")

        # Create user folder
        user_folder = f"uploads/{user}"
        os.makedirs(user_folder, exist_ok=True)

        # =========================
        # FILE UPLOAD
        # =========================
        st.subheader("📁 Upload File")
        uploaded_file = st.file_uploader("Choose a file")

        if uploaded_file is not None:
            file_path = os.path.join(user_folder, uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success("📤 File Uploaded Successfully")

        # =========================
        # FILE DOWNLOAD
        # =========================
        st.subheader("📂 Your Files")

        files = os.listdir(user_folder)

        if len(files) == 0:
            st.info("No files uploaded yet")
        else:
            for file in files:
                file_path = os.path.join(user_folder, file)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ {file}",
                        data=f,
                        file_name=file
                    )

        # =========================
        # LOGOUT
        # =========================
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("🔐 AI-Based Secure Cloud Storage | Streamlit + DeepFace")