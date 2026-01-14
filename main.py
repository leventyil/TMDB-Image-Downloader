import requests
import os
import tkinter as tk
import ttkbootstrap as ttk 

# Global flag to stop download
stop_download = False
current_media_folder = None 

#Saves the API key so there's no need to enter it every time.
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
    media_type = media_type_var.get()  # Get selected media type (movie or tv)
    
    # Get media details to retrieve title/name
    media_details_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}?api_key={API_KEY}"
    media_details_response = requests.get(media_details_url)
    
    if media_details_response.status_code != 200:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        status_label_StringVar.set('Error ' + str(media_details_response.status_code) + ", Please make sure you've entered the right information!")
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
    
    if not selected_categories:
        status_label_StringVar.set('Please select at least one category!')
        return
    
    #The url provided by TMDB for retrieving images
    url = f"https://api.themoviedb.org/3/{media_type}/{media_id}/images?api_key={API_KEY}"

    response = requests.get(url)
    
    if response.status_code != 200:
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        status_label_StringVar.set('Error ' + str(response.status_code) + ", Please make sure you've entered the right information!")
        ID_button.config(state='normal')
        stop_button.config(state='disabled')
    else:
        #Using a JSON format for the response so it's easier to sift through
        text = response.json()
        
        #An integer to keep track of the names of the files, 2000x3000 Poster (img_number)
        img_number = 1
        
        #An integer to keep track of the number of files to be downloaded in each category (Backdrops, Logos, Posters)
        category_number = 0
        
        #Deleting the "id" key from the JSON response because it would mess up the for loop as it's numeric and can't be iterated.
        del text["id"]
        
        # Stop spinner and switch to determinate mode
        progress_bar.stop()
        progress_bar.config(mode='determinate')
        
        # Calculate total images to download for progress bar
        total_images = sum(len(text[category]) for category in text if category in selected_categories)
        if high_quality_posters_var.get() and 'posters' in selected_categories:
            # Adjust for high quality filter
            total_images -= sum(1 for image in text['posters'] if image["height"] < 1920)
        
        images_processed = 0
        progress_bar['maximum'] = total_images
        
        #Storing the size of every category and making directories
        size = []
        for category in text:
            if category in selected_categories:
                size.append(len(text[f"{category}"]))
                os.makedirs(f"./Images/{media_folder}/{category.title()}", exist_ok = True)
            else:
                size.append(0)
            
        for category in text:
            if category not in selected_categories:
                continue
            
            # Calculate total images for this category (considering high quality filter for posters)
            if category == 'posters' and high_quality_posters_var.get():
                total_in_category = sum(1 for image in text[category] if image["height"] >= 1920)
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
                
                #Checks every iteration to see if the user has closed the window so it can stop running the script if so
                if root.winfo_viewable():
                    # Skip low quality posters if high quality filter is enabled
                    if category == 'posters' and high_quality_posters_var.get() and image["height"] < 1920:
                        continue
                    
                    img_url = "https://image.tmdb.org/t/p/original" + image["file_path"]
                    img_extension = image["file_path"].split('.')[1]
                    #Saving the image in this format: widthxheight Category (img_number).img_extension
                    # In the Images/MediaFolder/Category/ subdirectory
                    file_path = f'Images/{media_folder}/{category.title()}/{str(image["width"])}x{str(image["height"])} {category.title()[0:-1]} ({str(img_number)}).{img_extension}'
                    
                    # Skip if file already exists
                    if os.path.exists(file_path):
                        progress_label_StringVar.set(str(img_number) + f'/{str(total_in_category)} (Skipped - Already exists)')
                        images_processed += 1
                        progress_bar['value'] = images_processed
                        root.update()
                        img_number += 1
                        continue
                    
                    img_data = requests.get(img_url).content
                    with open(file_path, 'wb') as handler:
                        handler.write(img_data)
                    progress_label_StringVar.set(str(img_number) + f'/{str(total_in_category)} Downloaded')
                    images_processed += 1
                    progress_bar['value'] = images_processed
                    root.update()
                    img_number += 1
                else:
                    #If the window has been closed, the program gets killed
                    exit()
            img_number = 1
            category_number += 1
        status_label_StringVar.set('Finished!')
        # Calculate total downloaded considering high quality filter
        total_downloaded = 0
        for cat in selected_categories:
            if cat in text:
                if cat == 'posters' and high_quality_posters_var.get():
                    total_downloaded += sum(1 for image in text[cat] if image["height"] >= 1920)
                else:
                    total_downloaded += len(text[cat])
        progress_label_StringVar.set(f'{str(total_downloaded)}/{str(total_downloaded)} Downloaded')
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
        # Convert to absolute path for Windows
        absolute_path = os.path.abspath(current_media_folder)
        os.startfile(absolute_path)


#Root definition
root = tk.Tk()
root.title('TMDB-Poster-Downloader')
root.geometry('400x430')                

