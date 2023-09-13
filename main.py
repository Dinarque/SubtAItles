# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 17:49:25 2023

@author: 3b13j
"""

debug_mode = False
import ffmpeg
import streamlit as st 
from pytube import YouTube
from pydub import AudioSegment
from pydub.playback import play
from streamlit_player import st_player
import os
import shutil
import random 
import io
from docx import Document

## some functions 

def get_video(link):
    
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    try :
        os.remove("buffer.mp4")
    except :
        print("clear")
    try :
         os.remove("buffer.mp3")
    except :
         print("clear")
    try :
        os.remove("final_video.mp4")
    except :
          print("clear")
    os.rename(out_file, "buffer.mp4")
    base , ext = os.path.splitext(out_file)
    mp3 = shutil.copy("buffer.mp4", "buffer.mp3") 
    return yt.title, yt.thumbnail_url, mp3, out_file


def get_subtitles(link):

    import assemblyai as aai
    aai.settings.api_key = st.secrets["KEY"]
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(link)
    return transcript
    
def treat_vtt(vtt, dif) : 
    
    
    
    buffer = vtt.split("\n")
    if debug_mode : 
        for i in range (len(buffer)) : 
            st.write(i, buffer[i])
    
    to_modif = {}
    for i in range(len(buffer)) :
        if i > 1 and i%3 == 0 :
            to_modif[i] = buffer[i]
    
    
    for k in to_modif.keys() : 
        
        line = to_modif[k].split(" ")
        n_l = ""
        for wd in line : 
           rand = random.randint(0, 101)
           if rand <= dif or  dif == 100: 
               n_l +=  len(wd) * "_"+ " "
           else : 
               n_l += wd + " "
           
        buffer[k] = n_l
    
    if debug_mode : 
        for i in range (len(buffer)) : 
            st.write(i, buffer[i])
   
    truffer = ""
    for line in buffer : truffer += line +"\n"
    return truffer



def treat_srt(srt, dif) : 
    
    
    buffer = srt.split("\n")
    if debug_mode : 
        for i in range (len(buffer)) : 
            st.write(i, buffer[i])
    
    to_modif = {}
    for i in range(len(buffer)) :
        if  (i+2)%4 == 0 :
            to_modif[i] = buffer[i]
            
            

    for k in to_modif.keys() : 
        
        line = to_modif[k].split(" ")
        n_l = ""
        for wd in line : 
           rand = random.randint(0, 101)
           if rand < dif or  dif == 100 : 
               n_l +=  len(wd) * "_"+ " "
           else : 
               n_l += wd + " "
           
        buffer[k] = n_l
    
    if debug_mode : 
        for i in range (len(buffer)) : 
            st.write(i, buffer[i])
   
    truffer = ""
    for i in range(int(len(buffer)/4)) :
       truffer += buffer[4*i] +" "+ buffer[4*i+1] +" "+ buffer[4*i+2]+" "+ buffer[4*i+3]+ "\n"
    
    
    
    
    return truffer

def subtitles_to_file(obj, form, dif) :
    if form == "vtt" : res = treat_vtt(obj.export_subtitles_vtt(), dif)
    elif form == "srt" : res = treat_srt(obj.export_subtitles_srt(), dif)
    else : st.write("invalid subtitles format")
    
    with open("subtitles."+str(form), "w") as file:
        file.write(res)
    return res

def add_subtitles(mp4, sub) : 
    
    
    video = ffmpeg.input(mp4)
    audio = video.audio
    ffmpeg.concat(video.filter("subtitles", sub), audio, v=1, a=1).output("final_video.mp4").run()
    return "final_video.mp4"
    """
    (
    ffmpeg
    .input(mp4)
    .filter('subtitles', sub)
    .output('final_vodep.mp4')
    .run()
    )
    st.write("caribou polu")
    """
    return 'final_video.mp4'
    
def save_subtitles_to_doc(subs) : 
        
    import docx
    doc = docx.Document()
    doc.add_heading(f'Worksheet for the video "{st.session_state.title}"',1)
    doc.add_paragraph(subs)
    doc.save('worksheet.docx')
    
## sidebar 

if debug_mode : 
    st.session_state 

with st.sidebar :
    st.subheader("Configurate the app")
    
    link = st.text_input("Put link to the youtube video")
    
    difficulty = st.slider('Adjust difficulty', 0, 100)
    st.session_state.difficulty = difficulty
    
    if st.button("Lets learn !") :
        #main part that runs the analysis 
        st.session_state.link = link
        st.session_state.title, st.session_state.thumbnail, st.session_state.mp3 , st.session_state.mp4 = get_video(link)
        st.write("file ready")
        st.session_state.subtitles = get_subtitles(st.session_state.mp3)
        
        

if "link" in st.session_state : 
    st_player(link)
"___"
if "subtitles" in st.session_state : 
    st.subheader("subtitles :") 
    processed_sub = subtitles_to_file(st.session_state.subtitles, "srt", st.session_state.difficulty)
    st.write(processed_sub)
    save_subtitles_to_doc(processed_sub)
   
    doc = Document('worksheet.docx')
    doc_download = doc
    bio = io.BytesIO()
    doc_download.save(bio)
    
    st.download_button(label="Download worksheet", data = bio ,
            file_name= 'worksheet.docx',
            mime="docx"
        )
    st.write("lets add the subtitles")
    #final = add_subtitles(st.session_state.mp4, "subtitles.srt")
    #st.video(final)
    
   
   
    
else : st.subheader("Please update a video")

    
    
    




    
    