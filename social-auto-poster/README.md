# Nova AJ Social Auto Poster

A beginner-friendly Python app that creates a 15-second text video and publishes it to a Facebook Page and a connected Instagram Professional account.

## Features

- Creates a vertical 1080x1920 MP4 with MoviePy.
- Centers the supplied text and fades it in.
- Uploads the local MP4 directly to the Facebook Graph API.
- Uses file.io as temporary public hosting for Instagram's `video_url` requirement.
- Waits for Instagram media processing before publishing.
- Reads secrets from `.env` instead of source code.

## Files

```text
social-auto-poster/
├── auto_post.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer.
- A Facebook Page that you manage.
- An Instagram Professional account connected to that Page.
- A configured Meta developer app and an access token with the permissions required by your app.

## Setup

1. Copy `.env.example` to `.env`.
2. Put your Meta values into `.env`:

```text
ACCESS_TOKEN=YOUR_PAGE_ACCESS_TOKEN
PAGE_ID=YOUR_FACEBOOK_PAGE_ID
IG_USER_ID=YOUR_INSTAGRAM_PROFESSIONAL_ACCOUNT_ID
GRAPH_API_VERSION=v23.0
```

3. Install packages:

```bash
pip install -r requirements.txt
```

4. Run:

```bash
python auto_post.py
```

5. Enter the text when prompted.

## Meta setup

Use the official Meta developer portal and documentation to create/configure your app and obtain the correct Page access token. Meta permissions and Graph API versions can change, so use the current requirements shown for your app.

The account must be eligible for Instagram Graph API publishing. A personal Instagram account is not sufficient for this workflow.

## Security

Never commit `.env` or a real access token. The included `.gitignore` prevents accidental commits.

## Temporary hosting note

Instagram needs a public URL so its servers can fetch a video. This project uses file.io to create that URL automatically. file.io is an external service and can change its API, limits, availability, or retention behavior. If it stops accepting the upload, replace `upload_file_io()` with another public object-storage/upload provider.

## Troubleshooting

### Missing token/Page/account ID

Make sure `.env` exists in the same directory from which the program is run and contains all three required values.

### Facebook permission error

The access token may be the wrong token type, expired, or missing the permissions required by the current Meta API/app configuration.

### Instagram container error

Check that `IG_USER_ID` is the Instagram Professional account ID, not the Instagram username, and that the account is connected to the Facebook Page.

### Instagram processing error

The video must be reachable by Meta through the temporary public URL. Try again if the temporary host expires or rejects the upload.
