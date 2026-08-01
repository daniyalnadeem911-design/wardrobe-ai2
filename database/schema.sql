-- database/schema.sql

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    gender TEXT,
    height TEXT,
    skin_tone TEXT,
    country TEXT,
    city TEXT,
    preferred_style TEXT,
    favorite_colors TEXT,
    theme TEXT DEFAULT 'light',
    groq_api_key TEXT,
    onboarded INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wardrobe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    section TEXT NOT NULL,
    color TEXT,
    material TEXT,
    pattern TEXT,
    sleeve_length TEXT,
    brand TEXT,
    season TEXT,
    description TEXT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    occasion TEXT,
    weather_summary TEXT,
    upper_id INTEGER,
    lower_id INTEGER,
    footwear_id INTEGER,
    accessory_id INTEGER,
    jacket_id INTEGER,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    outfit_id INTEGER NOT NULL,
    worn_on DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (outfit_id) REFERENCES outfits(id)
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    outfit_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (outfit_id) REFERENCES outfits(id)
);