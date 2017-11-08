# pylint: disable=invalid-name
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageFont, ImageDraw
import textwrap
import os
from multiprocessing import Queue
import idna

base_url = 'http://xkcd.com'
site_status = requests.get(base_url)

#Only continue if the site is online
if site_status.status_code == 200:

    site_content = BeautifulSoup(site_status.content, 'html.parser')
    comic_info = site_content.find(id='comic')
    comic_url = "http:" + comic_info.img['src']

    #Find and print the title of the comic
    comic_title = comic_info.img['alt']
    print("Title: {}".format(comic_title))

    #Find and print the alternate title/hidden joke
    alt_comic_title = comic_info.img['title']
    print("Alt comic title: {}".format(alt_comic_title))

    #Download the image using the alt-title as the actual title
    comic_img = open(comic_title + "_tmp.png",'wb')
    comic_img.write(requests.get(comic_url).content)
    comic_img.close()

    #Lets download a font so that we can write on the image
    font = ImageFont.truetype("arial.ttf", 14, encoding="unic")

    #Lets give the comic filename a variable
    saved_comic = Image.open(comic_title + "_tmp.png")

    comic_size = saved_comic.size

    #Create a new image to put the text on
    text_img = Image.new("RGB", comic_size, color='white') 
    draw = ImageDraw.Draw(text_img) #Clean slate the image

    #create array split by width (avg char is 7px)
    lines = textwrap.wrap(alt_comic_title, width=(comic_size[0] / 7)) 
    line_print_counter = 0

    width, height = font.getsize(lines[0]) 

    #Print line by line the text
    for line in lines:
        width, height = font.getsize(line)
        draw.text((0 , line_print_counter), line,'black',font=font)
        line_print_counter += height

    draw = ImageDraw.Draw(text_img)

    #Create a new image to paste the original image and the text to

    #If the image is less than 300, do side by side
    if comic_size[0] < 300:
        final_img= Image.new("RGB", (comic_size[0] * 2, comic_size[1]))
        saved_comic.copy()
        final_img.paste(saved_comic,(0,0))

        text_img.copy()
        final_img.paste(text_img,(comic_size[0], 0))
    else:
        final_img= Image.new("RGB", (comic_size[0], comic_size[1] * 2))
        saved_comic.copy()
        final_img.paste(saved_comic,(0,0))

        text_img.copy()
        final_img.paste(text_img,(0, comic_size[1]))

    #Show it and save it
    final_img.show()
    final_img.save(comic_title + ".png")

else:
    print("Site status is unavailable ({status})".format(status=site_status.status_code))

#Cleanup
os.remove(comic_title + "_tmp.png")
