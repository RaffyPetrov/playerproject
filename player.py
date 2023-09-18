from tkinter import *
from tkinter import  Button, Listbox, END
import pygame
from tkinter import filedialog
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
import tkinter as tk
import music_play_db_setup as database
import threading
import pygame.mixer

current_song_index = 0
playlist_songs = []


root = Tk()
root.title('Hazelnut Player')
root.geometry("650x1200")
# Load the image
# Initialize Pygame Mixer
pygame.mixer.init()
# Grab Song Length Time Info
#---------------------------------------------------------------------------------------------------------------------------------------
# Create a function for button hover effect
def on_enter(e):
    e.widget['background'] = '#e0e0e0'  # change to a light gray when hovering
def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'  # restore original color when not hovering
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Create a search bar
def search_playlists():
    keyword = search_var.get().lower()  # Retrieving user input from the Entry widget
    all_playlists_listbox.delete(0, tk.END)  # Clear current listbox content
    # Using get_all_playlists that returns a list of (playlist_id, playlist_name)
    all_playlists = database.get_all_playlists()
    for _, playlist_name in all_playlists:
        if keyword in playlist_name.lower():  # Case-insensitive match
            all_playlists_listbox.insert(tk.END, playlist_name)
#Adding more songs to new created playlist in the "Update All Playlists with Songs" frame
def play_next_song():
    global current_song_index, playlist_songs
    if current_song_index < len(playlist_songs):
        _, song_path = playlist_songs[current_song_index]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0)
        # Get song length and start updating time
        song_mut = MP3(song_path)
        global song_length
        song_length = song_mut.info.length
        play_time()
        # Move to the next song index for the next call
        current_song_index += 1
        # Use after to check for song end event every 500 milliseconds (half a second)
        root.after(500, check_for_song_end)
def check_for_song_end():
    if not pygame.mixer.music.get_busy():
        play_next_song()
        return
    # If song didn't end, check again after half a second
    root.after(500, check_for_song_end)
def check_song_status():
    global playlist_songs
    if pygame.mixer.music.get_busy():
        # If the song is still playing, check again after 1 second
        root.after(1000, check_song_status)
    else:
        # If the song is done, play the next one
        play_next_song()
def create_new_playlist():
    playlist_name = simpledialog.askstring("New Playlist", "Enter the name of the new playlist:")
    if playlist_name:
        database.add_playlist(playlist_name)
        playlist_listbox.insert(tk.END, playlist_name)
        update_all_playlists_with_songs()
def song_addition_handler():
    # Check if a playlist is selected
    if not playlist_listbox.curselection():
        messagebox.showwarning("No Selection", "Please select a playlist before adding a song.")
        return 
    song_path = filedialog.askopenfilename(initialdir='/', title="Choose A Song", filetypes=(("mp3 Files", "*.mp3"),))
    if song_path:
        selected_playlist_name = playlist_listbox.get(playlist_listbox.curselection())
        database.add_song_to_playlist(selected_playlist_name, song_path)
        update_song_listbox()
        update_all_playlists_with_songs()
def update_song_listbox():
    songs_listbox.delete(0, tk.END)
    
    if not playlist_listbox.curselection():
        return
    selected_playlist_name = playlist_listbox.get(playlist_listbox.curselection())
    # Get playlist_id from the name
    playlists = database.get_all_playlists()
    for p_id, p_name in playlists:
        if p_name == selected_playlist_name:
            playlist_id = p_id
            break  
    songs = database.get_songs_from_playlist(playlist_id)
    for song_title, _ in songs:
        songs_listbox.insert(tk.END, song_title)
def update_all_playlists_with_songs():
    all_playlists_listbox.delete(0, tk.END)
    playlists = database.get_all_playlists()
    for p_id, playlist_name in playlists:
        all_playlists_listbox.insert(tk.END, playlist_name)
        songs = database.get_songs_from_playlist(p_id)
        for song_title, _ in songs:
            all_playlists_listbox.insert(tk.END, f'    {song_title}')
