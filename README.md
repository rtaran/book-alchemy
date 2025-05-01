# Digital Library 📚

A modern web application for managing your book collection, built with Flask and SQLAlchemy.

![Screenshot](https://via.placeholder.com/800x400.png?text=Digital+Library+Screenshot)

## Features

### Core Features
- **Book Management**: Add/View books with ISBN, title, publication year, and ratings
- **Author Management**: Add/View authors with birth/death dates
- **Search Functionality**: Find books by title or author name
- **Sorting**: Organize books by title or author
- **Responsive UI**: Modern design with Tailwind CSS
- **Cover Images**: Automatic book covers via OpenLibrary API

### Bonus Features
- 🎨 Modern UI Design
- 🔍 Detailed Book/Author Pages
- ❌ Cascade Author Deletion
- ⭐ Book Ratings (1-10)
- 🤖 AI Book Recommendations (OpenAI integration)

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- SQLite database

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/rtaran/book-alchemy.git
   cd book-alchemy
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your_secret_key_here
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

   - `SECRET_KEY`: A random string used by Flask for session security. You can generate one with:
     ```bash
     python -c "import secrets; print(secrets.token_hex(16))"
     ```

   - `RAPIDAPI_KEY`: Required for AI book recommendations. Get your key by:
     1. Sign up at [RapidAPI](https://rapidapi.com/)
     2. Subscribe to the [ChatGPT API](https://rapidapi.com/chatgpt-api-chatgpt-api-default/api/chatgpt-42)
     3. Copy your API key from the dashboard

4. Initialize the database and run the application:
   ```bash
   python app.py
   ```

   The application will be available at http://localhost:5001

## Usage

1. **Home Page**: Browse your book collection, search, and sort books
2. **Add Author**: Create new author profiles with biographical information
3. **Add Book**: Add new books to your library with details and ratings
4. **Book Details**: Click on any book title to view detailed information
5. **AI Recommendations**: Get personalized book recommendations based on your library

## Troubleshooting

- **Session Error**: If you see "The session is unavailable because no secret key was set", make sure you've created the `.env` file with a SECRET_KEY as described in the setup instructions.
- **Recommendation Error**: If book recommendations don't work, verify your RAPIDAPI_KEY is correctly set in the `.env` file.
