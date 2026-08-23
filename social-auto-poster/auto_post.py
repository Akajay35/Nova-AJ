"""
Nova AJ - Facebook + Instagram Auto Video Poster

Creates a 15-second MP4 from text, uploads it directly to a Facebook
Page, temporarily uploads it to file.io for a public URL, and then
publishes it to a connected Instagram Professional account.

SETUP
-----
1. Create a Meta developer app at https://developers.facebook.com/.
2. Connect your Instagram Professional account to your Facebook Page.
3. Configure the permissions required by your Meta app for Page video
   publishing and Instagram content publishing.
4. Put the following values in a local .env file:
       ACCESS_TOKEN=your_page_access_token
       PAGE_ID=your_numeric_page_id
       IG_USER_ID=your_instagram_professional_account_id
5. Install dependencies:
       pip install -r requirements.txt
6. Run:
       python auto_post.py

SECURITY
--------
Never commit .env or real access tokens to GitHub.

NOTE
----
Instagram video publishing is asynchronous. The script creates the
Instagram media container, waits for Meta to report FINISHED, and only
then calls media_publish.

file.io is a third-party temporary file host. Its API, limits, and
retention policy can change. If it does not return a public URL, the
Instagram part cannot continue.
"""

import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from moviepy import ColorClip, CompositeVideoClip, TextClip


VIDEO_FILE = Path("video.mp4")
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_DURATION = 15
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v23.0")
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")


def fail(message: str) -> None:
    print(f"\nERROR: {message}")
    sys.exit(1)


def check_environment() -> None:
    missing = [
        name
        for name, value in (
            ("ACCESS_TOKEN", ACCESS_TOKEN),
            ("PAGE_ID", PAGE_ID),
            ("IG_USER_ID", IG_USER_ID),
        )
        if not value
    ]
    if missing:
        fail(
            "Your .env file is missing "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in the real values."
        )


def api_error(response: requests.Response, service: str) -> None:
    try:
        payload = response.json()
        error = payload.get("error", {})
        message = error.get("message", response.text[:500])
        code = error.get("code")
        detail = f" (code {code})" if code is not None else ""
        print(f"ERROR: {service} rejected the request: {message}{detail}")
    except ValueError:
        print(
            f"ERROR: {service} rejected the request "
            f"with HTTP {response.status_code}."
        )


def create_video(text: str) -> None:
    print("\n1/4 Creating 15-second video...")

    background = ColorClip(
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        color=(20, 24, 35),
        duration=VIDEO_DURATION,
    )

    try:
        text_clip = TextClip(
            text=text,
            font_size=64,
            color="white",
            method="caption",
            size=(900, 1000),
            text_align="center",
            horizontal_align="center",
            vertical_align="center",
        ).with_position("center")

        def fade_opacity(t: float) -> float:
            return max(0.0, min(1.0, t))

        text_clip = text_clip.with_opacity(fade_opacity)
        video = CompositeVideoClip(
            [background, text_clip],
            size=(VIDEO_WIDTH, VIDEO_HEIGHT),
        ).with_duration(VIDEO_DURATION)

        video.write_videofile(
            str(VIDEO_FILE),
            fps=30,
            codec="libx264",
            audio=False,
        )
        video.close()
        text_clip.close()
    finally:
        background.close()

    if not VIDEO_FILE.exists():
        fail("MoviePy finished without creating video.mp4.")
    print(f"Created {VIDEO_FILE.resolve()}")


def upload_facebook() -> tuple[str, str]:
    print("\n2/4 Uploading video to Facebook Page...")
    url = f"{GRAPH_BASE_URL}/{PAGE_ID}/videos"

    try:
        with VIDEO_FILE.open("rb") as video_file:
            response = requests.post(
                url,
                data={"access_token": ACCESS_TOKEN},
                files={"source": (VIDEO_FILE.name, video_file, "video/mp4")},
                timeout=300,
            )
    except requests.RequestException as exc:
        fail(f"Could not connect to Facebook: {exc}")

    if not response.ok:
        api_error(response, "Facebook")
        sys.exit(1)

    video_id = response.json().get("id")
    if not video_id:
        fail("Facebook did not return a video ID. Check your token and Page permissions.")

    link = f"https://www.facebook.com/{video_id}"
    print(f"Facebook Video ID: {video_id}")
    print(f"Facebook link: {link}")
    return video_id, link


