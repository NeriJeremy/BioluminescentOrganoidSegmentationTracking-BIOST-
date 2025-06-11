# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 16:05:26 2025

@author: jneri
"""

class processBIOST:

    def __init__(self, directory, GetRims, save_dir, Save, FigParameters, ProcessingParameters):
        
        self.directory = directory
        self.GetRims = GetRims
        self.save_dir = save_dir
        self.Save = Save
        self.FigParameters = FigParameters
        self.ProcessingParameters = ProcessingParameters
    
    def meansmooth(self, smoothingfactor):
        