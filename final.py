from os import path, makedirs
from datetime import datetime, date
from sys import argv,exit
from hashlib import sha256
from ctypes import windll
from urllib import request
import requests, sqlite3, re

def main():
    # * DO NOT MODIFY THIS FUNCTION *

    # Determine the path of image cache directory and SQLite data base file
    image_cache_path = get_image_cache_path()
    db_path = path.join(image_cache_path, 'apod_images.db')

    # Determine the date of the desired APOD
    apod_date = get_apod_date()

    # Create the image cache database, if it does not already exist
    create_apod_image_cache_db(db_path)

    # Get info about the APOD from the NASA API
    apod_info_dict = get_apod_info(apod_date)
    
    # Get the URL of the APOD
    image_url = get_apod_image_url(apod_info_dict)
    image_title = get_apod_image_title(apod_info_dict)
    
    # Determine the path at which the downloaded image would be saved 
    image_path = get_apod_image_path(image_cache_path, image_title, image_url)

    # Download the APOD image data, but do not save to disk
    image_data = download_image_from_url(image_url)

    # Determine the SHA-256 hash value and size of the APOD image data
    image_size = get_image_size(image_data)
    image_sha256 = get_image_sha256(image_data)

    # Print APOD image information
    print_apod_info(image_url, image_title, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not apod_image_already_in_cache(db_path, image_sha256):
        save_image_file(image_data, image_path)
        add_apod_to_image_cache_db(db_path, image_title, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_cache_path():
    """
    Gets the path of the image cache directory in which all APOD
    images are saved. Creates the image cache directory if it 
    does not already exist.
    
    Exits script execution if no image cache directory path is 
    specified as a command line parameter or the specified path
    is not a valid full path.

    :returns: Path of the image cache directory
    """
    if len(argv) >= 2:
        dir_path = argv[1]

        if not path.isabs(dir_path):
            print("\nError: Image cache path parameter must be absolute.")
            exit("\nScript execution aborted")
        else:
            if path.isdir(dir_path):
                print("\nImage cache directory: ", dir_path)
                return dir_path
            elif path.isfile(dir_path):
                print("\nError: Path Parameter is existing file.")
                exit("\nScript execution aborted")
            else:
                print("\nCreating new image director '"+dir_path+"'...",end='')
                try:
                    makedirs(dir_path)
                    print('success')
                except:
                    print("Failure")
                return dir_path
    else:
        print("\nError:Missing image path paramerter")
        exit("\nScript execution aborted")

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Script exits if the date is invalid or formatted incorrectly.
    Returns today's date if no date is provided on the command line. 

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """
    if len(argv) >=3:
        apod_date = argv[2]
        try:
            apod_datetime = datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Must be YYYY-MM-DD")
            exit("Script execution aborted")

        if apod_datetime.date() < date(1995,6,16):
            print("Error: Date too far in the past; First image take on 1995-06-16")
            exit("Script execution aborted")
        elif apod_datetime.date() > date.today():
            print("Error: Date Cannot be in Future")
            exit("Script execution aborted")
    else:           
        apod_date =date.today().isoformat()
    print("APOD date:", apod_date)
    return apod_date

def get_apod_image_path(image_cache_path, image_title, image_url):
   
    file_ext = image_url.split(".")[-1]
    file_name = image_title.strip()
    file_name = file_name.replace(' ','_')
    file_name = re.sub(r'\W','', file_name)
    file_name = '.'.join((file_name, file_ext))
    file_path = path.join(image_cache_path, file_name)
    return file_path


def get_apod_info(apod_date):
    
    print('Getting Image information from NASA..', end='')
    NASA_API_KEY = 'tz6CvXkLfg4etTXfvIZSOFaGDi6Cmm9BT393j05V'
    APOD_URL = "https://api.nasa.gov/planetary/apod"
    apod_params= {
        'api_key': NASA_API_KEY,
        'date': apod_date,
        'thumbs': True
    }
    resp_msg = requests.get(APOD_URL, params = apod_params)
    if resp_msg.status_code == requests.codes.ok:
        print("Success")
    else:
        print("Failure code", resp_msg.status_code)
        exit("Script execution aborted")
    apod_info_dict = resp_msg.json()
    return apod_info_dict

def get_apod_image_url(apod_info_dict):
      
    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict['hdurl']
    elif apod_info_dict['media_type'] == 'video':
        return apod_info_dict['thumbnail_url']

def get_apod_image_title(apod_info_dict):
    
    return apod_info_dict['title']

def print_apod_info(image_url, image_title, image_path, image_size, image_sha256):
    
    print("\nAPOD Image Information: \n")
    print("\nImage Title: ", image_title)
    print("\nImage URL: ",image_url)
    print("\nPath: ", image_path)
    print("\nSize: ", image_size)
    print("\nHash value(SHA256): ", image_sha256)

def create_apod_image_cache_db(db_path):
    return 

def add_apod_to_image_cache_db(db_path, image_title, image_path, image_size, image_sha256):
    return

def apod_image_already_in_cache(db_path, image_sha256):
    return

def get_image_size(image_data):
    return len(image_data)

def get_image_sha256(image_data):

    return sha256(image_data).hexdigest().upper()

def download_image_from_url(image_url):
   
    print('Download Image from NASA...', end='')

    resp_msg = requests.get(image_url)

    if resp_msg.status_code == requests.codes.ok:
        print('success')
        return (resp_msg.content)
    else:
        print('Failure Code', resp_msg.status_code)
        exit('Script execution aborted')


def save_image_file(image_data, image_path):
   
    try:
        print("Saving image to file cache...", end='')
        with open(image_path,'wb') as fp:
            fp.write(image_data)
        print('success')
    except:
        print("Failure")
        exit('Script execution aborted')

def set_desktop_background_image(image_path):
    return


main()