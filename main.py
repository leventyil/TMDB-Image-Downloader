import requests
import os
import tkinter as tk
import ttkbootstrap as ttk

# Global flag to stop download
stop_download = False
current_media_folder = None

# Saves the API key so there's no need to enter it every time.
def set_API_key():
    API_file = open('./API_key.txt', 'w')
    API_key = API_entry_StringVar.get()
    API_file.write(API_key)
    API_file.close()
    API_button_StringVar.set('Saved!')

def download():
    global stop_download, current_media_folder
    stop_download = False
    stop_button.config(state='normal')
    ID_button.config(state='disabled')
    open_folder_button.config(state='disabled')
    progress_bar['value'] = 0
    # Start spinner (indeterminate mode)
    progress_bar.config(mode='indeterminate')
    progress_bar.start(10)
    status_label_StringVar.set('Loading...')
    root.update()

    API_KEY = API_entry_StringVar.get()
    media_id = ID_entry_StringVar.get()
    media_type = media_type_var.get()  # movie or tv

    # Language options for images
    image_language = image_language_StringVar.get().strip()
    include_image_language = include_image_language_StringVar.get().strip()
    image_lang_params = {}
    if image_language:
        image_lang_params["language"] = image_language
    if include_image_language:
        image_lang_params["include_image_language"] = include_image_language

    # Get media details to retrieve title/name
    media_details_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}"
    details_params = {"api_key": API_KEY}
    if image_language:
        details_params["language"] = image_language
    media_details_response = requests.get(media_details_url, params=details_params)

    if media_details_response.status_code != 200:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        status_label_StringVar.set(
            'Error ' + str(media_details_response.status_code)
            + ", Please make sure you've entered the right information!"
        )
        ID_button.config(state='normal')
        stop_button.config(state='disabled')
        return

    media_data = media_details_response.json()
    # Use 'title' for movies, 'name' for TV shows
    media_title = media_data.get('title' if media_type == 'movie' else 'name', media_id)
    # Get release year
    release_date = media_data.get('release_date' if media_type == 'movie' else 'first_air_date', '')
    media_year = release_date.split('-')[0] if release_date else 'Unknown'
    # Display title and year
    media_info_StringVar.set(f'{media_title} ({media_year})')
    root.update()
    # Sanitize title for folder name (remove invalid characters)
    media_folder = "".join(c for c in media_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not media_folder:
        media_folder = media_id

    current_media_folder = f"./Images/{media_folder}"

    # Get selected categories
    selected_categories = []
    if backdrops_var.get():
        selected_categories.append('backdrops')
    if logos_var.get():
        selected_categories.append('logos')
    if posters_var.get():
        selected_categories.append('posters')

    # Episode backdrops support
    season_val = season_entry_StringVar.get().strip()
    episode_val = episode_entry_StringVar.get().strip()
    if episode_backdrops_var.get():
        if media_type != 'tv':
            progress_bar.stop()
            progress_bar.config(mode='determinate')
            status_label_StringVar.set('Episode backdrops only work for TV shows.')
            ID_button.config(state='normal')
            stop_button.config(state='disabled')
            return

        if all_seasons_var.get():
            # All seasons: no need for season/episode in the GUI
            selected_categories.append('episode_backdrops')
        else:
            # Single season (and maybe single episode)
            if not season_val.isdigit():
                progress_bar.stop()
                progress_bar.config(mode='determinate')
                status_label_StringVar.set('Please enter a numeric season for episode backdrops.')
                ID_button.config(state='normal')
                stop_button.config(state='disabled')
                return
            if episode_val and not episode_val.isdigit():
                progress_bar.stop()
                progress_bar.config(mode='determinate')
                status_label_StringVar.set('Episode must be numeric if provided.')
                ID_button.config(state='normal')
                stop_button.config(state='disabled')
                return
            selected_categories.append('episode_backdrops')

    if not selected_categories:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        status_label_StringVar.set('Please select at least one category!')
        ID_button.config(state='normal')
        stop_button.config(state='disabled')
        return

    # Main images endpoint
    images_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}/images"
    params = {"api_key": API_KEY}
    params.update(image_lang_params)
    response = requests.get(images_url, params=params)

    if response.status_code != 200:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        status_label_StringVar.set(
            'Error ' + str(response.status_code)
            + ", Please make sure you've entered the right information!"
        )
        ID_button.config(state='normal')
        stop_button.config(state='disabled')
        return

    # Using a JSON format for the response so it's easier to sift through
    text = response.json()

    # Episode backdrops: all seasons or single season/episode
    if 'episode_backdrops' in selected_categories:
        episode_backdrops = []

        if all_seasons_var.get():
            # Get TV show details to know which seasons exist
            tv_details_url = f"https://api.themoviedb.org/3/tv/{media_id}"
            tv_params = {"api_key": API_KEY}
            if image_language:
                tv_params["language"] = image_language
            tv_details_response = requests.get(tv_details_url, params=tv_params)
            if tv_details_response.status_code == 200:
                tv_data = tv_details_response.json()
                seasons = tv_data.get("seasons", [])
                for season in seasons:
                    season_number = season.get("season_number")
                    if season_number in (0, None):
                        # Skip specials (season 0) if desired
                        continue

                    season_url = f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                    season_params = {"api_key": API_KEY}
                    if image_language:
                        season_params["language"] = image_language
                    season_response = requests.get(season_url, params=season_params)
                    if season_response.status_code != 200:
                        continue
                    season_data = season_response.json()
                    episodes = season_data.get("episodes", [])

                    for ep in episodes:
                        ep_number = ep.get("episode_number")
                        if not isinstance(ep_number, int):
                            continue
                        episode_url = (
                            f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                            f"/episode/{ep_number}/images"
                        )
                        ep_params = {"api_key": API_KEY}
                        ep_params.update(image_lang_params)
                        episode_response = requests.get(episode_url, params=ep_params)
                        if episode_response.status_code != 200:
                            continue
                        episode_data = episode_response.json()
                        stills = episode_data.get("stills", [])
                        for still in stills:
                            still["__season"] = season_number
                            still["__episode"] = ep_number
                            # try to carry episode title if present
                            still["__episode_name"] = ep.get("name") or ""
                            episode_backdrops.append(still)
            else:
                status_label_StringVar.set(
                    f'Error {tv_details_response.status_code} getting TV details; skipping episode backdrops.'
                )
        else:
            # Single season: either one episode or all episodes in that season
            season_number = int(season_val)

            if episode_val:
                # Single specific episode
                ep_number = int(episode_val)
                episode_url = (
                    f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                    f"/episode/{ep_number}/images"
                )
                ep_params = {"api_key": API_KEY}
                ep_params.update(image_lang_params)
                episode_response = requests.get(episode_url, params=ep_params)
                if episode_response.status_code == 200:
                    episode_data = episode_response.json()
                    stills = episode_data.get("stills", [])
                    # fetch episode details once to get title
                    ep_details_url = (
                        f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                        f"/episode/{ep_number}"
                    )
                    ep_details_params = {"api_key": API_KEY}
                    if image_language:
                        ep_details_params["language"] = image_language
                    ep_details_resp = requests.get(ep_details_url, params=ep_details_params)
                    ep_name = ""
                    if ep_details_resp.status_code == 200:
                        ep_details = ep_details_resp.json()
                        ep_name = ep_details.get("name") or ""
                    for still in stills:
                        still["__season"] = season_number
                        still["__episode"] = ep_number
                        still["__episode_name"] = ep_name
                        episode_backdrops.append(still)
                else:
                    status_label_StringVar.set(
                        f'Error {episode_response.status_code} getting episode images; skipping episode backdrops.'
                    )
            else:
                # No specific episode: all episodes in the season
                season_url = f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                season_params = {"api_key": API_KEY}
                if image_language:
                    season_params["language"] = image_language
                season_response = requests.get(season_url, params=season_params)
                if season_response.status_code == 200:
                    season_data = season_response.json()
                    episodes = season_data.get("episodes", [])
                    for ep in episodes:
                        ep_number = ep.get("episode_number")
                        if not isinstance(ep_number, int):
                            continue
                        episode_url = (
                            f"https://api.themoviedb.org/3/tv/{media_id}/season/{season_number}"
                            f"/episode/{ep_number}/images"
                        )
                        ep_params = {"api_key": API_KEY}
                        ep_params.update(image_lang_params)
                        episode_response = requests.get(episode_url, params=ep_params)
                        if episode_response.status_code != 200:
                            continue
                        episode_data = episode_response.json()
                        stills = episode_data.get("stills", [])
                        for still in stills:
                            still["__season"] = season_number
                            still["__episode"] = ep_number
                            still["__episode_name"] = ep.get("name") or ""
                            episode_backdrops.append(still)
                else:
                    status_label_StringVar.set(
                        f'Error {season_response.status_code} getting season details; skipping episode backdrops.'
                    )

        text['episode_backdrops'] = episode_backdrops

    # An integer to keep track of the names of the files, 2000x3000 Poster (img_number)
    img_number = 1

    # An integer to keep track of the number of files to be downloaded in each category
    category_number = 0

    # Delete the "id" key if present
    if "id" in text:
        del text["id"]

    # Stop spinner and switch to determinate mode
    progress_bar.stop()
    progress_bar.config(mode='determinate')

    # Calculate total images to download for progress bar
    total_images = 0
    for category in text:
        if category in selected_categories:
            if category == 'posters' and high_quality_posters_var.get():
                total_images += sum(1 for image in text[category] if image.get("height", 0) >= 1920)
            else:
                total_images += len(text[category])

    images_processed = 0
    progress_bar['maximum'] = total_images if total_images > 0 else 1

    # Make directories
    for category in text:
        if category in selected_categories:
            os.makedirs(f"./Images/{media_folder}/{category.title()}", exist_ok=True)

    for category in text:
        if category not in selected_categories:
            continue

        # Total images for this category (considering high quality filter for posters)
        if category == 'posters' and high_quality_posters_var.get():
            total_in_category = sum(1 for image in text[category] if image.get("height", 0) >= 1920)
        else:
            total_in_category = len(text[category])

        status_label_StringVar.set(category.title())
        for image in text[f"{category}"]:
            # Check if stop was requested
            if stop_download:
                status_label_StringVar.set('Stopped by user')
                ID_button.config(state='normal')
                stop_button.config(state='disabled')
                return

            if root.winfo_viewable():
                # Skip low quality posters if high quality filter is enabled
                if category == 'posters' and high_quality_posters_var.get() and image.get("height", 0) < 1920:
                    continue

                img_url = "https://image.tmdb.org/t/p/original" + image["file_path"]
                img_extension = image["file_path"].split('.')[-1]

                # Build filename; special case for episode backdrops
                if category == 'episode_backdrops':
                    season_number = int(image.get("__season", season_val or 0))
                    episode_number = int(image.get("__episode", episode_val or 0))
                    se_tag = f'S{season_number:02d}E{episode_number:02d}'
                    # Episode title (sanitized)
                    ep_name_raw = image.get("__episode_name", "") or ""
                    ep_name = "".join(
                        c for c in ep_name_raw
                        if c.isalnum() or c in (' ', '-', '_')
                    ).strip()
                    if not ep_name:
                        ep_name = "Episode"
                    # Season folder path
                    season_folder = f"Season {season_number:02d}"
                    season_dir = os.path.join(
                        "Images",
                        media_folder,
                        category.title(),
                        season_folder
                    )
                    os.makedirs(season_dir, exist_ok=True)
                    filename = (
                        f'{se_tag} {ep_name} '
                        f'{image["width"]}x{image["height"]} '
                        f'Backdrop {img_number:02d}.{img_extension}'
                    )
                    file_path = os.path.join(season_dir, filename)
                else:
                    filename = (
                        f'{image["width"]}x{image["height"]} '
                        f'{category.title()[0:-1]} ({img_number}).{img_extension}'
                    )
                    file_path = f'Images/{media_folder}/{category.title()}/{filename}'

                # Skip if file already exists
                if os.path.exists(file_path):
                    progress_label_StringVar.set(
                        f'{img_number}/{total_in_category} (Skipped - Already exists)'
                    )
                    images_processed += 1
                    progress_bar['value'] = images_processed
                    root.update()
                    img_number += 1
                    continue

                img_data = requests.get(img_url).content
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                progress_label_StringVar.set(f'{img_number}/{total_in_category} Downloaded')
                images_processed += 1
                progress_bar['value'] = images_processed
                root.update()
                img_number += 1
            else:
                # Window closed: exit
                exit()
        img_number = 1
        category_number += 1

    status_label_StringVar.set('Finished!')
    # Calculate total downloaded considering high quality filter
    total_downloaded = 0
    for cat in selected_categories:
        if cat in text:
            if cat == 'posters' and high_quality_posters_var.get():
                total_downloaded += sum(1 for image in text[cat] if image.get("height", 0) >= 1920)
            else:
                total_downloaded += len(text[cat])
    progress_label_StringVar.set(f'{total_downloaded}/{total_downloaded} Downloaded')
    progress_bar['value'] = progress_bar['maximum']
    ID_button.config(state='normal')
    stop_button.config(state='disabled')
    open_folder_button.config(state='normal')
    root.update()