def play_playlist():
    global playlist_songs, current_song_index
    # Helper function to find playlist ID by name
    def get_playlist_id_by_name(name):
        for p_id, p_name in database.get_all_playlists():
            if p_name == name:
                return p_id
        return None
    # Check if a playlist is selected in either listbox
    selected_playlist_name = None
    if all_playlists_listbox.curselection():
        selected_playlist_name = all_playlists_listbox.get(all_playlists_listbox.curselection())
    elif playlist_listbox.curselection():
        selected_playlist_name = playlist_listbox.get(playlist_listbox.curselection())
    # If no playlist is selected in both listboxes
    if not selected_playlist_name:
        messagebox.showwarning("No Selection", "Please select a playlist before playing.")
        return
    playlist_id = get_playlist_id_by_name(selected_playlist_name)
    if not playlist_id:
        messagebox.showwarning("Error", "Selected playlist not found in the database.")
        return
    playlist_songs = database.get_songs_from_playlist(playlist_id) 
    # Check if songs are available in the selected playlist
    if not playlist_songs:
        messagebox.showwarning("No Songs", f"No songs found in the playlist: {selected_playlist_name}")
        return
    # Reset the current song index
    current_song_index = 0
    # Start playing songs on a separate thread
    thread = threading.Thread(target=play_next_song)
    thread.start()
def play_time():
    # Check for double timing
    if stopped:
        return
    # Grab Current Song Elapsed Time
    current_time = pygame.mixer.music.get_pos() / 1000
    # convert to time format
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
    # Get Currently Playing Song
    # current_song = song_box.curselection()
    # Grab song title from playlist
    song = song_box.get(ACTIVE)
    # add directory structure and mp3 to song title
    song = f'C:/Users/swift/Desktop/playerproject/audio/{song}.mp3'
    # Load Song with Mutagen
    song_mut = MP3(song)
    # Get song Length
    global song_length
    song_length = song_mut.info.length
    # Convert to Time Format
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
    # Increase current time by 1 second
    current_time += 1
    if int(my_slider.get()) == int(song_length):
        status_bar.config(text=f'Time Elapsed: {converted_song_length}  of  {converted_song_length}  ')
    elif paused:
        pass
    elif int(my_slider.get()) == int(current_time):
        # Update Slider To position
        slider_position = int(song_length)
        my_slider.config(to=slider_position, value=int(current_time))
    else:
        # Update Slider To position
        slider_position = int(song_length)
        my_slider.config(to=song_length, value=current_time)
        # convert to time format
        converted_current_time = time.strftime('%M:%S', time.gmtime(int(my_slider.get())))
        # Output time to status bar
        status_bar.config(text=f'Time Elapsed: {converted_current_time}  of  {converted_song_length}  ')
        # Move this thing along by one second
        next_time = int(my_slider.get()) + 1
        my_slider.config(value=next_time)
    # Output time to status bar
    # status_bar.config(text=f'Time Elapsed: {converted_current_time}  of  {converted_song_length}  ')
    # Update slider position value to current song position...
    # my_slider.config(value=int(current_time))
    # update time
    status_bar.after(1000, play_time)
# Add Song Function
def add_song():
    song = filedialog.askopenfilename(initialdir='audio/', title="Choose A Song", filetypes=(("mp3 Files", "*.mp3"), ))
    # strip out the directory info and .mp3 extension from the song name
    song = song.replace("C:/Users/swift/Desktop/playerproject/audio/", "")
    song = song.replace(".mp3", "")
    # Add song to listbox
    song_box.insert(END, song)
# Add many songs to playlist
def add_many_songs():
    songs = filedialog.askopenfilenames(initialdir='audio/', title="Choose A Song", filetypes=(("mp3 Files", "*.mp3"), ))
    # Loop thru song list and replace directory info and mp3
    for song in songs:
        song = song.replace("C:/Users/swift/Desktop/playerproject/audio/", "")
        song = song.replace(".mp3", "")
        # Insert into playlist
        song_box.insert(END, song)
