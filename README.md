# radarr-batch-movie-importer

This simple script allows you to pass import movies from https://www.listchallenges.com/lists/movies
into your Radarr library.


# Usage

1. Clone repository
2. Fill 'config.json' with correct values for your server
  * radar_url - url to your radar instance
  * radarr_api_key - Can be found in your Radarr instance under "Settings -> General"
  * qualityProfileId - Id of quality profile to be set on new added movie. Pick one from 1 to 6 (Can be changed later in mass movie editor)
  * rootFolderPath - path to your movie library
  
3. Call script, for example:
```
cd radarr-batch-movie-importer
python3 import.py https://www.listchallenges.com/movies-where-things-happen-out-of-order 
```
You can pass multiple lists, space separated.

Sometimes, there i mismatch in release date in radarr  and list, so 1 year tolerance is used to match correct film.


# Future enhancments
* Import movies from txt file
* Check if movi exists in library before trying to add it
