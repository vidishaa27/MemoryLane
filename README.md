# MemoryLane

A platform for creating personal digital magazines — preserve memories, life events, friendships, relationships, travels, and personal stories in a magazine-style format.

## Problem

Tools like Canva help with general design but don't offer a dedicated experience for building personal, story-based magazines that combine memories, music, and journaling in one cohesive format.

## Solution

MemoryLane lets users create their own digital magazines: add pages, write stories, upload photos, embed Spotify songs, and publish the finished magazine to share or read online.

## Features (V1)

- User accounts (sign up / log in)
- Create a magazine
- Add and organize pages
- Add text content to pages
- Add images to pages
- Add Spotify links to pages
- Publish a magazine
- Read a magazine online

## Tech Stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Flask (Python)

**Database**
- SQL

**Deployment**
- Vercel

## Target Users

Anyone who wants to preserve and revisit memories — life events, friendships, relationships, travel, and personal stories — in a beautiful, magazine-style format.

## Success Criteria (V1)

A user can:
- Create an account
- Create a magazine
- Add pages
- Add text and images to pages
- Add Spotify links
- Publish and view the magazine online

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
memorylane/
├── app/
│   ├── static/        # CSS, JS, images
│   ├── templates/      # HTML templates
│   ├── models.py       # Database models
│   ├── routes.py        # App routes
│   └── __init__.py
├── migrations/          # Database migrations
├── requirements.txt
├── .env.example
└── README.md
```

## Roadmap (Future Features)

- Drag-and-drop page editor
- Magazine templates
- Spotify song embeds (full player)
- Custom themes
- Private/Public magazine visibility
- PDF export
- Collaborative editing
- AI-assisted page design

## Contributing

Contributions, ideas, and feedback are welcome. Feel free to open an issue or submit a pull request.

## License

MIT License — feel free to use, modify, and build on this project.