# Play selected song
def play():
    # Set Stopped Variable To False So Song Can Play
    global stopped
    stopped = False
    song = song_box.get(ACTIVE)
    song = f'C:/Users/swift/Desktop/playerproject/audio/{song}.mp3'
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)
    # Call the play_time function to get song length
    play_time()
    # Update Slider To position
    # slider_position = int(song_length)
    # my_slider.config(to=slider_position, value=0)
    # Get current volume
    # current_volume = pygame.mixer.music.get_volume()
    # slider_label.config(text=current_volume * 100)
    # Get current Volume
    current_volume = pygame.mixer.music.get_volume()
    # Times by 100 to make it easier to work with
    current_volume = current_volume * 100
    # slider_label.config(text=current_volume * 100)
    # Change Volume Meter Picture
    if int(current_volume) < 1:
        volume_meter.config(image=vol0)
    elif int(current_volume) > 0 and int(current_volume) <= 25:
        volume_meter.config(image=vol1)
    elif int(current_volume) >= 25 and int(current_volume) <= 50:
        volume_meter.config(image=vol2)
    elif int(current_volume) >= 50 and int(current_volume) <= 75:
        volume_meter.config(image=vol3)
    elif int(current_volume) >= 75 and int(current_volume) <= 100:
        volume_meter.config(image=vol4)
# Stop playing current song
global stopped
stopped = False
def stop():
    # Reset Slider and Status Bar
    status_bar.config(text='')
    my_slider.config(value=0)
    # Stop Song From Playing
    pygame.mixer.music.stop()
    song_box.selection_clear(ACTIVE)
    # Clear The Status Bar
    status_bar.config(text='')
    # Set Stop Variable To True
    global stopped
    stopped = True
    # Get current Volume
    current_volume = pygame.mixer.music.get_volume()
    # Times by 100 to make it easier to work with
    current_volume = current_volume * 100
    # Change Volume Meter Picture
    if int(current_volume) < 1:
        volume_meter.config(image=vol0)
    elif int(current_volume) > 0 and int(current_volume) <= 25:
        volume_meter.config(image=vol1)
    elif int(current_volume) >= 25 and int(current_volume) <= 50:
        volume_meter.config(image=vol2)
    elif int(current_volume) >= 50 and int(current_volume) <= 75:
        volume_meter.config(image=vol3)
    elif int(current_volume) >= 75 and int(current_volume) <= 100:
        volume_meter.config(image=vol4)
# Play The Next Song in the playlist
def next_song():
    global current_song_index, playlist_songs
    # Check if playlist_songs is empty
    if not playlist_songs:
        return
    # Increment current song index
    current_song_index += 1
    # If it's the last song, go back to the first one
    if current_song_index >= len(playlist_songs):
        current_song_index = 0
    song_title, song_path = playlist_songs[current_song_index]
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play(loops=0)
    song_box.selection_clear(0, tk.END)
    song_box.activate(current_song_index)
    song_box.selection_set(current_song_index)
def previous_song():
    global current_song_index, playlist_songs
    # Check if playlist_songs is empty
    if not playlist_songs:
        return
    # Decrement current song index
    current_song_index -= 1
    # If it's the first song, go to the last one
    if current_song_index < 0:
        current_song_index = len(playlist_songs) - 1
    song_title, song_path = playlist_songs[current_song_index]
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play(loops=0)
    song_box.selection_clear(0, tk.END)
    song_box.activate(current_song_index)
    song_box.selection_set(current_song_index)
# Delete A Song
def delete_song():
    stop()
    # Delete Currently Selected Song
    song_box.delete(ANCHOR)
    # Stop Music if it's playing
    pygame.mixer.music.stop()
# Delete All Songs from Playlist
def delete_all_songs():
    stop()
    # Delete All Songs
    song_box.delete(0, END)
    # Stop Music if it's playing
    pygame.mixer.music.stop()
# Create Global Pause Variable
global paused
paused = False
# Pause and Unpause The Current Song
def pause(is_paused):
    global paused
    paused = is_paused
    if paused:
        # Unpause
        pygame.mixer.music.unpause()
        paused = False
    else:
        # Pause
        pygame.mixer.music.pause()
        paused = True
# Create slider function
def slide(x):
    global current_song_index, playlist_songs
    song_position = int(my_slider.get())
    pygame.mixer.music.set_pos(song_position)
    # Ensure there are songs in the playlist_songs and a valid index
    if playlist_songs and 0 <= current_song_index < len(playlist_songs):
        song_title, song_path = playlist_songs[current_song_index]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0, start=int(my_slider.get()))
