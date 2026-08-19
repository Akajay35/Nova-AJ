# Nova-AJ Android

Native Android client foundation for Nova-AJ.

## Architecture

- Kotlin + Jetpack Compose UI
- HTTPS/WebSocket transport to the Nova-AJ backend
- No API keys stored in the Android client
- Voice input/output handled by Android capabilities
- Authentication and backend authorization remain server-side

## Planned screens

- Home / voice assistant
- Chat
- Trainer Mode
- Skills
- Memory
- Permissions
- Settings
- Diagnostics

This directory is intentionally a client foundation. Backend business logic remains in the root Nova-AJ application.