def stop_download_func():
    global stop_download
    stop_download = True

def open_folder():
    global current_media_folder
    if current_media_folder and os.path.exists(current_media_folder):
        absolute_path = os.path.abspath(current_media_folder)
        os.startfile(absolute_path)

# Root definition
root = tk.Tk()
root.title('TMDB-Poster-Downloader')
root.geometry('420x600')
root.minsize(420, 600)

# API inputs
API_input_frame = ttk.Frame(master=root)
API_label = ttk.Label(master=API_input_frame, text='API key:')
API_entry_StringVar = tk.StringVar()
if os.path.exists('API_key.txt'):
    API_key_txt = open('API_key.txt', 'r')
    API_key = API_key_txt.read()
    API_entry_StringVar.set(API_key)
API_entry = ttk.Entry(master=API_input_frame, textvariable=API_entry_StringVar)
API_button_StringVar = tk.StringVar()
API_button_StringVar.set('Save')
API_button = ttk.Button(master=API_input_frame, textvariable=API_button_StringVar, command=set_API_key)
API_label.pack(side='left')
API_entry.pack(side='left', padx=10)
API_button.pack(side='left')
API_input_frame.pack(pady=10, anchor='w', padx=10)

# Image language filters (stacked vertically)
lang_frame = ttk.Frame(master=root)

