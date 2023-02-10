# -*- coding: utf-8 -*-

"""
Class for packing (and unpacking) a music playlist to a video, just for some 
purposes...
 
"""
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio import *
from moviepy.editor import concatenate_videoclips
import json

import os, string, random, pathlib

class MusicToVideoPacker:
    ''' Class for packing (and unpacking) a music playlist to a video.
    '''
    
    VIDEO_FILE_TYPES = [".mp4",]    
    AUDIO_FILE_TYPES = [".mp3",] 
    DATA_DIR = "../data/"
    OUT_EXT = ".mp4"
    META_FILE  = "META.txt"
    VIDEO_RESOLUTION = (240,240)
    WANTED_BITRATE = "320K"
    
    def __init__(self, VideoDir: str, AudioDir: str):
        if not os.path.isdir(VideoDir) or not os.path.isdir(AudioDir):
            raise Exception("Wrong MusicToVideoPacker video/audio directories. Please specify valid values")
        
        self.video_dir = VideoDir
        self.audio_dir = AudioDir
        self.audio_files = list()
        self.video_files = list()
        self.meta = {}        
        self.output_dir = self.DATA_DIR
        self.clip_circle_prefix=0
        
    def list_videos(self, verb=False):
        if verb: print(f"Searching video files in '{self.video_dir}' ...\n")
        self.dir_traverse(self.video_dir, self.VIDEO_FILE_TYPES, self.video_files, verb)
        if len(self.video_files)<1:
            print("No video files found.")

    def list_audios(self, verb=False):
        if verb: print(f"Searching audio files in '{self.audio_dir}' ...\n")
        self.dir_traverse(self.audio_dir, self.AUDIO_FILE_TYPES, self.audio_files, verb)
        if len(self.audio_files)<1:
            print("No audio files found.")
        
    def dir_traverse(self, directory:str, filter_types:list, results:list, verb=False):
        for fl in os.listdir(directory):
            fl_path = os.path.join(directory, fl)
            if os.path.isdir(fl_path):
                #print("     - DIR")
                self.dir_traverse(fl_path, filter_types, results)
            elif os.path.isfile(fl_path) and os.path.splitext(fl)[-1] in filter_types:
                if verb: print(f"   {fl}")
                results.append(fl_path)
            
    def Pack(self, output_path=None):
        print("Packing ...")
        
        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)
            
        if not len(self.audio_files):
            print(" Retrieving files to pack...")
            self.list_videos()    
            self.list_audios()    
        
        self.output_dir=output_path if not output_path is None else self.DATA_DIR
            
        if len(self.audio_files)<1 or len(self.video_files)<1:
            print("! Error. No audio or video files found.")
            return
        
        clip_i=0
        self.clip_circle_prefix=0
        #global clip
        #global song
        songs=list()
        clip = VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)            
        audio_chunck_duration = 0 
        
        for audio_file in self.audio_files:
            print("      Processing {0}\n".format(audio_file))
            song = AudioFileClip(audio_file)
            songs.append(song)
            audio_chunck_duration+=song.duration
            
            if audio_chunck_duration > clip.duration:
                
                if len(songs)==1: # single song is longer than clip..

                    #concetating clips to exeed the song duration                    
                    clips_for_concat=[clip,]
                    clips_for_concat_duration = clip.duration
                    while clip_i<len(self.video_files):
                        print(f" >> Concetating video {os.path.basename(self.video_files[clip_i])}")
                        clip_i+=1
                        newclip = VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)
                        clips_for_concat.append(newclip)
                        clips_for_concat_duration+=newclip.duration
                        if clips_for_concat_duration > song.duration: break                    
                    clip=concatenate_videoclips(clips_for_concat)                 
                    
                    #assembling songs and clip
                    assembledClipFilename = pathlib.Path(song.filename).stem+pathlib.Path(newclip.filename).suffix
                    assembledClip = self.AssembleClip(clip, songs, assembledClipFilename)
                    audio_chunck_duration=0
                    songs=[]
                    for cl in clips_for_concat: cl.close()

                else: # len(songs) > 1
                                
                    #assembling songs and clip
                    assembledClip = self.AssembleClip(clip, songs[:-1])
                    audio_chunck_duration=song.duration
                    songs=[song,]
                clip_i+=1
                if clip_i >= len(self.video_files):
                    #print(" ! Video files ended! Quiting.")
                    #break
                    clip_circle_prefix+=1
                    clip_i=0
                    
                clip = VideoFileClip(self.video_files[clip_i], audio=False, target_resolution=self.VIDEO_RESOLUTION)            

        #saving leftovers
        if len(songs) and  clip_i < len(self.video_files):
            self.AssembleClip(clip, songs)
            
        #saving metadata
        print("Saving metadata.")
        with open(os.path.join(self.output_dir, self.META_FILE), "w") as fl:
            fl.write(json.JSONEncoder().encode(self.meta))
            
        print("Packing done.")
        
    def appendRandPrefis(self, name:str):
        return f"{self.clip_circle_prefix}"+"".join(random.choices(string.digits+string.ascii_uppercase, k=5))+"_"+name

    def AssembleClip(self, clip, songs:list, clipAssambleName_ = None):
        
        audioTrack = AudioClip.CompositeAudioClip(songs)
        clip.audio = audioTrack    
        clip = clip.subclip(0, audioTrack.duration)    

        #!..  to check file existance               
        clip_save_name =  clipAssambleName_ if clipAssambleName_ != None else os.path.basename(clip.filename)
        clip_save_name = self.appendRandPrefis(clip_save_name)
                    
        self.saveClip(clip, clip_save_name)
        
        # adding metadata
        self.meta[clip_save_name]=[{'name':os.path.basename(song.filename), 'duration':song.duration} for song in songs]
    
        # !.. close songs
        for song in songs: song.close()

        return clip
    
    def saveClip(self, clip, flname):

        print(f"Saving {flname}...")        
        clip.write_videofile(os.path.join(self.output_dir, flname), audio_bitrate = self.WANTED_BITRATE)        
        clip.close()

    def Unpack(self, assembly_path:str, out_path:str = "./"):        
        if not os.path.exists(os.path.join(assembly_path, self.META_FILE)):
            raise Exception("Invalid path to assembly. Please specify path containing 'META.txt'")
        
        with open(os.path.join(assembly_path, self.META_FILE), "r")as fl:
            self.meta=json.load(fl)
            
        for clipnm in self.meta:
            print(f"  {clipnm}  - disassembling...")
            if not os.path.exists(os.path.join(assembly_path,clipnm)):
                print("f!! Error while disassembling: {clipnm} not found")
            clip = VideoFileClip(os.path.join(assembly_path, clipnm), audio=True)
            track = clip.audio
            t=0
            for song_meta in self.meta[clipnm]:
                print(f"    {song_meta['name']}  - extracting...")
                song = track.subclip(t, song_meta["duration"])
                t+=song_meta["duration"]
                song.write_audiofile(os.path.join(out_path, song_meta["name"]), bitrate = self.WANTED_BITRATE)
                song.close()
                
            clip.close()
            
        # ! ... may be add songs hash check
        print("Disassembling done.")    
                                

if __name__=="__main__":
    video_dir = r"/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/"
    audio_dir =r"/home/hackassen/works/MusicPacker/data/in/"
    packed_path = r"/home/hackassen/works/MusicPacker/data/packed/"

    packer = MusicToVideoPacker(video_dir, audio_dir)
    packer.Pack(output_path=packed_path)
        
    output_path = r"/home/hackassen/works/MusicPacker/data/out/"
    packer.Unpack(packed_path, output_path)
    