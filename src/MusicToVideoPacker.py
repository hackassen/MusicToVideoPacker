# -*- coding: utf-8 -*-

"""
Class for packing (and unpacking) a music playlist to a video, just for some 
purposes...
 
"""
from moviepy.video.io import *
from moviepy.audio.io import *
from moviepy.audio import *
import json

import os, string, random

class MusicToVideoPacker:
    # some descr
   
    VIDEO_FILE_TYPES = [".mp4",]    
    AUDIO_FILE_TYPES = [".mp3",] 
    DATA_DIR = "../data/"
    OUT_EXT = ".mp4"
    OUT_PATH  = DATA_DIR+"PACKED"+OUT_EXT
    META_FILE  = "META.txt"
    VIDEO_WIDTH = 240
    VIDEO_RESOLUTION = (240,240)
    
    def __init__(self, VideoDir: str, AudioDir: str):
        if not os.path.isdir(VideoDir) or not os.path.isdir(AudioDir):
            raise Exception("Wrong MusicToVideoPacker video/audio directories. Please specify valid values")
        
        self.video_dir = VideoDir
        self.audio_dir = AudioDir
        self.audio_files = list()
        self.video_files = list()
        self.meta = {}        
            
        
    def list_videos(self):
        print(f"Searching video files in '{self.video_dir}' ...\n")
        self.dir_traverse(self.video_dir, self.VIDEO_FILE_TYPES, self.video_files)
        if len(self.video_files)<1:
            print("No video files found.")

    def list_audios(self):
        print(f"Searching audio files in '{self.audio_dir}' ...\n")
        self.dir_traverse(self.audio_dir, self.AUDIO_FILE_TYPES, self.audio_files)
        if len(self.audio_files)<1:
            print("No audio files found.")
        
    def dir_traverse(self, directory:str, filter_types:list, results:list):
        for fl in os.listdir(directory):
            fl_path = directory+"/"+fl
            if os.path.isdir(fl_path):
                #print("     - DIR")
                self.dir_traverse(fl_path, filter_types, results)
            elif os.path.isfile(fl_path) and os.path.splitext(fl)[-1] in filter_types:
                print(f"   {fl}")
                results.append(fl_path)
            
    def Pack(self):
        print("Packing ...")
        
        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)
            
        if len(self.audio_files)<1 or len(self.video_files)<1:
            print("! Error. No audio or video files found.")
            return
        
        clip_i=0
        #global clip
        #global song
        songs=list()
        clip = VideoFileClip.VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)            
        audio_chunck_duration = 0 
        
        for audio_file in self.audio_files:
            print("      Processing {0}\n".format(audio_file))
            song = AudioFileClip.AudioFileClip(audio_file)
            
            if audio_chunck_duration + song.duration > clip.duration:
                
                if audio_chunck_duration==0: # single song is longer than clip..
                    # ! try to glue several vioes to the length of the song
                    raise Exception("!!! ERROR the song is longer than the clip.")
                
                #assembling songs and clip
                assembledClip = self.AssembleClip(clip, songs)
                audio_chunck_duration=song.duration
                songs=[song,]
                clip_i+=1
                
                #tp
                break
            
            songs.append(song)
            audio_chunck_duration+=song.duration
            
            
        #saving metadata
        print("Saving metadata.")
        with open(self.DATA_DIR+self.META_FILE, "w") as fl:
            fl.write(json.JSONEncoder().encode(self.meta))
            
        print("Packing done.")
        
    def AssembleClip(self, clip, songs:list):
        audioTrack = AudioClip.CompositeAudioClip(songs)
        # !.. close soungs
        #for song in songs: song.close()
        
        clip.audio = audioTrack    
        clip = clip.subclip(0, audioTrack.duration)    

        #!.. to add random suffix to clipname, to check file existance       
        rand_prep = ''.join(random.choices(string.digits+string.ascii_uppercase, k=5))+"_"
        clip_save_name = rand_prep+os.path.basename(clip.filename)
        self.saveClip(clip, clip_save_name)
        
        # adding metadata
        self.meta[clip_save_name]=[{'name':os.path.basename(song.filename), 'duration':song.duration} for song in songs]
    
        return clip
    
    def saveClip(self, clip, flname):

        print(f"Saving {flname}...")        
        clip.write_videofile(f"{self.DATA_DIR}{flname}")        
        clip.close()
    
                                
            
#from moviepy import VideoFileClip, concatenate_videoclips
#clip1 = VideoFileClip("myvideo.mp4")
#final_clip.resize(width=480)
#.write_videofile("my_stack.mp4")

if __name__=="__main__":
    video_dir = r"/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/"
    audio_dir =r"/home/hackassen/homehackassenDownloadsyndMusic/"
    packer = MusicToVideoPacker(video_dir, audio_dir)
    packer.list_videos()    
    packer.list_audios()    
    packer.Pack()