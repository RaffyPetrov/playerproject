import sqlite3

DATABASE_NAME = 'music_player.db'

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except sqlite3.Error as e:
        print(e)
    return conn

def execute_query(conn, query, values=None):
    """Execute a single query."""
    try:
        cursor = conn.cursor()
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    return cursor


# Table Creation Functions
def create_tables():
    """Initialize all tables."""
    conn = create_connection()
    
    # Playlist table
    execute_query(conn, """
    CREATE TABLE IF NOT EXISTS playlists (
        id integer PRIMARY KEY,
        name text NOT NULL
    );""")
    
    # Songs table
    execute_query(conn, """
    CREATE TABLE IF NOT EXISTS songs (
        id integer PRIMARY KEY,
        title text NOT NULL,
        path text NOT NULL
    );""")
    
    # Playlist-Song Linking table
    execute_query(conn, """
    CREATE TABLE IF NOT EXISTS playlist_song_link (
        id integer PRIMARY KEY,
        playlist_id integer NOT NULL,
        song_id integer NOT NULL,
        FOREIGN KEY (playlist_id) REFERENCES playlists (id),
        FOREIGN KEY (song_id) REFERENCES songs (id)
    );""")
    
    conn.close()

# Add New Data Functions
def add_playlist(playlist_name):
    conn = create_connection()
    execute_query(conn, "INSERT INTO playlists (name) VALUES (?)", (playlist_name,))
    conn.close()

def add_song(song_title, song_path):
    conn = create_connection()
    cursor = execute_query(conn, "INSERT INTO songs (title, path) VALUES (?, ?)", (song_title, song_path))
    song_id = cursor.lastrowid
    conn.close()
    return song_id

def add_song_to_playlist(playlist_name, song_path):
    song_title = song_path.split("/")[-1]
    song_id = add_song(song_title, song_path)

    conn = create_connection()
    cursor = execute_query(conn, "SELECT id FROM playlists WHERE name=?", (playlist_name,))
    playlist_id = cursor.fetchone()[0]
    conn.close()

    link_song_to_playlist(playlist_id, song_id)

# Link song to playlist
def link_song_to_playlist(playlist_id, song_id):
    conn = create_connection()
    execute_query(conn, "INSERT INTO playlist_song_link (playlist_id, song_id) VALUES (?, ?)", (playlist_id, song_id))
    conn.close()

# Fetch Data Functions
def get_all_songs():
    conn = create_connection()
    cursor = execute_query(conn, "SELECT title, path FROM songs")
    songs = cursor.fetchall()
    conn.close()
    return songs

def get_all_playlists():
    conn = create_connection()
    cursor = execute_query(conn, "SELECT id, name FROM playlists")
    playlists = cursor.fetchall()
    conn.close()
    return playlists

def get_songs_from_playlist(playlist_id):
    conn = create_connection()
    cursor = execute_query(conn, "SELECT songs.title, songs.path FROM songs INNER JOIN playlist_song_link ON songs.id = playlist_song_link.song_id WHERE playlist_song_link.playlist_id = ?", (playlist_id,))
    songs = cursor.fetchall()
    conn.close()
    return songs


def is_song_in_db(song_title, filepath):
    """Check if the song with title and filepath exists in the songs table."""
    conn = create_connection()
    cursor = execute_query(conn, "SELECT * FROM songs WHERE title=? AND path=?", (song_title, filepath))
    result = cursor.fetchone()
    conn.close()
    return bool(result)

def is_song_in_playlist(song_title, playlist_id):
    """Check if song is in the playlist."""
    conn = create_connection()
    cursor = execute_query(conn, """
        SELECT songs.id
        FROM songs
        INNER JOIN playlist_song_link ON songs.id = playlist_song_link.song_id
        WHERE songs.title = ? AND playlist_song_link.playlist_id = ?
    """, (song_title, playlist_id))
    result = cursor.fetchone()
    conn.close()
    return bool(result)


# Using the existing add_song and add_playlist functions to support our new functions

def add_song_to_playlist_if_not_exists(song_title, song_path, playlist_name):
    """Add song to the songs table if not exists and then add it to the given playlist."""
    
    # Check if song is already in database
    if not is_song_in_db(song_title, song_path):
        song_id = add_song(song_title, song_path)
    else:
        conn = create_connection()
        cursor = execute_query(conn, "SELECT id FROM songs WHERE title=? AND path=?", (song_title, song_path))
        song_id = cursor.fetchone()[0]
        conn.close()

    # Check if playlist exists or create
    conn = create_connection()
    cursor = execute_query(conn, "SELECT id FROM playlists WHERE name=?", (playlist_name,))
    playlist_id_result = cursor.fetchone()
    conn.close()
    if playlist_id_result:
        playlist_id = playlist_id_result[0]
    else:
        add_playlist(playlist_name)
        conn = create_connection()
        cursor = execute_query(conn, "SELECT id FROM playlists WHERE name=?", (playlist_name,))
        playlist_id = cursor.fetchone()[0]
        conn.close()

    # Check if song is already in the playlist and add if not
    if not is_song_in_playlist(song_title, playlist_id):
        link_song_to_playlist(playlist_id, song_id)

def get_song_path(playlist_name, song_title):
    """Query the database to get the path of the song based on its title and playlist name"""
    conn = create_connection()
    query = """
        SELECT s.path
        FROM songs s
        JOIN playlist_songs ps ON s.id = ps.song_id
        JOIN playlists p ON p.id = ps.playlist_id
        WHERE s.title = ? AND p.name = ?
    """
    cursor = execute_query(conn, query, (song_title, playlist_name))
    song_path = cursor.fetchone()[0]
    conn.close()
    return song_path

def get_songs_in_playlist(playlist_name):
    """Query the database to get a list of songs in a specified playlist"""
    conn = create_connection()
    query = """
        SELECT s.title
        FROM songs s
        JOIN playlist_songs ps ON s.id = ps.song_id
        JOIN playlists p ON p.id = ps.playlist_id
        WHERE p.name = ?
    """
    cursor = execute_query(conn, query, (playlist_name,))
    songs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return songs


def get_playlist_name_by_id(playlist_id):
    """Fetch the playlist name by its ID from the database"""
    conn = create_connection()
    cursor = execute_query(conn, "SELECT name FROM playlists WHERE id=?", (playlist_id,))
    playlist_name = cursor.fetchone()[0]
    conn.close()
    return playlist_name



# Initialize tables
create_tables()