# API inputs
API_input_frame = ttk.Frame(master = root)
API_label = ttk.Label(master = API_input_frame, text = 'API key:')
API_entry_StringVar = tk.StringVar()
if os.path.exists('API_key.txt'):
    API_key_txt = open('API_key.txt', 'r')
    API_key = API_key_txt.read()
    API_entry_StringVar.set(API_key)
API_entry = ttk.Entry(master = API_input_frame, textvariable = API_entry_StringVar)
API_button_StringVar = tk.StringVar()
API_button_StringVar.set('Save')
API_button = ttk.Button(master = API_input_frame, textvariable = API_button_StringVar, command = set_API_key)
API_label.pack(side = 'left')
API_entry.pack(side = 'left', padx = 10)
API_button.pack(side = 'left')
API_input_frame.pack(pady = 20, anchor='w', padx=10)


# Media type selection
media_type_frame = ttk.Frame(master = root)
media_type_label = ttk.Label(master = media_type_frame, text = 'Media Type:')
media_type_var = tk.StringVar(value='movie')
media_type_movie_radio = ttk.Radiobutton(master = media_type_frame, text = 'Movie', variable = media_type_var, value = 'movie')
media_type_tv_radio = ttk.Radiobutton(master = media_type_frame, text = 'TV Show', variable = media_type_var, value = 'tv')
media_type_label.pack(side = 'left')
media_type_movie_radio.pack(side = 'left', padx = 5)
media_type_tv_radio.pack(side = 'left', padx = 5)
media_type_frame.pack(pady = 10, anchor='w', padx=10)

# ID inputs
ID_input_frame = ttk.Frame(master = root)
ID_label = ttk.Label(master = ID_input_frame, text = 'Media ID:')
ID_entry_StringVar = tk.StringVar()
ID_entry = ttk.Entry(master = ID_input_frame, textvariable = ID_entry_StringVar)
ID_label.pack(side = 'left')
ID_entry.pack(side = 'left', padx = 10)
ID_input_frame.pack(anchor='w', padx=10)

# Category checkboxes
category_frame = ttk.Frame(master = root)
category_label = ttk.Label(master = category_frame, text = 'Categories:')
backdrops_var = tk.BooleanVar(value=True)
logos_var = tk.BooleanVar(value=True)
posters_var = tk.BooleanVar(value=True)

# Function to toggle high quality posters checkbox
def toggle_high_quality_posters():
    if posters_var.get():
        high_quality_posters_check.config(state='normal')
    else:
        high_quality_posters_check.config(state='disabled')
        high_quality_posters_var.set(False)

backdrops_check = ttk.Checkbutton(master = category_frame, text = 'Backdrops', variable = backdrops_var)
logos_check = ttk.Checkbutton(master = category_frame, text = 'Logos', variable = logos_var)
posters_check = ttk.Checkbutton(master = category_frame, text = 'Posters', variable = posters_var, command = toggle_high_quality_posters)
high_quality_posters_var = tk.BooleanVar(value=False)
high_quality_posters_check = ttk.Checkbutton(master = category_frame, text = 'High Quality Posters Only (1920px+)', variable = high_quality_posters_var)
category_label.pack(anchor='w', padx=10)
backdrops_check.pack(anchor='w', padx=20)
logos_check.pack(anchor='w', padx=20)
posters_check.pack(anchor='w', padx=20)
high_quality_posters_check.pack(anchor='w', padx=40)
category_frame.pack(pady = 10, anchor='w')

# Download button
ID_button_frame = ttk.Frame(master = root)
ID_button_StringVar = tk.StringVar()
ID_button_StringVar.set('Download')
ID_button = ttk.Button(master = ID_button_frame, textvariable = ID_button_StringVar, command = download)
stop_button = ttk.Button(master = ID_button_frame, text = 'Stop', command = stop_download_func, state='disabled')
open_folder_button = ttk.Button(master = ID_button_frame, text = 'Open Folder', command = open_folder, state='disabled')
ID_button.pack(side='left', padx=5)
stop_button.pack(side='left', padx=5)
open_folder_button.pack(side='left', padx=5)
ID_button_frame.pack(anchor='w', padx=10)

# Progress bar
progress_bar = ttk.Progressbar(master = root, mode='determinate', length=370)
progress_bar.pack(pady=10, anchor='w', padx=10)

# Media info (title and year)
media_info_StringVar = tk.StringVar()
media_info_label = ttk.Label(master = root, textvariable = media_info_StringVar, font=('Arial', 10, 'bold'))
media_info_label.pack(anchor='w', padx=10)

#Status
status_label_StringVar = tk.StringVar()
status_label = ttk.Label(master = root, textvariable = status_label_StringVar)
status_label.pack(pady = 10, anchor='w', padx=10)

#Progress
progress_label_StringVar = tk.StringVar()
progress_label = ttk.Label(master = root, textvariable = progress_label_StringVar)
progress_label.pack(anchor='w', padx=10)
root.mainloop()