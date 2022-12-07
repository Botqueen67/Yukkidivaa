#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import random
import re
import textwrap

import numpy as np

import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)
from youtubesearchpython.__future__ import VideosSearch

from config import MUSIC_BOT_NAME, YOUTUBE_IMG_URL

def make_col():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    
def remove_non_ascii(text):
    new_val = text.encode("ascii", "ignore")
    updated_str = new_val.decode()
    return updated_str

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newHeight, newWidth))
    newImg = ImageOps.expand(newImage, border=10, fill="yellow")
    return newImg
    
def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2] 
    

async def gen_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(
                        f"cache/thumb{videoid}.png", mode="wb"
                    )
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")        
        background = image2.filter(filter=ImageFilter.BoxBlur(35))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.8)
        image2 = background
        
        circle = Image.open("assets/circle.jpg")
        
        # changing circle color
        im = circle
        im = im.convert('RGBA')
        color = make_col()
     
        data = np.array(im)
        red, green, blue, alpha = data.T        
        
        white_areas = (red == 255) & (blue == 255) & (green == 255)
        data[..., :-1][white_areas.T] = color
        
        im2 = Image.fromarray(data)        
        circle = im2
        # done
        
        image3 = image1.crop((280,0,720,1000))
        lum_img = Image.new('L', [720,720] , 0)
        draww = ImageDraw.Draw(lum_img)
        draww.pieslice([(0,0), (720,720)], 0, 360, fill = 255, outline = "white")
        img_arr = np.array(image3)
        lum_img_arr = np.array(lum_img)
        final_img_arr = np.dstack((img_arr,lum_img_arr))
        image3 = Image.fromarray(final_img_arr)
        image3 = image3.resize((500,500))
        
        image2.paste(image3, (50,70))
        image2.paste(circle, (0,0))        
       
        
        font1 = ImageFont.truetype("assets/font2.ttf", 40)
        font2 = ImageFont.truetype("assets/font2.ttf", 70)
        font3 = ImageFont.truetype("assets/font.ttf", 40)
        font4 = ImageFont.truetype("assets/font2.ttf", 30)
        
        image4 = ImageDraw.Draw(image2)
        image4.text((10, 10), "DIVU MUSIC", fill="white", font = font1, align ="left") 
        image4.text((150, 1000), "Enjoy the song!", fill="white", font = font2, stroke_width=2, stroke_fill="white", align ="left")        
       
                    # title
        title1 = truncate(title)
        image4.text((50, 650), text=title1[0], fill="white", stroke_width=1, stroke_fill="white",font = font3, align ="left") 
        image4.text((50, 710), text=title1[1], fill="white", stroke_width=1, stroke_fill="white", font = font3, align ="left") 

            # description
        views = f"Views : {views}"
        duration = f"Duration : {duration} Mins"
        channel = f"Channel : {channel}"

        image4.text((100, 810), text=views, fill="white", font = font4, align ="left") 
        image4.text((100, 860), text=duration, fill="white", font = font4, align ="left") 
        image4.text((100, 910), text=channel, fill="white", font = font4, align ="left")
            
        image2 = ImageOps.expand(image2,border=20,fill=make_col())
        image2 = image2.convert('RGB')
        image2.save(f"cache/{videoid}.jpg")
        file = f"cache/{videoid}.jpg"
        #os.remove(file)

        return file
    except Exception as e:
        print(e)
        return "YOUTUBE_IMG_URL"
