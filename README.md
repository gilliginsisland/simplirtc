# simplirtc

`simplirtc` is a small wrapper script around [bachya/simplisafe-python](https://github.com/bachya/simplisafe-python), designed for use with [AlexxIT/go2rtc](https://github.com/AlexxIT/go2rtc) as an `echo` plugin. It extracts Amazon Kinesis stream information from SimpliSafe cameras and makes it available to `go2rtc`, enabling video streaming over WebRTC, RTSP, HomeKit, and other protocols.

## Features

- Extracts SimpliSafe camera stream info (Amazon Kinesis)
- Echo-compatible with `go2rtc`
- Enables Home Assistant, Frigate, and other integrations via go2rtc

## Installation

Install directly from GitHub using pip or uv:

```bash
pip install git+https://github.com/gilliginsisland/simplirtc.git
```

or using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install git+https://github.com/gilliginsisland/simplirtc.git
```

This will install the `simplirtc` CLI entry point.

## Authentication

Before streaming, you must generate a token by authenticating with SimpliSafe:

```bash
simplirtc --token <path-to-token-file> authenticate
```

Follow the interactive prompt to authenticate.

## Camera Listing

Once authenticated, fetch your camera and location IDs:

```bash
simplirtc --token <path-to-token-file> cameras
```

Example output:

```json
{
  "My Home (1234567)": [
    "Dining Room (2e62e933cd05957f502797cf95d6fa49)",
    "Basement (c725b9ecaa40be2e1c748d198c0e70ba)"
  ]
}
```

## go2rtc Configuration

Add the following entries to your `go2rtc` config:

```yaml
streams:
  simplirtc_dining_room:
    - echo:simplirtc --token=/etc/go2rtc/simplirtc.token stream --location=1234567 --camera=2e62e933cd05957f502797cf95d6fa49
    - ffmpeg:simplirtc_dining_room#audio=opus/16000

  simplirtc_basement:
    - echo:simplirtc --token=/etc/go2rtc/simplirtc.token stream --location=1234567 --camera=c725b9ecaa40be2e1c748d198c0e70ba
    - ffmpeg:simplirtc_basement#audio=opus/16000
```

## Streaming Output

Once configured, `go2rtc` will handle transcoding and stream delivery via:

- WebRTC (browser)
- RTSP
- HomeKit
- Any client supported by go2rtc

## Use Cases

- Integrate SimpliSafe cameras into Home Assistant
- Add to Frigate for object detection
- Use RTSP streams in NVRs or video players
- Enable HomeKit Secure Video for SimpliSafe cameras

## License

This project is licensed under [The Unlicense](https://unlicense.org/). You are free to use, modify, and distribute this software without restriction.

There is absolutely no warranty.
