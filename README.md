<img src="TMDB-Poster-Downloader-Logo.png">
<h1 align = "center">TMDB-Image-Downloader</h1>
<p align = "center">
A simple program written in Python that receives a TMDB API key and a movie or TV show ID and downloads images (posters, backdrops, logos, and TV episode stills) available on TMDB.
</p>

## Thank you
Thank you to Erfangholiz for the initial program and leventyil for their commit enhancements.

## Features

- Download posters, backdrops, and logos for movies and TV shows
- Download TV episode backdrops:
  - Single episode (Season + Episode)
  - All episodes in one season
  - All seasons (all episodes in the show)
- Optional high quality posters filter (only posters with height ≥ 1920px)
- Per-image progress updates and overall progress bar
- Image language options using TMDB’s `language` and `include_image_language` parameters

## Use cases

- Backdrops can be used in reviews and analyses relevant to the movie or episode they're about (e.g. the original project used a backdrop from TMDB for
  <a href="https://medium.com/@erfan1382gh/a-complete-breakdown-of-annette-2021-from-start-to-finish-8b7c28e39d94">this analysis on Annette (2021)</a>).

- Logos can be indispensable for video essayists especially because a lot of the ones provided by TMDB have transparent backgrounds which makes them great for thumbnails.

- Posters can be a great encapsulation of the marketing techniques used in the industry at the time; they can also give you great contrast when compared to posters from other countries which are sometimes also provided on the website.

- Episode backdrops (stills) are useful for creating thumbnails, episode guides, or artwork that needs a specific scene from a TV episode.

Posters, backdrops, logos, and episode stills can be a very neat thing for all movie and TV enthusiasts.

## Folder and filename layout

All images are stored under the `Images/` directory, grouped by media title (sanitized).

### Movies and TV show-level images

- `Images/<Title>/Posters/...`
- `Images/<Title>/Backdrops/...`
- `Images/<Title>/Logos/...`

Filenames follow the pattern:

- `<width>x<height> Poster (N).jpg`
- `<width>x<height> Backdrop (N).jpg`
- `<width>x<height> Logo (N).png`

### TV episode backdrops

Episode backdrops are organized per season:

- `Images/<Title>/Episode_backdrops/Season 01/`
- `Images/<Title>/Episode_backdrops/Season 02/`
- etc.

Filenames include season/episode code, episode title, resolution, and an index:

- `S01E01 Pilot 1920x1080 Backdrop 01.jpg`
- `S01E01 Pilot 1280x720 Backdrop 02.jpg`

If an episode title is not available from TMDB, a generic `Episode` label is used instead.

## Image language options

The app exposes two TMDB image language parameters:

- **Language Code (ISO 639-1)** → TMDB `language` parameter  
- **Image Language(s) or null (comma separated)** → TMDB `include_image_language` parameter

Common setups:

- Prefer Dutch images and language-less artwork:
  - Language Code: `nl`
  - Image Language(s): `nl,null`
- Accept all languages:
  - Leave both fields empty.

For more details on how TMDB handles image languages, see the TMDB documentation.

## How to Use

1. Acquire a TMDB API key. There are several guides online; creating an account and getting the key should take less than five minutes.
2. Download the latest version or clone the source:

   ```bash
   git clone TMDB-Poster-Downloader

   cd TMDB-Poster-Downloader/

   python main.py
3. Enter your TMDB API key and click **Save** (only needed on first run or when your key changes).

4. Choose **Media Type** (`Movie` or `TV Show`).

5. Enter the **Media ID** (from the TMDB URL). For example, this is the URL for *Slaughterhouse-Five* (1972):

`https://www.themoviedb.org/movie/24559-slaughterhouse-five`

The Movie ID is:`24559`

**Optional, for TV shows:**

Enter **Season** and/or **Episode** and enable **Episode Backdrops**:

- Season + Episode + Episode Backdrops (All Seasons off) → that one episode.  
- Season only + Episode Backdrops (All Seasons off) → all episodes in that season.  
- Episode Backdrops + All Seasons (episodes) → all seasons and episodes.

Select which categories you want (Backdrops, Logos, Posters, Episode Backdrops), adjust language options if desired, and click **Download**.
