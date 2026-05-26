# TkinterDownloader

A modern desktop YouTube video query and dashed video player built with Python, Tkinter, and VLC.

To play video using this app your pc must have vlc installed.

## Download

<p align="center">
  <a href="https://github.com/DevilForDevs/TkinterDownloader/releases">
    <img src="https://img.shields.io/badge/Download-Windows_EXE-0078D6?style=for-the-badge&logo=windows&logoColor=white" />
  </a>
</p>

## Related Project

<p align="center">
  <a href="https://github.com/DevilForDevs/YoutubeCloneAndroidXML">
    <img src="https://img.shields.io/badge/Related_Project-YouTube_Clone_XML-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
</p>


# Preview

## Search Results Screen

![Search Screen](https://github.com/user-attachments/assets/ccd13668-585b-4dca-9e57-3518c1a072b7)

---

## Embedded Player Screen

![Player Screen](https://github.com/user-attachments/assets/123b3fd8-de40-457f-86cb-054e72fef8ea)

---

## Embedded Player with Suggestions
![Player Screen](https://github.com/user-attachments/assets/5e2ddcc4-666e-462e-8ac7-be5c16f96d9b)

---

## Fullscreen Player

![Fullscreen Player](https://github.com/user-attachments/assets/86470259-0541-4388-9499-d843fd733f44)

---

# Features

- YouTube search using hidden internal APIs
- Smooth threaded loading
- Embedded VLC video player
- Resolution switching during playback
- Fullscreen support
- Sidebar navigation
- Seekbar with live duration updates
- Buffered playback UI
- Scrollable search results
- Thumbnail caching
- Async video loading using threading
- Desktop-style UI using Tkinter

---

# Architecture

## Search System

The search screen uses YouTube internal APIs instead of browser automation.

Features:

- Fast search responses
- Continuation token pagination
- Lazy loading
- Background threading
- Thumbnail downloading
- Infinite-style loading

---

## Player System

The player uses:

- `python-vlc`
- dynamic resolution switching

Playback is handled using VLC while Tkinter manages the UI layer.

---

# Threading

The application heavily uses Python threading to prevent UI freezing.

Threading is used for:

- YouTube search requests
- Thumbnail downloading
- Playlist generation
- Video metadata fetching

This keeps the Tkinter UI responsive during network operations.
Users can switch quality during playback without restarting the player.

---

# Fullscreen Mode

Fullscreen mode:

- hides sidebar automatically
- expands player view
- keeps controls accessible
- supports instant toggling

---

# Tech Stack

## UI

- Tkinter

## Video Playback

- VLC
- python-vlc

## Networking

- requests

## Concurrency

- threading

---

# Project Structure

```text
tabs/
├── Home/
├── Player/
│   ├── utils/
│   └── widgets/
widgets/
tempFiles/
thumbnail/
```

---

# Requirements

```bash
pip install python-vlc requests
```

Also install VLC Media Player on your system.

---

# Run

```bash
python main.py
```

---

# Notes

- Uses hidden YouTube APIs
- No browser automation
- No Selenium
- Lightweight desktop architecture
- Optimized for Windows desktop usage

---

# Future Improvements

- Download support
- Playlist support
- Subtitle support
- Playback history
- Keyboard shortcuts
- Better buffering detection
- Audio/video separate stream merging
- Theme system

---

# License

MIT License