# Row 1: Image language
image_language_StringVar = tk.StringVar()
lang_label = ttk.Label(lang_frame, text='Language Code (ISO 639-1):')
lang_entry = ttk.Entry(lang_frame, textvariable=image_language_StringVar, width=30)
lang_label.pack(anchor='w')
lang_entry.pack(anchor='w', pady=(0, 4))

# Row 2: Include image languages
include_image_language_StringVar = tk.StringVar()
include_lang_label = ttk.Label(
    lang_frame,
    text='Image Language(s) or null (comma separated):'
)
include_lang_entry = ttk.Entry(
    lang_frame,
    textvariable=include_image_language_StringVar,
    width=30
)
include_lang_label.pack(anchor='w')
include_lang_entry.pack(anchor='w')

lang_frame.pack(anchor='w', padx=10, pady=5)

# Media type selection
media_type_frame = ttk.Frame(master=root)
media_type_label = ttk.Label(master=media_type_frame, text='Media Type:')
media_type_var = tk.StringVar(value='movie')
media_type_movie_radio = ttk.Radiobutton(
    master=media_type_frame, text='Movie', variable=media_type_var, value='movie'
)
media_type_tv_radio = ttk.Radiobutton(
    master=media_type_frame, text='TV Show', variable=media_type_var, value='tv'
)
media_type_label.pack(side='left')
media_type_movie_radio.pack(side='left', padx=5)
media_type_tv_radio.pack(side='left', padx=5)
media_type_frame.pack(pady=10, anchor='w', padx=10)

