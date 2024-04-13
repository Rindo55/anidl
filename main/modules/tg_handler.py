
import asyncio
import time
import aiohttp
import requests
import aiofiles
import sys
from moviepy.editor import VideoFileClip
from main.modules.compressor import compress_video

from main.modules.utils import episode_linker, get_duration, get_epnum, status_text, get_filesize, b64_to_str, str_to_b64, send_media_and_reply, get_durationx

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.modules.uploader import upload_video
from main.modules.thumbnail import generate_thumbnail

import os

from main.modules.db import del_anime, save_uploads, is_fid_in_db, is_tit_in_db

from main.modules.downloader import downloader

from main.modules.anilist import get_anilist_data, get_anime_img, get_anime_name

from config import INDEX_USERNAME, UPLOADS_USERNAME, UPLOADS_ID, INDEX_ID, PROGRESS_ID, LINK_ID

from main import app, queue, status

from pyrogram.errors import FloodWait

from pyrogram import filters, enums

from main.inline import button1

status: Message

async def tg_handler():

    while True:

        try:
            if len(queue) != 0:

                i = queue[0]  

                i = queue.pop(0)
                
                id, name, video = await start_uploading(i)
                print("Title: ", i["title"])
                await del_anime(i["title"])
                await save_uploads(i["title"])
                await asyncio.sleep(30)


            else:                

                if "Idle..." in status.text:

                    try:

                        await status.edit(await status_text("Idle..."))

                    except:

                        pass

                await asyncio.sleep(30)

                

        except FloodWait as e:

            flood_time = int(e.x) + 5

            try:

                await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

            except:

                pass

            await asyncio.sleep(flood_time)

        except:

            pass

def get_audio_info(video_path):
    try:
        video_clip = VideoFileClip(video_path)
        audio = video_clip.audio
        audio_info = {
            'audio_track_language': audio.langcode
        }
        return audio_info
    except Exception as e:
        print(f"Error: {e}")
        return None             

async def start_uploading(data):

    try:

        title = data["title"]
        dbtit = data["title"]
        title = title.replace("Dr. Stone - New World", "Dr Stone New World")
        title = title.replace("Opus.COLORs", "Opus COLORs")
        title = title.replace(" Isekai wa Smartphone to Tomo ni. 2", " Isekai wa Smartphone to Tomo ni 2")
        title = title.replace("Stand My Heroes - Warmth of Memories - OVA", "Stand My Heroes Warmth of Memories - OVA")
        link = data["link"]
        size = data["size"]
        nyaasize = data["size"]
        subtitle = data["subtitle"]
        name, ext = title.split(".")

        name += f" [AniDL]." + ext

        KAYO_ID =  -1001895203720
        uj_id = 1159872623
        DATABASE_ID = -1001895203720
        bin_id = -1002062055380
        name = name.replace(f" [AniDL].","").replace(ext,"").strip()
        id, img, tit = await get_anime_img(get_anime_name(title))
        msg = await app.send_photo(bin_id,photo=img,caption=title)

        print("Downloading --> ",name)
        img, caption = await get_anilist_data(title)
        await asyncio.sleep(5)
        await status.edit(await status_text(f"Downloading {name}"),reply_markup=button1)
        file = await downloader(msg,link,size,title)

        await msg.edit(f"Download Complete : {name}")
        print("Encoding --> ",name)

        duration = get_duration(file)
        durationx = get_durationx(file)
        filed = os.path.basename(file)
        filed = filed.replace(filed[-14:], ".mkv")
        filed = filed.replace("[Erai-raws]", "[AniDL]")
        filed = filed.replace("[1080p][Multiple Subtitle]", "[1080p Web-DL]")
        filed = filed.replace("[1080p]", "[1080p Web-DL]")
        filed = filed.replace("2nd Season", "S2")
        filed = filed.replace("3rd Season", "S3")
        razo = filed.replace("[1080p Web-DL]", "[720p x265] @animxt")
        fpath = "downloads/" + filed
        ghostname = name
        ghostname = ghostname.replace("[1080p][Multiple Subtitle]", "")
        ghostname = ghostname.replace("[1080p]", "")
        ghostname = ghostname.replace("2nd Season", "S2")
        ghostname = ghostname.replace("3rd Season", "S3")
        subtitle = subtitle.replace("][", ", ")
        subtitle = subtitle.replace("[", "")
        subtitle = subtitle.replace("]", "")     
    
        os.rename(file,"video.mkv")
        titlx = title.replace('[1080p][Multiple Subtitle]', '[Web][480p x265 10Bit][Opus][Erai-raws]')
        titm = f"**[AniDL] {titlx}**"
        tito = f"[AniDL] {titlx}"
        main = await app.send_photo(KAYO_ID,photo=img, caption=titm)
        compressed = await compress_video(duration,main,tito)
    

        if compressed == "None" or compressed == None:

            print("Encoding Failed Uploading The Original File")

            os.rename("video.mkv",fpath)

        else:

            os.rename("out.mkv",fpath)
  
        print("Uploading --> ",name)
        video = await upload_video(msg,img,fpath,id,tit,name,size,main,subtitle,nyaasize,audio_info)



        try:

            os.remove("video.mkv")

            os.remove("out.mkv")

            os.remove(file)

            os.remove(fpath)
        except:

            pass     

    except FloodWait as e:

        flood_time = int(e.x) + 5

        try:

            await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

        except:

            pass

        await asyncio.sleep(flood_time)
        
    return id, name, video

    
