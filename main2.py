from tqdm import tqdm
import pandas as pd
import requests
import os
import time
from datetime import datetime
from helper_func import calcRunTime, getExpID, write2Log



def get_sat_img(indx, id, lat, long, output_dir):
# ==== CONFIGURATION ====
    API_KEY = ""  # CC@g


 
    
    OUTPUT_DIR = output_dir
    LATITUDE = lat
    LONGITUDE = long
    ZOOM = 20         # Zoom level: 0 (world) -> 21+ (building)
    IMAGE_SIZE = "640x640" # Max free tier size
    SCALE = 1              # 1=normal, 2=high-res (counts as more pixels)

    # ==== CREATE OUTPUT FOLDER ====
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ==== BUILD REQUEST URL ====
    url = (
        "https://maps.googleapis.com/maps/api/staticmap"
        f"?center={LATITUDE},{LONGITUDE}"
        f"&zoom={ZOOM}"
        f"&size={IMAGE_SIZE}"
        f"&scale={SCALE}"
        f"&maptype=satellite"
        f"&key={API_KEY}"
    )

    # ==== DOWNLOAD IMAGE ====
    response = requests.get(url)

    if response.status_code == 200:
        filename = os.path.join(OUTPUT_DIR, f"{id}.jpg")
        with open(filename, "wb") as f:
            f.write(response.content)
        # print(f"Saved satellite image: {filename}")
        return 200
    else:
        print(f"Error {response.status_code}: {response.text}")
        write2Log(ExpID=expID, content=f'Error at: {indx}, id: {id}\n')
        return 404








expID = getExpID()
write2Log(ExpID=expID, content=f'ExpID: {expID}\n')

df = pd.read_csv(f'datasets/osv5m/train.csv')

strt_indx = 310000
img_num = 11126
output_dir = 'datasets/osv5m_sat/train'
os.makedirs(output_dir, exist_ok=True)

write2Log(ExpID=expID, content=f'Start Location: {strt_indx}\nNumber of Location: {img_num}\n')
write2Log(ExpID=expID, content=f'StartTime: {datetime.now()}\n\n')
start_time = time.time()


for i in tqdm(range(img_num)):
    id = df['id'].loc[strt_indx+i]
    lat = df['latitude'].loc[strt_indx+i]
    long = df['longitude'].loc[strt_indx+i]
    # try:
    #     get_sat_img(indx=strt_indx+i, id=id, lat=lat, long=long, output_dir=output_dir)
    # except Exception as e:
    #     write2Log(ExpID=expID, content=f'Error at: {strt_indx+i}, id: {id}\n')
    #     break
    
    stat_code = get_sat_img(indx=strt_indx+i, id=id, lat=lat, long=long, output_dir=output_dir)
    
    if stat_code==404:
        write2Log(ExpID=expID, content=f'Total downloaded: {i-1}\n')
        break

    
    if(i%1000==0):
        write2Log(ExpID=expID, content=f'Check: {strt_indx+i}, id: {id}\n')



write2Log(ExpID=expID, content=f'\nLastIndex {strt_indx+img_num}\n')
write2Log(ExpID=expID, content=f'\nEndTime: {datetime.now()}\n')
end_time = time.time()
write2Log(ExpID=expID, content=f'Runtime: {calcRunTime(stt=start_time, edt=end_time)}\n')

# import requests
# import os

# def download_street_view_image(lat, lon, api_key, save_path, heading=0, pitch=0, fov=90, size="640x640"):
#     """
#     Downloads a Google Street View image based on latitude and longitude.

#     Args:
#         lat (float): Latitude
#         lon (float): Longitude
#         api_key (str): Your Google Maps API key
#         save_path (str): Where to save the image (e.g., 'output.jpg')
#         heading (int): Direction the camera is pointing (0–360 degrees)
#         pitch (int): Up or down angle (-90 to 90)
#         fov (int): Field of view (10–120)
#         size (str): Image size in WIDTHxHEIGHT format (max 640x640 unless premium)
#     """

#     base_url = "https://maps.googleapis.com/maps/api/streetview"
#     params = {
#         "size": size,
#         "location": f"{lat},{lon}",
#         "heading": heading,
#         "pitch": pitch,
#         "fov": fov,
#         "key": api_key
#     }

#     response = requests.get(base_url, params=params)

#     if response.status_code == 200:
#         with open(save_path, "wb") as f:
#             f.write(response.content)
#         print(f"Image saved to {save_path}")
#     else:
#         print(f"Failed to fetch image: {response.status_code} - {response.text}")



# api_key = "YOUR_GOOGLE_API_KEY"
# lat, lon = 40.689247, -74.044502  # Example: Statue of Liberty
# save_path = "street_view.jpg"

# download_street_view_image(lat, lon, api_key, save_path)