# Create Volume Function
def volume(x):
    pygame.mixer.music.set_volume(volume_slider.get())
    # Get current Volume
    current_volume = pygame.mixer.music.get_volume()
    # Times by 100 to make it easier to work with
    current_volume = current_volume * 100
    # slider_label.config(text=current_volume * 100)
    # Change Volume Meter Picture
    if int(current_volume) < 1:
        volume_meter.config(image=vol0)
    elif int(current_volume) > 0 and int(current_volume) <= 25:
        volume_meter.config(image=vol1)
    elif int(current_volume) >= 25 and int(current_volume) <= 50:
        volume_meter.config(image=vol2)
    elif int(current_volume) >= 50 and int(current_volume) <= 75:
        volume_meter.config(image=vol3)
    elif int(current_volume) >= 75 and int(current_volume) <= 100:
        volume_meter.config(image=vol4)
# Store the current playing status (to check if a song is already playing)
is_playing = False
# Function to play selected song
def play_selected_song():
    selected_song = songs_listbox.get(songs_listbox.curselection())
    playlist_name = playlist_listbox.get(playlist_listbox.curselection())
    song_path = database.get_song_path(playlist_name, selected_song)  # Implement this function to get the song path
    global is_playing
    if song_path:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        is_playing = True
# Function to play the selected playlist
def play_selected_playlist():
    selected_playlist = playlist_listbox.get(playlist_listbox.curselection())
    songs = database.get_songs_in_playlist(selected_playlist)  # Implement this function to get the songs in the playlist
    global is_playing
    if songs:
        # Stop any currently playing song
        pygame.mixer.music.stop()
        # Play each song in the playlist one by one
        for song in songs:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue  # Wait for the song to finish playing
        is_playing = True
#-------------------------------------------------------------------------------------------------------------------------------------------------------
#GUI Components
# Create Master Frame
master_frame = Frame(root)
master_frame.pack(pady=20)
# Create Playlist Box
song_box = Listbox(master_frame, bg="darkolivegreen1", fg="darkolivegreen1", width=80, selectbackground="white", selectforeground="black")
song_box.grid(row=0, column=0)
# define player Control Buttons Images
back_btn_img = PhotoImage(file='buttons/back50.png')
forward_btn_img = PhotoImage(file='buttons/forward50.png')
play_btn_img = PhotoImage(file='buttons/play50.png')
pause_btn_img = PhotoImage(file='buttons/pause50.png')
stop_btn_img = PhotoImage(file='buttons/stop50.png')
# Define Volume Control Images
global vol0
global vol1
global vol2
global vol3
global vol4
vol0 = PhotoImage(file='images/volume0.png')
vol1 = PhotoImage(file='images/volume1.png')
vol2 = PhotoImage(file='images/volume2.png')
vol3 = PhotoImage(file='images/volume3.png')
vol4 = PhotoImage(file='images/volume4.png')
# Create Player Control Frame
controls_frame = Frame(master_frame)
controls_frame.grid(row=1, column=0, pady=20)
# Create Volume Meter
volume_meter = Label(master_frame, image=vol0)
volume_meter.grid(row=1, column=1, padx=10)
# Create Volume Label Frame
volume_frame = LabelFrame(master_frame, text="Volume")
volume_frame.grid(row=0, column=1, padx=30)
# Create Player Control Buttons
back_button = Button(controls_frame, image=back_btn_img, borderwidth=0, command=previous_song)
forward_button = Button(controls_frame, image=forward_btn_img, borderwidth=0, command=next_song)
play_button = Button(controls_frame, image=play_btn_img, borderwidth=0, command=play)
pause_button = Button(controls_frame, image=pause_btn_img, borderwidth=0, command=lambda: pause(paused))
stop_button = Button(controls_frame, image=stop_btn_img, borderwidth=0, command=stop)
back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)
# Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)
# Create Add Song Menu
add_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Add Songs", menu=add_song_menu)
add_song_menu.add_command(label="Add One Song To Playlist", command=add_song)
# Add Many Songs to playlist
add_song_menu.add_command(label="Add Many Songs To Playlist", command=add_many_songs)
# Create Delete Song Menu
remove_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Remove Songs", menu=remove_song_menu)
remove_song_menu.add_command(label="Delete A Song From Playlist", command=delete_song)
remove_song_menu.add_command(label="Delete All Songs From Playlist", command=delete_all_songs)
# Create Status Bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)
# Create Music Position Slider
my_slider = ttk.Scale(master_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=360)
my_slider.grid(row=2, column=0, pady=10)
# Create Volume Slider
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient=VERTICAL, value=1, command=volume, length=125)
volume_slider.pack(pady=10)
#---------------------------------------------------------------------------------------------------------------------------------------
# Frames for organization
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, padx=20, pady=10)