# ID inputs
ID_input_frame = ttk.Frame(master=root)
ID_label = ttk.Label(master=ID_input_frame, text='Media ID:')
ID_entry_StringVar = tk.StringVar()
ID_entry = ttk.Entry(master=ID_input_frame, textvariable=ID_entry_StringVar)
ID_label.pack(side='left')
ID_entry.pack(side='left', padx=10)
ID_input_frame.pack(anchor='w', padx=10)

# Season and Episode inputs (for TV episodes)
episode_frame = ttk.Frame(master=root)
season_label = ttk.Label(master=episode_frame, text='Season:')
season_entry_StringVar = tk.StringVar()
season_entry = ttk.Entry(master=episode_frame, textvariable=season_entry_StringVar, width=5)

episode_label = ttk.Label(master=episode_frame, text='Episode:')
episode_entry_StringVar = tk.StringVar()
episode_entry = ttk.Entry(master=episode_frame, textvariable=episode_entry_StringVar, width=5)

season_label.pack(side='left')
season_entry.pack(side='left', padx=5)
episode_label.pack(side='left', padx=5)
episode_entry.pack(side='left', padx=5)
episode_frame.pack(anchor='w', padx=10, pady=5)

# Category checkboxes
category_frame = ttk.Frame(master=root)
category_label = ttk.Label(master=category_frame, text='Categories:')
backdrops_var = tk.BooleanVar(value=True)
logos_var = tk.BooleanVar(value=True)
posters_var = tk.BooleanVar(value=True)
episode_backdrops_var = tk.BooleanVar(value=False)
all_seasons_var = tk.BooleanVar(value=False)

