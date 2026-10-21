from pathlib import Path
import streamlit as st

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Images folder
IMAGE_DIR = BASE_DIR / "images"


def find_image(keyword):
    """
    Find an image by keyword.
    Works with JPG, JPEG, PNG and WEBP.
    """

    if not IMAGE_DIR.exists():
        return None

    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    keyword = keyword.lower()

    for file in IMAGE_DIR.iterdir():

        if not file.is_file():
            continue

        if file.suffix.lower() not in extensions:
            continue

        if keyword in file.stem.lower():
            return str(file)

    return None


def show_image(keyword, caption=None):

    image = find_image(keyword)

    if image:

        st.image(
            image,
            caption=caption,
            use_container_width=True
        )

        return True

    else:

        st.warning(
            f"Image not found for: {keyword}"
        )

        return False


# ============================================================
# AVAILABLE IMAGES
# ============================================================

MCLAREN_CAR = find_image("mclaren_car")
LANDO_NORRIS = find_image("lando_norris")
OSCAR_PIASTRI = find_image("oscar_piastri")
F1_RACE = find_image("f1_race")