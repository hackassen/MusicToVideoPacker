#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 12:11:18 2023

@author: hackassen
packing/unpacking test for MusicToVideoPacker
"""

from MusicToVideoPacker import MusicToVideoPacker as Packer

video_dir = r"/home/hackassen/Downloads/movies/[Udemy] Python Programming Machine Learning, Deep Learning (05.2021)/"
#audio_dir =r"/home/hackassen/homehackassenDownloadsyndMusic/"
audio_dir = r"/home/hackassen/tp/in/"
packed_dir = r"/home/hackassen/tp/packed/"
packer = Packer(video_dir, audio_dir)
packer.Pack(packed_dir)


#packed_path = r"/home/hackassen/works/MusicPacker/data/"
#output_path = r"/home/hackassen/tp/"
#packer.Unpack(packed_path, output_path)


