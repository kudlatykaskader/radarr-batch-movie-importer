#!/usr/bin/python3

import os
import sys
import requests
import re
import json
import pathlib
import argparse
import urllib.parse
import html

class List:
    def __init__(self, url, id):
        self.url = url
        self.id = id

    def __str__(self):
        return "Id: {}, url: {}".format(self.url, self.id)
        
class Movie:
    def __init__(self, name, year):
        self.name = name
        self.year = year
        self.radarr_info = None
    
    def __str__(self):
        return "Title: {}, year: {}".format(self.name, self.year)
    
    
def get_list_id(url):
    page = get_page_content(url)
    x = re.search("(?<=\/print-list\/)\d+", page)
    return x.group() if x else None
    
    
def get_page_content(url):
    return requests.get(url = url).text
    
def get_config():
    return json.loads(pathlib.Path("config.json").read_text())

def radarr_search_movie(name, year):
    config = get_config()
    encoded_name = urllib.parse.quote_plus(html.unescape(name))
    radarr_url = "http://{}/api/movie/lookup?term={}&apikey={}".format(config["radarr_url"], encoded_name, config["radarr_api_key"])
    r = requests.get(url = radarr_url).json()
    for search_result in r:
        if search_result["year"] in range(int(year) - 2, int(year) + 2):
            return search_result
    return None
    #print(json.dumps(r, indent=4, sort_keys=True))

def radarr_add_movie(movie):    
    radarr_url = "http://{}/api/movie?apikey={}".format(config["radarr_url"], config["radarr_api_key"])
    
    radarr_data = {}
    radarr_data["title"] = movie.radarr_info["title"]
    radarr_data["qualityProfileId"] = config["qualityProfileId"]
    radarr_data["titleSlug"] = movie.radarr_info["titleSlug"]
    radarr_data["images"] = movie.radarr_info["images"]
    radarr_data["tmdbId"] = movie.radarr_info["tmdbId"]
    radarr_data["year"] = movie.radarr_info["year"]
    radarr_data["rootFolderPath"] = config["rootFolderPath"]

    radarr_data = json.dumps(radarr_data)
    radarr_data = str(radarr_data)
    radarr_data = radarr_data.encode('utf-8')
    headers = {'Content-Type': 'application/json', 'charset': 'utf-8'}
    
    r = requests.post(url = radarr_url, data = radarr_data, headers = headers)
    
    if r.status_code == 201:
        print("Added '{}' to Radarr library".format(movie.name))
        return 0
    elif r.status_code == 400:
        print("Movie already exists: {}".format(movie.name, r.status_code))
        return 1
    else:
        print("Unknown error. [ERR_CODE] {}".format(r.status_code))
        return 2
    

def main(args, config):
    print("Collecting lists..")
    lists = []
    for url in args.urls:
        list_id = get_list_id(url)
        list = List(url, list_id)
        if list.url and list.id:
            print("Adding list: {}".format(list.url))
            lists.append(list)
    
    movies = []
    for list in lists:
        if list.url and list.id:
            print_list = get_page_content("https://www.listchallenges.com/print-list/{}".format(list.id))
            print_list_lines = re.split("\n", print_list)
            for line in print_list_lines:
                match = re.search("(?<=\d\. ).+(?=\(\d{4}\))", line)
                movie_name = match.group() if match else None
                match = re.search("\d{4}(?=\))", line)
                movie_year = match.group() if match else None
                movie = Movie(movie_name, movie_year)
                if movie.name and movie.year:
                    movies.append(movie)
    
    log_added = ""
    log_skipped = ""
    
    for movie in movies:
        info = radarr_search_movie(movie.name, movie.year)
        if info:
            movie.radarr_info = info
            if radarr_add_movie(movie) == 0:
                log_added += "{} ({})\n".format(movie.name, movie.year)
        else:
            print("Skipping '{}', radarr info not found".format(movie.name))
            log_skipped += "{} ({})\n".format(movie.name, movie.year)
    pathlib.Path("added_movies.log").write_text(log_added)
    pathlib.Path("skipped_movies.log").write_text(log_skipped)
parser = argparse.ArgumentParser(description="Radarr importer for listchallenges.com movie lists")
parser.add_argument("urls", type=str, nargs='+', help="List of urls")

args = parser.parse_args()
config = get_config()

main(args, config)