def toggle_high_quality_posters():
    if posters_var.get():
        high_quality_posters_check.config(state='normal')
    else:
        high_quality_posters_check.config(state='disabled')
        high_quality_posters_var.set(False)

backdrops_check = ttk.Checkbutton(master=category_frame, text='Backdrops', variable=backdrops_var)
logos_check = ttk.Checkbutton(master=category_frame, text='Logos', variable=logos_var)
posters_check = ttk.Checkbutton(
    master=category_frame, text='Posters', variable=posters_var, command=toggle_high_quality_posters
)
high_quality_posters_var = tk.BooleanVar(value=False)
high_quality_posters_check = ttk.Checkbutton(
    master=category_frame,
    text='High Quality Posters Only (1920px+)',
    variable=high_quality_posters_var
)
episode_backdrops_check = ttk.Checkbutton(
    master=category_frame, text='Episode Backdrops', variable=episode_backdrops_var
)
all_seasons_check = ttk.Checkbutton(
    master=category_frame, text='All Seasons & Episodes', variable=all_seasons_var
)

category_label.pack(anchor='w', padx=10)
backdrops_check.pack(anchor='w', padx=20)
logos_check.pack(anchor='w', padx=20)
posters_check.pack(anchor='w', padx=20)
high_quality_posters_check.pack(anchor='w', padx=40)
episode_backdrops_check.pack(anchor='w', padx=20)
all_seasons_check.pack(anchor='w', padx=40)
category_frame.pack(pady=10, anchor='w')

# Download / Stop / Open Folder buttons
ID_button_frame = ttk.Frame(master=root)
ID_button_StringVar = tk.StringVar()
ID_button_StringVar.set('Download')
ID_button = ttk.Button(master=ID_button_frame, textvariable=ID_button_StringVar, command=download)
stop_button = ttk.Button(master=ID_button_frame, text='Stop', command=stop_download_func, state='disabled')
open_folder_button = ttk.Button(master=ID_button_frame, text='Open Folder', command=open_folder, state='disabled')
ID_button.pack(side='left', padx=5)
stop_button.pack(side='left', padx=5)
open_folder_button.pack(side='left', padx=5)
ID_button_frame.pack(anchor='w', padx=10)

# Progress bar
progress_bar = ttk.Progressbar(master=root, mode='determinate', length=370)
progress_bar.pack(pady=10, anchor='w', padx=10)

# Media info (title and year)
media_info_StringVar = tk.StringVar()
media_info_label = ttk.Label(master=root, textvariable=media_info_StringVar, font=('Arial', 10, 'bold'))
media_info_label.pack(anchor='w', padx=10)

# Status
status_label_StringVar = tk.StringVar()
status_label = ttk.Label(master=root, textvariable=status_label_StringVar)
status_label.pack(pady=10, anchor='w', padx=10)

# Progress
progress_label_StringVar = tk.StringVar()
progress_label = ttk.Label(master=root, textvariable=progress_label_StringVar)
progress_label.pack(anchor='w', padx=10)

root.mainloop()
