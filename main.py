import requests
import os
import tkinter as tk
import ttkbootstrap as ttk 

#Saves the API key so there's no need to enter it every time.
def set_API_key():
    API_file = open('./API_key.txt', 'w')
    API_key = API_entry_StringVar.get()
    API_file.write(API_key)
    API_file.close()
    API_button_StringVar.set('Saved!')


def download():
    status_label_StringVar.set('')
    root.update()
    
    API_KEY = API_entry_StringVar.get()
    movie_id = ID_entry_StringVar.get()
    
    # Get movie details to retrieve movie title
    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    movie_details_response = requests.get(movie_details_url)
    
    if movie_details_response.status_code != 200:
        status_label_StringVar.set('Error ' + str(movie_details_response.status_code) + ", Please make sure you've entered the right information!")
        return
    
    movie_data = movie_details_response.json()
    movie_title = movie_data.get('title', movie_id)
    # Sanitize movie title for folder name (remove invalid characters)
    movie_folder = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not movie_folder:
        movie_folder = movie_id
    
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
    
    #The url provided by TMDB for retrieving movie images, https://developer.themoviedb.org/reference/movie-images
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={API_KEY}"

    response = requests.get(url)
    
    if response.status_code != 200:
        status_label_StringVar.set('Error ' + str(response.status_code) + ", Please make sure you've entered the right information!")
    else:
        #Using a JSON format for the response so it's easier to sift through
        text = response.json()
        
        #An integer to keep track of the names of the files, 2000x3000 Poster (img_number)
        img_number = 1
        
        #An integer to keep track of the number of files to be downloaded in each category (Backdrops, Logos, Posters)
        category_number = 0
        
        #Deleting the "id" key from the JSON response because it would mess up the for loop as it's numeric and can't be iterated.
        del text["id"]
        
        #Storing the size of every category and making directories
        size = []
        for category in text:
            if category in selected_categories:
                size.append(len(text[f"{category}"]))
                os.makedirs(f"./Images/{movie_folder}/{category.title()}", exist_ok = True)
            else:
                size.append(0)
            
        for category in text:
            if category not in selected_categories:
                continue
                
            status_label_StringVar.set(category.title())
            for image in text[f"{category}"]:
                #Checks every iteration to see if the user has closed the window so it can stop running the script if so
                if root.winfo_viewable():
                    img_url = "https://image.tmdb.org/t/p/original" + image["file_path"]
                    img_extension = image["file_path"].split('.')[1]
                    img_data = requests.get(img_url).content
                    #Saving the image in this format: widthxheight Category (img_number).img_extension
                    # In the Images/MovieFolder/Category/ subdirectory
                    with open(f'Images/{movie_folder}/{category.title()}/{str(image["width"])}x{str(image["height"])} {category.title()[0:-1]} ({str(img_number)}).{img_extension}', 'wb') as handler:
                        handler.write(img_data)
                    progress_label_StringVar.set(str(img_number) + f'/{str(len(text[category]))} Downloaded')
                    root.update()
                    img_number += 1
                else:
                    #If the window has been closed, the program gets killed
                    exit()
            img_number = 1
            category_number += 1
        status_label_StringVar.set('Finished!')
        total_downloaded = sum(len(text[cat]) for cat in selected_categories if cat in text)
        progress_label_StringVar.set(f'{str(total_downloaded)}/{str(total_downloaded)} Downloaded')
        root.update()


#Root definition
root = tk.Tk()
root.title('TMDB-Poster-Downloader')
root.geometry('400x280')                

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
API_input_frame.pack(pady = 20)


# ID inputs
ID_input_frame = ttk.Frame(master = root)
ID_label = ttk.Label(master = ID_input_frame, text = 'Movie ID:')
ID_entry_StringVar = tk.StringVar()
ID_entry = ttk.Entry(master = ID_input_frame, textvariable = ID_entry_StringVar)
ID_label.pack(side = 'left')
ID_entry.pack(side = 'left', padx = 10)
ID_input_frame.pack()

# Category checkboxes
category_frame = ttk.Frame(master = root)
category_label = ttk.Label(master = category_frame, text = 'Categories:')
backdrops_var = tk.BooleanVar(value=True)
logos_var = tk.BooleanVar(value=True)
posters_var = tk.BooleanVar(value=True)
backdrops_check = ttk.Checkbutton(master = category_frame, text = 'Backdrops', variable = backdrops_var)
logos_check = ttk.Checkbutton(master = category_frame, text = 'Logos', variable = logos_var)
posters_check = ttk.Checkbutton(master = category_frame, text = 'Posters', variable = posters_var)
category_label.pack()
backdrops_check.pack(anchor='w', padx=20)
logos_check.pack(anchor='w', padx=20)
posters_check.pack(anchor='w', padx=20)
category_frame.pack(pady = 10)

# Download button
ID_button_frame = ttk.Frame(master = root)
ID_button_StringVar = tk.StringVar()
ID_button_StringVar.set('Download')
ID_button = ttk.Button(master = ID_button_frame, textvariable = ID_button_StringVar, command = download)
ID_button.pack()
ID_button_frame.pack()

#Status
status_label_StringVar = tk.StringVar()
status_label = ttk.Label(master = root, textvariable = status_label_StringVar)
status_label.pack(pady = 10)

#Progress
progress_label_StringVar = tk.StringVar()
progress_label = ttk.Label(master = root, textvariable = progress_label_StringVar)
progress_label.pack()
root.mainloop()