middle_frame = tk.Frame(root)  # Frame for buttons
middle_frame.pack(fill=tk.X, padx=20, pady=10)

bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, padx=20, pady=10)
#-------------------------------------------------------------------------------------------------------------------------------------------
# Frame and Listbox for displaying playlists
playlist_frame = tk.Frame(top_frame, bd=2, relief="ridge")
playlist_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

playlist_label = tk.Label(playlist_frame, text="Playlists:")
playlist_label.pack()

playlist_listbox = tk.Listbox(playlist_frame, bg="darkolivegreen1")  # Set the background color here
playlist_listbox.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
playlist_scrollbar = tk.Scrollbar(playlist_frame, orient="vertical", command=playlist_listbox.yview)
playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
playlist_listbox.config(yscrollcommand=playlist_scrollbar.set)
btn_create_playlist = tk.Button(playlist_frame, text="Create New Playlist", command=create_new_playlist)
btn_create_playlist.pack(pady=5)

# Frame and Listbox for displaying songs of selected playlist
songs_frame = tk.Frame(top_frame, bd=2, relief="ridge")
songs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

songs_label = tk.Label(songs_frame, text="Songs in selected Playlist:")
songs_label.pack()
songs_listbox = tk.Listbox(songs_frame, bg="darkolivegreen1")  # Set the background color here
songs_listbox.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
songs_scrollbar = tk.Scrollbar(songs_frame, orient="vertical", command=songs_listbox.yview)
songs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
songs_listbox.config(yscrollcommand=songs_scrollbar.set)
btn_add_song = tk.Button(songs_frame, text="Add Song to Selected Playlist", command=song_addition_handler)
btn_add_song.pack(pady=5)
btn_play_playlist = tk.Button(songs_frame, text="Play Selected Playlist", command=play_playlist)
btn_play_playlist.pack(pady=5)

#--------------------------------------------------------------------------------------------------------------------------------------------
# Frame and Listbox for displaying all playlists with songs
all_playlists_frame = tk.Frame(bottom_frame, bd=2, relief="ridge")
all_playlists_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Entry and button for search, packed at the top
search_var = tk.StringVar()
search_entry = tk.Entry(all_playlists_frame, textvariable=search_var)
search_entry.pack(pady=5)
search_button = tk.Button(all_playlists_frame, text="Search", command=search_playlists)
search_button.pack(pady=5)

all_playlists_label = tk.Label(all_playlists_frame, text="All Playlists with songs:")
all_playlists_label.pack(pady=5)

# Use an inner frame to separate the Listbox and its Scrollbar from the buttons for cleaner design
inner_frame = tk.Frame(all_playlists_frame)
inner_frame.pack(fill=tk.BOTH, expand=True)

all_playlists_listbox = tk.Listbox(inner_frame, width=50, bg="darkolivegreen1")
all_playlists_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, pady=5)

all_playlists_scrollbar = tk.Scrollbar(inner_frame, orient="vertical", command=all_playlists_listbox.yview)
all_playlists_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
all_playlists_listbox.config(yscrollcommand=all_playlists_scrollbar.set)

# Pack buttons vertically below each other
btn_update_all_playlists = tk.Button(all_playlists_frame, text="Show all playlists with songs", command=update_all_playlists_with_songs)
btn_update_all_playlists.pack(fill=tk.X, padx=5, pady=5)

root.configure(bg='darkolivegreen1')  # or any other color you prefer
root.mainloop() 