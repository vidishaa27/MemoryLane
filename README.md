# MemoryLane

A platform for creating personal digital magazines — preserve memories, life events, friendships, relationships, travels, and personal stories in a magazine-style format.

## Problem

Tools like Canva help with general design but don't offer a dedicated experience for building personal, story-based magazines that combine memories, music, and journaling in one cohesive format.

## Solution

MemoryLane lets users create their own digital magazines: add pages, write stories, upload photos, embed Spotify songs, and publish the finished magazine to share or read online.

## Features (Version 1)

- Create multiple digital magazines
- Add, edit, and delete pages
- Attach images to pages
- Add Spotify song links
- Reorder pages
- Dashboard with magazine statistics
- Export magazines as PDF
- Persistent SQLite storage

## Tech Stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Flask (Python)

**Database**
- SQLite

**Deployment**
- Render

## Target Users

Anyone who wants to preserve and revisit memories — life events, friendships, relationships, travel, and personal stories — in a beautiful, magazine-style format.

## Current Functionality (V1)

A user can:
- Create a magazine
- Add pages
- Add text and images to pages
- Add Spotify links
- Export magazine as pdf

## Getting Started

```bash
# Clone the repository
git clone https://github.com/<your-username>/memorylane.git
cd memorylane

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
flask run
```

## Project Structure

```
MemoryLane/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── static/
│   ├── style.css
│   ├── script.js
│   └── image.png
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── magazine.html
│   ├── create-magazine.html
│   └── create-page.html
│
├── screenshots/
└── LICENSE
```

## Roadmap (Future Features)


- Drag-and-drop page editor
- Magazine templates
- Spotify song embeds (full player)
- Custom themes
- Private/Public magazine visibility
- Collaborative editing
- AI-assisted page design

## Contributing

Contributions, ideas, and feedback are welcome. Feel free to open an issue or submit a pull request.

## License

MIT License — feel free to use, modify, and build on this project.