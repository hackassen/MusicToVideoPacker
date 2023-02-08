# -*- coding: utf-8 -*-

"""
Class for packing (and unpacking) a music playlist to a video, just for some 
purposes...
 
"""
from moviepy.video.io import *
from moviepy.audio.io import *
from moviepy.audio import *
from moviepy.editor import concatenate_videoclips
import json

import os, string, random

class MusicToVideoPacker:
    # some descr
   
    VIDEO_FILE_TYPES = [".mp4",]    
    AUDIO_FILE_TYPES = [".mp3",] 
    DATA_DIR = "../data/"
    OUT_EXT = ".mp4"
    #OUT_PATH  = DATA_DIR+"PACKED"+OUT_EXT
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

                    #concetating clips to exeed the song duration                    
                    clips_for_concat=[clip,]
                    clips_for_concat_duration = clip.duration
                    while clip_i<len(self.video_files):
                        print(f" >> Concetating video {os.path.basename(self.video_files[clip_i])}")
                        clip_i+=1
                        newclip = VideoFileClip.VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)
                        clips_for_concat.append(newclip)
                        clips_for_concat_duration+=newclip.duration
                        if clips_for_concat_duration > song.duration: break
                            
                    #print(f" clips to concat {clips_for_concat}")
                    clip=concatenate_videoclips(clips_for_concat)
                    #print(f" conc done.")
                                
                #assembling songs and clip
                assembledClip = self.AssembleClip(clip, songs)
                audio_chunck_duration=song.duration
                songs=[song,]
                clip_i+=1
                clip = VideoFileClip.VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)            
                continue
                
                #tp
                #break
            
            songs.append(song)
            audio_chunck_duration+=song.duration
            
            
        #saving metadata
        print("Saving metadata.")
        with open(self.DATA_DIR+self.META_FILE, "w") as fl:
            fl.write(json.JSONEncoder().encode(self.meta))
            
        print("Packing done.")
        
    def AssembleClip(self, clip, songs:list):
        
        audioTrack = AudioClip.CompositeAudioClip(songs)
        #print("!!!!!!!!!!!!!!!!!!")
        clip.audio = audioTrack    
        clip = clip.subclip(0, audioTrack.duration)    

        #!..  to check file existance       
        rand_prep = ''.join(random.choices(string.digits+string.ascii_uppercase, k=5))+"_"
        clip_save_name = rand_prep+os.path.basename(clip.filename)
        self.saveClip(clip, clip_save_name)
        
        # adding metadata
        self.meta[clip_save_name]=[{'name':os.path.basename(song.filename), 'duration':song.duration} for song in songs]
    
        # !.. close songs
        for song in songs: song.close()

        return clip
    
    def saveClip(self, clip, flname):

        print(f"Saving {flname}...")        
        clip.write_videofile(f"{self.DATA_DIR}{flname}")        
        clip.close()

    def Disassemble(self, assembly_path:str, out_path:str = "./"):
        if not os.path.exists(assembly_path+"/"+self.META_FILE):
            raise Exception("Invalid path to assembly. Please specify path containing 'META.txt'")
        
        with open(assembly_path+"/"+self.META_FILE, "r")as fl:
            self.meta=json.load(fl)
            
        for clipnm in self.meta:
            print(f"  {clipnm}  - disassembling...")
            if not os.path.exists(assembly_path+"/"+clipnm):
                print("f!! Error while disassembling: {clipnm} not found")
            clip = VideoFileClip.VideoFileClip(assembly_path+"/"+clipnm, audio=True)
            track = clip.audio
            t=0
            for song_meta in self.meta[clipnm]:
                print(f"    {song_meta['name']}  - extracting...")
                song = track.subclip(t, song_meta["duration"])
                t+=song_meta["duration"]
                song.write_audiofile(out_path+"/"+song_meta["name"])
                song.close()
                
            clip.close()
            
        print("Disassembling done.")
                                
            
#from moviepy import VideoFileClip, concatenate_videoclips
#clip1 = VideoFileClip("myvideo.mp4")
#final_clip.resize(width=480)
#.write_videofile("my_stack.mp4")

if __name__=="__main__":
    video_dir = r"/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/"
    audio_dir =r"/home/hackassen/homehackassenDownloadsyndMusic/"

    video_dir = r"/home/hackassen/works/MusicPacker/src/tp/"
    audio_dir =r"/home/hackassen/works/MusicPacker/src/tpA/"

    packer = MusicToVideoPacker(video_dir, audio_dir)
    packer.list_videos()    
    packer.list_audios()    
    packer.Pack()
    
    
    packed_path = r"/home/hackassen/works/MusicPacker/data/"
    packed_path = r"/home/hackassen/tp/"
    #packer.Disassemble(packed_path)
    