def upload_file_io() -> str:
    print("\n3/4 Creating a temporary public URL with file.io...")

    try:
        with VIDEO_FILE.open("rb") as video_file:
            response = requests.post(
                "https://file.io",
                files={"file": (VIDEO_FILE.name, video_file, "video/mp4")},
                timeout=300,
            )
    except requests.RequestException as exc:
        fail(f"Could not connect to file.io: {exc}")

    if not response.ok:
        fail(
            "file.io rejected the upload. Its service or limits may have changed. "
            f"HTTP {response.status_code}."
        )

    try:
        data = response.json()
    except ValueError:
        fail("file.io did not return valid JSON.")

    public_url = data.get("link") or data.get("url") or data.get("download_url")
    if not public_url:
        fail("file.io did not return a public video URL.")

    print("Public URL created. Instagram can now fetch the video.")
    return public_url


def create_instagram_container(video_url: str, caption: str) -> str:
    url = f"{GRAPH_BASE_URL}/{IG_USER_ID}/media"
    try:
        response = requests.post(
            url,
            data={
                "access_token": ACCESS_TOKEN,
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
            },
            timeout=120,
        )
    except requests.RequestException as exc:
        fail(f"Could not connect to Instagram: {exc}")

    if not response.ok:
        api_error(response, "Instagram container creation")
        sys.exit(1)

    container_id = response.json().get("id")
    if not container_id:
        fail("Instagram did not return a container ID. Check IG_USER_ID and permissions.")

    print(f"Instagram container: {container_id}")
    return container_id


def wait_for_instagram(container_id: str) -> None:
    print("Waiting for Instagram to process the video...")
    url = f"{GRAPH_BASE_URL}/{container_id}"

    for attempt in range(1, 31):
        try:
            response = requests.get(
                url,
                params={"access_token": ACCESS_TOKEN, "fields": "status_code"},
                timeout=60,
            )
        except requests.RequestException as exc:
            fail(f"Could not check Instagram processing status: {exc}")

        if not response.ok:
            api_error(response, "Instagram status check")
            sys.exit(1)

        status = response.json().get("status_code")
        print(f"  Attempt {attempt}/30: {status}")

        if status == "FINISHED":
            return
        if status in {"ERROR", "EXPIRED"}:
            fail(f"Instagram could not process the video. Status: {status}")

        time.sleep(10)

    fail("Instagram did not finish processing within the timeout. Try again later.")


def publish_instagram(container_id: str) -> str:
    url = f"{GRAPH_BASE_URL}/{IG_USER_ID}/media_publish"
    try:
        response = requests.post(
            url,
            data={
                "access_token": ACCESS_TOKEN,
                "creation_id": container_id,
            },
            timeout=120,
        )
    except requests.RequestException as exc:
        fail(f"Could not publish to Instagram: {exc}")

    if not response.ok:
        api_error(response, "Instagram publishing")
        sys.exit(1)

    media_id = response.json().get("id")
    if not media_id:
        fail("Instagram did not return a Media ID.")
    return media_id


def get_instagram_permalink(media_id: str) -> str | None:
    try:
        response = requests.get(
            f"{GRAPH_BASE_URL}/{media_id}",
            params={"access_token": ACCESS_TOKEN, "fields": "permalink"},
            timeout=60,
        )
    except requests.RequestException:
        return None

    if not response.ok:
        return None
    return response.json().get("permalink")


def main() -> None:
    print("=" * 60)
    print("      NOVA AJ - FACEBOOK + INSTAGRAM AUTO POSTER")
    print("=" * 60)

    check_environment()

    text = input("\nEnter the text for your 15-second video: ").strip()
    if not text:
        fail("You did not enter any text. Run the program again and enter text.")

    create_video(text)
    facebook_id, facebook_link = upload_facebook()
    public_url = upload_file_io()
    container_id = create_instagram_container(public_url, text)
    wait_for_instagram(container_id)
    instagram_id = publish_instagram(container_id)
    instagram_link = get_instagram_permalink(instagram_id)

    print("\n" + "=" * 60)
    print("SUCCESS - BOTH PLATFORMS HAVE BEEN PROCESSED")
    print("=" * 60)
    print(f"Facebook Video ID:   {facebook_id}")
    print(f"Facebook Link:       {facebook_link}")
    print(f"Instagram Media ID:  {instagram_id}")
    print(f"Instagram Link:      {instagram_link or 'Not returned by Meta'}")
    print(f"Local video:         {VIDEO_FILE.resolve()}")


if __name__ == "__main__":
    main()
