# -*- coding: utf-8 -*-
"""
------------------------------------------------------------------------------
Octavo Systems - Read Rubik's Cube
------------------------------------------------------------------------------
Authors:   Erik Welsh (erik.welsh [at] octavosystems.com)
License:   Copyright 2017, Octavo Systems, LLC. All rights reserved.
           
The Software is available for download and use subject to the terms and 
conditions of this License. Access or use of the Software constitutes 
acceptance and agreement to the terms and conditions of this License.

Redistribution and use of the Software in source and binary forms, with 
or without modification, are permitted provided that the following conditions 
are met:
  - Redistributions of source code must retain the above copyright notice, 
    this list of conditions and the capitalized paragraph below.
  - Redistributions in binary form must reproduce the above copyright notice, 
    this list of conditions and the capitalized paragraph below in the 
    documentation and/or other materials provided with the distribution.

The names of the software's authors or their organizations may not be used 
to endorse or promote products derived from the Software without specific 
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
------------------------------------------------------------------------------
Read Rubik's cube

Command line:
    read_rubiks_cube.py -i <image_file> 


Description:

Class Cube:
    - Members
      - Faces: "U" (up), "D" (down), "F" (front), "B" (back), "R" (right), "L" (left)
        - Order:  U, L, F, R, B, D
    - Methods
      - print_cube()
      - create_string()
      - verify_cube()
      - rotate_cube() (forward only for now)
      - rotate_face() (back face, CW/CCW only for now)

Class Face:
    - Members
      - Cube dimension (ie 3x3)
      - Array of Tiles
        - Tile is a tuple that is (position, (color tuple))
    - Methods
      - rotate_face() (CW/CCW)


------------------------------------------------------------------------------
Known Issues:

"""
import cv2
import numpy as np
import time

import queue
import threading
import sys
import getopt
import cv2
import rcpy

from PIL import Image, ImageDraw, ImageFont

cal =0

#-----------------------------------------------------------------------------
# Global Variables
#-----------------------------------------------------------------------------
#IMAGE_WIDTH             =  1280
#IMAGE_HEIGHT            =   720

IMAGE_WIDTH             =  352
IMAGE_HEIGHT            =  240

AREA_MIN                =  5000
AREA_MAX                = 10000
HIGHT_WIDTH_DIFF_MAX    = 20

DUPLICATE_OFFSET        = 10

# Ideal cube locations
# TILES                   = [(700, 375, 100, 100),
#                            (575, 375, 100, 100),
#                            (450, 375, 100, 100),
#                            (700, 250, 100, 100),
#                            (575, 250, 100, 100),
#                            (450, 250, 100, 100),
#                            (700, 125, 100, 100),
#                            (575, 125, 101, 100), 
#                            (450, 125, 100, 100)]

'''TILES                   = [(725, 325, 125, 125),
                           (575, 325, 125, 125),
                           (425, 325, 125, 125),
                           (725, 175, 125, 125),
                           (575, 175, 125, 125),
                           (425, 175, 125, 125),
                           (725,  25, 125, 125),
                           (575,  25, 125, 125), 
                           (425,  25, 125, 125)]'''

'''TILES                   = [(730, 320, 120, 90),
                           (600, 320, 120, 90),
                           (460, 320, 120, 90),
                           (730, 190, 120, 90),
                           (600, 190, 120, 90),
                           (460, 190, 120, 90),
                           (730,  60, 120, 90),
                           (600,  60, 120, 90), 
                           (460,  60, 120, 90)]'''

#640 x 480                       
'''TILES                   = [(430, 340, 100, 100),
                           (290, 340, 100, 100),
                           (150, 340, 100, 100),
                           (430, 200, 100, 100),
                           (290, 200, 100, 100),
                           (150, 200, 100, 100),
                           (430,  60, 100, 100),
                           (290,  60, 100, 100), 
                           (150,  60, 100, 100)]'''
                           
#340 x 280
TILES                   = [(220, 180, 40, 40),
                           (140, 180, 40, 40),
                           (60,  180, 40, 40),
                           (220, 100, 40, 40),
                           (140, 100, 40, 40),
                           (60,  100, 40, 40),
                           (220,  20, 40, 40),
                           (140,  20, 40, 40), 
                           (60,   20, 40, 40)]


# Color letters
GREEN                   = "G"
WHITE                   = "W"
YELLOW                  = "Y"
RED                     = "R"
BLUE                    = "B"
ORANGE                  = "O"

                           
# Color values (R, G, B)
#   - Deterimined based on measurements from camera / cube
#
"""
# Speed cube w/ Black Outlines
COLORS                  = {GREEN  : ( 92, 135,  80),
                           WHITE  : (180, 174, 183),
                           YELLOW : ( 82, 180, 187),
                           RED    : ( 12,   9, 102),
                           BLUE   : (133,  75,  30),
                           ORANGE : ( 11,  37, 181)}
"""
"""
# Speed cube w/ Glossy Finish (day)
COLORS                  = {GREEN  : (115, 170, 127),  # (100, 155, 119),
                           WHITE  : (160, 166, 170),  # (155, 157, 172),
                           YELLOW : ( 63, 166, 191),  # ( 85, 165, 223),
                           RED    : (  4,   5, 144),  # (  5,   2, 155),
                           BLUE   : (143,  88,  31),  # (133,  75,  30),
                           ORANGE : (  4,  76, 178)}  # ( 11,  37, 181)}
"""
"""
# Speed cube w/ Matte Finish (TBD)
COLORS                  = {GREEN  : ( 85, 162, 127), #
                           WHITE  : (150, 150, 150), #
                           YELLOW : ( 37, 183, 190), # 
                           RED    : ( 13,   3, 134), # 
                           BLUE   : (155, 131,  82), # 
                           ORANGE : (  2,  55, 167)} # 
"""

COLOR_OFFSET            = 25
COLOR_UNKNOWN           = "X"

RED_THRESHOLD_0         = 100
RED_THRESHOLD_1         = 150
GREEN_THRESHOLD_0       = 30
GREEN_THRESHOLD_1       = 120
BLUE_THRESHOLD_0        = 30
BLUE_THRESHOLD_1        = 120

# Glossy speed cube light from right far away
#RGB_POINT               = [[241, 184, 0 ], [42 , 144, 165], [127 , 185, 73], [153 , 155, 150], [3  , 66 , 191], [0 , 0  , 174]]
# Glossy speeed cube LAB points light from right far away
#LAB_POINT               = [[134, 128, 77], [151, 125, 181], [175, 99, 150], [161, 125, 125], [114, 174, 182], [97, 187, 178]]

#Dec 2017 points
#RGB_POINT               = [[241, 184, 0 ], [44 , 216, 212], [127 , 185, 73], [153 , 155, 150], [17  , 110 , 249], [10 , 10  , 208]]
#LAB_POINT               = [[134, 128, 85], [151, 120, 175], [175, 93, 150], [161, 125, 125], [179, 170, 190], [97, 189, 170]]

# Glossy speed cube light from right far away
#RGB_POINT               = [[142, 73, 0 ], [80 , 157, 170], [127 , 185, 73], [183 , 173, 162], [25 , 115 , 208], [10 , 10  , 208]]
# Glossy speeed cube LAB points light from right far away
#LAB_POINT               = [[78, 137, 75], [167, 119, 174], [175, 93, 150], [180, 125, 120], [159, 165, 186], [75, 189, 170]]

# Glossy speed cube draker colors light from right far away
RGB_POINT               = [[142, 130, 0 ], [80 , 180, 215], [106 , 120, 59], [183 , 173, 162], [25 , 100 , 239], [10 , 10  , 190]]
# Glossy speeed cube darket colors LAB points light from right far away
LAB_POINT               = [[147, 140, 68], [186, 127, 181], [124, 93, 136], [180, 125, 120], [145, 170, 185], [97, 190, 175]]


# Matte speed cube
#RGB_POINT               = [[203, 176, 137 ], [27  , 156, 169], [107 , 185, 155], [121 , 125, 141], [2  , 55 , 202], [19  , 3  , 203]]

# Speed ccube with stickers
#RGB_POINT               = [[230, 174, 122 ], [92  , 200, 200], [167 , 225, 170], [168 , 182, 187], [35  , 109 , 230], [40  , 70  , 205]]





COLOR_DICT              = {0 : BLUE, 1 : YELLOW, 2 : GREEN, 3 : WHITE, 4 : ORANGE, 5 : RED}

# Face rotation directions
CLOCKWISE               = "CW"
COUNTER_CLOCKWISE       = "CCW"

# Cube rotation directions
ROTATE_FORWARD          = "F"

# Face Positions
FRONT                   = 2
BACK                    = 4
LEFT                    = 1
RIGHT                   = 3
TOP                     = 0
BOTTOM                  = 5

# Face Positions
FRONT_STR               = "F"
BACK_STR                = "B"
LEFT_STR                = "L"
RIGHT_STR               = "R"
TOP_STR                 = "U"
BOTTOM_STR              = "D"


#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------
class Face(object):
    dimension = None
    tiles     = None
    
    def __init__(self, color=None, tiles=None):
        self.dimension = 3
        if color is not None:
            self.tiles     = [color, color, color,
                              color, color, color,
                              color, color, color]
        else:
            if tiles is not None:
                self.tiles = tiles
            else:
                self.tiles = [COLOR_UNKNOWN, COLOR_UNKNOWN, COLOR_UNKNOWN,
                              COLOR_UNKNOWN, COLOR_UNKNOWN, COLOR_UNKNOWN,
                              COLOR_UNKNOWN, COLOR_UNKNOWN, COLOR_UNKNOWN]
    # End def

    def get_tile(self, position):
        return self.tiles[position]
    # End def
    
    def get_tiles(self):
        return self.tiles
    # End def

    def update_tile(self, position, color):
        self.tiles[position] = color
    # End def

    def update_tiles(self, tiles):
        for idx, tile in enumerate(tiles):
            self.update_tile(idx, tile)
    # End def

    def complete(self):
        ret_val = True
        
        for tile in self.tiles:
            if (tile == COLOR_UNKNOWN):
                ret_val = False
        
        return ret_val
    # End def

    def rotate_face(self, direction):
        current_face = list(self.tiles)
        
        if (direction == CLOCKWISE):
            self.tiles[0] = current_face[6]
            self.tiles[1] = current_face[3]
            self.tiles[2] = current_face[0]
            self.tiles[3] = current_face[7]
            self.tiles[4] = current_face[4]
            self.tiles[5] = current_face[1]
            self.tiles[6] = current_face[8]
            self.tiles[7] = current_face[5]
            self.tiles[8] = current_face[2]

        elif (direction == COUNTER_CLOCKWISE):
            self.tiles[0] = current_face[2]
            self.tiles[1] = current_face[5]
            self.tiles[2] = current_face[8]
            self.tiles[3] = current_face[1]
            self.tiles[4] = current_face[4]
            self.tiles[5] = current_face[7]
            self.tiles[6] = current_face[0]
            self.tiles[7] = current_face[3]
            self.tiles[8] = current_face[6]

        else:
            print("ERROR:  Unknown direction: {0}".format(direction))
    # End def
    
    def get_row_str(self, row):
        idx    = row * self.dimension
        output = " {0} {1} {2}".format(self.tiles[idx], self.tiles[idx + 1], self.tiles[idx + 2])
        return output
    # End def
    
    def print_face(self):
        for row in range(self.dimension):
            print(self.get_row_str(row))
    # End def
    
# End class


class Cube(object):
    dimension = None
    faces     = None
    
    def __init__(self, faces=None):
        self.dimension = 3
        if faces is None:
            self.faces = [Face(),  # Top    [0]
                          Face(),  # Left   [1]
                          Face(),  # Front  [2]
                          Face(),  # Right  [3]
                          Face(),  # Back   [4]
                          Face()]  # Bottom [5]
        else:
            self.faces = faces
    # End def

    def cube_complete(self):
        ret_val = True
        
        for face in self.faces:
            if not face.complete():
                ret_val = False
        
        return ret_val
    # End def
    
    def get_face(self, position):
        return self.faces[position]
    # End def
    
    def update_face(self, position, face):
        ret_val    = True
        curr_tiles = self.faces[position].get_tiles().copy()
        
        for idx, tile in enumerate(face.get_tiles()):
            current_color = self.faces[position].get_tile(idx)
            if (current_color == COLOR_UNKNOWN):
                self.faces[position].update_tile(idx, tile)
            else:
                if (current_color != tile):
                    print("WARNING: Scan of cube resulted in two diferent color values:  {0} and {1}".format(current_color, tile))
                    # Since there is a disagreement, update the value and return False so that we
                    # take another picture.  This means that two consequative scans have the same
                    # color value.
                    self.faces[position].update_tile(idx, tile)
                    ret_val = False
        
        #if not ret_val:
            # Restore original face
            # self.faces[position].update_tiles(curr_tiles)
        
        return ret_val
    # End def
    
    def swap_tile(self, src, dest):
        # Contains a tuple: (face number, position number)
        src_tile  = self.faces[ src[0]].get_tile( src[1])
        dest_tile = self.faces[dest[0]].get_tile(dest[1])
        
        self.faces[dest[0]].update_tile(dest[1],  src_tile)
        self.faces[ src[0]].update_tile( src[1], dest_tile)
    # End def
    
    def rotate_cube(self, direction):
        # Only supports forward direction currently
        current_faces = list(self.faces)
        
        if (direction == ROTATE_FORWARD):
            self.faces[TOP]    = current_faces[BACK]          # Back   moved to Top
            self.faces[LEFT].rotate_face(CLOCKWISE)           # Left   rotated  CW
            self.faces[FRONT]  = current_faces[TOP]           # Top    moved to Front
            self.faces[RIGHT].rotate_face(COUNTER_CLOCKWISE)  # Right  rotated  CCW
            self.faces[BACK]   = current_faces[BOTTOM]        # Bottom moved to Back
            self.faces[BOTTOM] = current_faces[FRONT]         # Front  moved to Bottom
            
            # Note:  When you move the bottom to the back, or the back to the top
            #    the face will actually rotate 180 degrees from our viewing angle
            self.faces[TOP].rotate_face(CLOCKWISE)
            self.faces[TOP].rotate_face(CLOCKWISE)
            
            self.faces[BACK].rotate_face(CLOCKWISE)
            self.faces[BACK].rotate_face(CLOCKWISE)
        else:
            print("ERROR: Direction not supported.")
        pass
    # End def
    
    def rotate_cube_face(self, position, direction):
        # Only supports back face (ie self.faces[4])
        if (position == BACK):
            if (direction == CLOCKWISE):
                # Rotate face
                self.faces[BACK].rotate_face(CLOCKWISE)
                
                # Swap tiles on the edges
                #   *** Order of operations matters; only need 3 sets of swaps
                #   Top    [0, 1, 2] -> Left   [6, 3, 0]
                #   Right  [2, 5, 8] -> Top    [0, 1, 2]
                #   Bottom [6, 7, 8] -> Right  [8, 5, 2]
                #   Left   [0, 3, 6] -> Bottom [6, 7, 8]
                self.swap_tile((TOP,    0), (LEFT,   6))
                self.swap_tile((TOP,    1), (LEFT,   3))
                self.swap_tile((TOP,    2), (LEFT,   0))
                
                self.swap_tile((RIGHT,  2), (TOP,    0))
                self.swap_tile((RIGHT,  5), (TOP,    1))
                self.swap_tile((RIGHT,  8), (TOP,    2))
                
                self.swap_tile((BOTTOM, 6), (RIGHT,  8))
                self.swap_tile((BOTTOM, 7), (RIGHT,  5))
                self.swap_tile((BOTTOM, 8), (RIGHT,  2))
                    
            elif (direction == COUNTER_CLOCKWISE):
                # Rotate face
                self.faces[BACK].rotate_face(COUNTER_CLOCKWISE)
                
                # Swap tiles on the edges
                #   *** Order of operations matters; only need 3 sets of swaps
                #   Top    [0][0, 1, 2] -> Right  [3][2, 5, 8]
                #   Left   [1][0, 3, 6] -> Top    [0][2, 1, 0]
                #   Bottom [5][6, 7, 8] -> Left   [1][0, 3, 6]
                #   Right  [3][2, 5, 8] -> Bottom [5][8, 7, 6]
                self.swap_tile((TOP,    0), (RIGHT,  2))
                self.swap_tile((TOP,    1), (RIGHT,  5))
                self.swap_tile((TOP,    2), (RIGHT,  8))
                
                self.swap_tile((LEFT,   0), (TOP,    2))
                self.swap_tile((LEFT,   3), (TOP,    1))
                self.swap_tile((LEFT,   6), (TOP,    0))
                
                self.swap_tile((BOTTOM, 6), (LEFT,   0))
                self.swap_tile((BOTTOM, 7), (LEFT,   3))
                self.swap_tile((BOTTOM, 8), (LEFT,   6))
                
            else:
                print("ERROR:  Unknown direction: {0}".format(direction))
        else:
            print("ERROR: Position not supported: {0}".format(position))
    # End def
    
    def get_color_counts(self):
        counts = {GREEN         : 0,
                  WHITE         : 0,
                  YELLOW        : 0,
                  RED           : 0,
                  BLUE          : 0,
                  ORANGE        : 0,
                  COLOR_UNKNOWN : 0}
        
        for face in self.faces:
            for tile in face.get_tiles():
                counts[tile] += 1

        return counts
    # End def
    
    def infer_side_centers(self):
        # From 4 faces, we can infer the other two faces:
        #   [W, R, Y, O] -> L = B; R = G
        #   [W, O, Y, R] -> L = G; R = B
        #   [W, B, Y, G] -> L = O; R = R
        #   [W, G, Y, B] -> L = R; R = O
        #   [B, R, G, O] -> L = Y; R = W
        #   [B, O, G, R] -> L = W; R = Y
        ret_val       = True
        inference_map = {GREEN  : {WHITE  : (RED   , ORANGE),
                                   YELLOW : (ORANGE, RED   ),
                                   RED    : (YELLOW, WHITE ),
                                   ORANGE : (WHITE , YELLOW)},
                         WHITE  : {GREEN  : (ORANGE, RED   ),
                                   RED    : (GREEN , BLUE  ),
                                   BLUE   : (RED   , ORANGE),
                                   ORANGE : (BLUE  , GREEN )},
                         YELLOW : {GREEN  : (RED   , ORANGE),
                                   RED    : (BLUE  , GREEN ),
                                   BLUE   : (ORANGE, RED   ),
                                   ORANGE : (GREEN , BLUE  )},
                         RED    : {GREEN  : (WHITE , YELLOW),
                                   WHITE  : (BLUE  , GREEN ),
                                   YELLOW : (GREEN , BLUE  ),
                                   BLUE   : (YELLOW, WHITE )},
                         BLUE   : {WHITE  : (ORANGE, RED   ),
                                   YELLOW : (RED   , ORANGE),
                                   RED    : (WHITE , YELLOW),
                                   ORANGE : (YELLOW, WHITE )},
                         ORANGE : {GREEN  : (YELLOW, WHITE ),
                                   WHITE  : (GREEN , BLUE  ),
                                   YELLOW : (BLUE  , GREEN ),
                                   BLUE   : (WHITE , YELLOW)}}
 
        t_center = self.faces[   TOP].get_tile(4)
        f_center = self.faces[ FRONT].get_tile(4)

        try:
            self.faces[  LEFT].update_tile(4, inference_map[t_center][f_center][0])
            self.faces[ RIGHT].update_tile(4, inference_map[t_center][f_center][1])
        except:
            print("ERROR: Could not infer cube sides.")
            self.print_cube()
            ret_val = False

        return ret_val
        # print("LEFT  = {0}".format(inference_map[t_center][f_center][0]))
        # print("RIGHT = {0}".format(inference_map[t_center][f_center][1]))
    # End def
    
    def infer_last_tile(self):
        counts    = self.get_color_counts()
        last_tile = None
        
        for count in counts.keys():
            if (count != COLOR_UNKNOWN):
                if (counts[count] != 9):
                    last_tile = count
        
        if ((counts[COLOR_UNKNOWN] == 1) and (last_tile is not None)):
            for face in self.faces:
                for idx, tile in enumerate(face.get_tiles()):
                    if (tile == COLOR_UNKNOWN):
                         face.update_tile(idx, last_tile)
        else:
            print("WARNING: Could not infer last tile.")
            self.print_cube()
    # End def
    
    def create_string(self):
        """""
        The names of the facelet positions of the cube
                      |************|
                      |*U1**U2**U3*|
                      |************|
                      |*U4**U5**U6*|
                      |************|
                      |*U7**U8**U9*|
                      |************|
         |************|************|************|************|
         |*L1**L2**L3*|*F1**F2**F3*|*R1**R2**F3*|*B1**B2**B3*|
         |************|************|************|************|
         |*L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*|
         |************|************|************|************|
         |*L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*|
         |************|************|************|************|
                      |************|
                      |*D1**D2**D3*|
                      |************|
                      |*D4**D5**D6*|
                      |************|
                      |*D7**D8**D9*|
                      |************|
    
        A cube definition string "UBL..." means for example: In position U1 we have the U-color, in position U2 we have the
        B-color, in position U3 we have the L color etc. according to the order U1, U2, U3, U4, U5, U6, U7, U8, U9, R1, R2,
        R3, R4, R5, R6, R7, R8, R9, F1, F2, F3, F4, F5, F6, F7, F8, F9, D1, D2, D3, D4, D5, D6, D7, D8, D9, L1, L2, L3, L4,
        L5, L6, L7, L8, L9, B1, B2, B3, B4, B5, B6, B7, B8, B9 of the enum constants.
        """
        output = ""
        
        # Create color -> face mapping dictionary
        #   - Use center of each face to make the mapping 
        c2f_map = {self.faces[   TOP].get_tile(4) : TOP_STR,
                   self.faces[  LEFT].get_tile(4) : LEFT_STR,
                   self.faces[ FRONT].get_tile(4) : FRONT_STR,
                   self.faces[ RIGHT].get_tile(4) : RIGHT_STR,
                   self.faces[  BACK].get_tile(4) : BACK_STR,
                   self.faces[BOTTOM].get_tile(4) : BOTTOM_STR}
        
        # Print string in U->L->F->R->B->D order
        # for face in self.faces:
        #     for tile in face.get_tiles():
        #         output += c2f_map[tile]

        # Print string in U->R->F->D->L->B order for the solver
        for tile in self.faces[TOP].get_tiles():
            output += c2f_map[tile]
        for tile in self.faces[RIGHT].get_tiles():
            output += c2f_map[tile]
        for tile in self.faces[FRONT].get_tiles():
            output += c2f_map[tile]
        for tile in self.faces[BOTTOM].get_tiles():
            output += c2f_map[tile]
        for tile in self.faces[LEFT].get_tiles():
            output += c2f_map[tile]
        for tile in self.faces[BACK].get_tiles():
            output += c2f_map[tile]
        
        return output
    # End def
    
    def print_cube(self):
        space  = "  "
        output = ""
        
        # Print Top
        face    = self.faces[TOP]
        for row in range(self.dimension):
            output += space * self.dimension
            output += face.get_row_str(row) + "\n"
        
        # Print Middle
        for row in range(self.dimension):
            output += self.faces[LEFT].get_row_str(row) + self.faces[FRONT].get_row_str(row) + self.faces[RIGHT].get_row_str(row) + self.faces[BACK].get_row_str(row) + "\n"
        
        # Print Bottom
        face    = self.faces[BOTTOM]
        for row in range(self.dimension):
            output += space * self.dimension
            output += face.get_row_str(row) + "\n"
    
        print(output)
    # End def
    
    def image_cube(self):
        
        color_dict = {'G': 'green', 'B': 'blue', 'O': 'orange', 'R': 'red', 'Y': 'yellow', 'W': 'white'}
        face_dict = {0 : TOP, 1 : LEFT, 2 : FRONT, 3 : RIGHT, 4 : BACK, 5 : BOTTOM}
        origx_dict = {0 : 250, 1 : 100, 2 : 250, 3 : 400, 4 : 550, 5 : 250}
        origy_dict = {0 : 100, 1 : 250, 2 : 250, 3 : 250, 4 : 250, 5 : 400}
        
        img = Image.new('RGB', (800, 800), color = 'white')
        d = ImageDraw.Draw(img)
        for i in range(6):
            face = self.faces[face_dict[i]]
            originx = origx_dict[i]
            originy = origy_dict[i]
            face_positions = [[originx, originy], [originx + 50, originy], [originx + 100, originy], 
                            [originx, originy + 50], [originx + 50, originy + 50], [originx + 100, originy + 50], 
                            [originx, originy + 100], [originx + 50, originy + 100], [originx + 100, originy + 100]]
            for row in range(self.dimension):
                block = face.get_row_str(row)
                d.rectangle(face_positions[row*3] + [x + 48 for x in face_positions[row*3]], fill=color_dict[block[1]], outline='black')
                d.rectangle(face_positions[row*3 + 1] + [x + 48 for x in face_positions[row*3 + 1]], fill=color_dict[block[3]], outline='black')
                d.rectangle(face_positions[row*3 + 2] + [x + 48 for x in face_positions[row*3 + 2]], fill=color_dict[block[5]], outline='black')
        img.save('pil_text_font.png')
        
    def verify_cube(self):
        ret_val = True
        
        if self.cube_complete():
            counts = self.get_color_counts()
            
            if (counts[COLOR_UNKNOWN] != 0):
                ret_val = False
            
            for count in counts.keys():
                if (count != COLOR_UNKNOWN):
                    if (counts[count] != 9):
                        ret_val = False
        else:
            ret_val = False
            
        if not ret_val:
            print("ERROR scanning cube.  Please re-scan.")
        
        return ret_val
    # End def
    
# End class


#-----------------------------------------------------------------------------
# Function Definitions
#-----------------------------------------------------------------------------
def capture_image(camera, width, height, debug=False, verbose=False):    
    # Set image capture size
    #   camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    #   camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)           # turn the autofocus off
    # os.system(uvcdynctrl -s "white balance temperature, auto" 0 )
    # camera.set(cv2.CAP_PROP_BRIGHTNESS, 0.4)
    # camera.set(cv2.CAP_PROP_CONTRAST, 0.1)
    # camera.set(cv2.CAP_PROP_SATURATION, 0.4)
    # camera.set(cv2.CAP_PROP_HUE, 0)
    # camera.set(cv2.CAP_PROP_GAIN, 1)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)           # turn the autofocus off
    
    time.sleep(2)
    # Capture image
    ret, frame = camera.read()

    # Wait for a bit
    # time.sleep(0.2)

    # Return image or None    
    if (ret):
        return frame
    else:
        return None
# End def


def match_color(color, verbose=False):
    ret_val = COLOR_UNKNOWN
    
    '''#Eucledian distance method
    dist = []
    for i in range(0, 6):
        dist.append([(color[0] - RGB_POINT[i][0]) ** 2 + (color[1] - RGB_POINT[i][1]) ** 2 + (color[2] - RGB_POINT[i][2]) ** 2])
    
    ret_val = COLOR_DICT[dist.index(min(dist))]'''
    
    color_rgb = np.uint8([[[int(color[0]), int(color[1]), int(color[2])]]])
    color_lab = cv2.cvtColor(color_rgb, cv2.COLOR_BGR2LAB)
    color_hsv = cv2.cvtColor(color_rgb, cv2.COLOR_BGR2HSV)

    for i in range(0, 6):
        if abs(color_lab[0][0][1] - LAB_POINT[i][1]) < 17 and abs(color_lab[0][0][2] - LAB_POINT[i][2]) < 17:
            ret_val = COLOR_DICT[i]
            
            if ret_val == ORANGE or ret_val == YELLOW or ret_val == RED:
                if abs(color_rgb[0][0][1] - RGB_POINT[4][1]) < 20:
                    ret_val = ORANGE
                elif abs(color_rgb[0][0][1] - RGB_POINT[5][1]) < 20:
                    ret_val = RED
                elif abs(color_rgb[0][0][1] - RGB_POINT[1][1]) < 20:
                    ret_val = YELLOW
            break
        
    # Check color based on thresholds
    # if ((abs(color[0] - color[1]) < 40) and (abs(color[0] - color[2]) < 40) and 
    #     (abs(color[1] - color[2]) < 40)):
    '''if ((abs(color[0] - color[1]) < 40) and (abs(color[1] - color[2]) < 40)):
        if (color[1] > 170):
            ret_val = WHITE
        else:
            ret_val = BLUE
            
    elif ((color[0] <  30) and (color[2] > 100)):
        if (color[1] <  40):
            ret_val = RED
        elif (color[1] < 100):
            ret_val = ORANGE
        elif (color[2] > 140):
            ret_val = YELLOW

    elif ((color[0] < 100) and (color[1] > 100) and (color[2] > 140)):
        ret_val = YELLOW

    elif ((color[0] < 130) and (color[1] > 150) and (color[2] < 170)):
        ret_val = GREEN
    
    elif ((color[0] > 100) and (color[1] < 140) and (color[2] < 100)):
        ret_val = BLUE'''
    
    
    """
    # Check color based on thresholds
    if ((color[0] > 100) and (color[1] > 100) and (color[2] > 100)):
        ret_val = WHITE
    
    if ((color[0] < 100) and (color[1] > 100) and (color[2] > 100)):
        ret_val = YELLOW
    
    if ((color[0] <  30) and (color[1] <  30) and (color[2] > 100)):
        ret_val = RED
    
    if ((color[0] <  30) and (color[1] < 100) and (color[2] > 100)):
        ret_val = ORANGE
    
    if ((color[0] < 120) and (color[1] > 100) and (color[2] >  80)):
        ret_val = GREEN
    
    if ((color[0] > 100) and (color[1] < 140) and (color[2] < 100)):
        ret_val = BLUE
    """
    """
    # Check color based on thresholds
    #   NOTE:  This method can have issues if there is any marks on the cube
    #       Could add special case for WHITE center
    if (color[0] < BLUE_THRESHOLD_0):
        if (color[1] < GREEN_THRESHOLD_0):
            ret_val = RED
        elif (color[1] > GREEN_THRESHOLD_1):
            ret_val = YELLOW
        else:
            ret_val = ORANGE
    elif(color[0] > BLUE_THRESHOLD_1):
        if (color[2] < RED_THRESHOLD_0):
            ret_val = BLUE
        else:
            ret_val = WHITE
    else:
        if (color[2] < RED_THRESHOLD_1):
            ret_val = GREEN
        else:
            ret_val = YELLOW
    """
    """
    # This method is not that reliable as lighting conditions / cubes change 
    #
    # Check each color for a match
    for c in COLORS.keys():
        if ((color[0] > (COLORS[c][0] - COLOR_OFFSET)) and
            (color[0] < (COLORS[c][0] + COLOR_OFFSET)) and
            (color[1] > (COLORS[c][1] - COLOR_OFFSET)) and 
            (color[1] < (COLORS[c][1] + COLOR_OFFSET)) and
            (color[2] > (COLORS[c][2] - COLOR_OFFSET)) and 
            (color[2] < (COLORS[c][2] + COLOR_OFFSET))):
            return c
    """
        
    # Print color choice
    if (verbose):
        print("Color RGB {0}: {1}, {2}, {3}".format(ret_val, color[0], color[1], color[2]))  
        print("Color LAB {0}: {1}, {2}, {3}".format(ret_val, color_lab[0][0][0], color_lab[0][0][1], color_lab[0][0][2])) 
    
    return ret_val
# End def


def show_cube_alignment(image):
    # Update image
    for tile in TILES:
        (x,y,w,h) = (tile[0], tile[1], tile[2], tile[3])
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)                
   
    print('Cube Alignment')
    cv2.imwrite('cube_alignment.png', image)
# End def


def process_cube_image(cube, camera, image, debug=False, verbose=False):
    # Performance monitor
    if (verbose):
        print('Processing Image')
        start_time = time.time()


    # Write original image
    if (debug):
        print('Write original image')
        cv2.imwrite('cube_01_orig.png', image)

        
    # Convert image to Grayscale
    if (False):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if (debug):
            print('Convert Grayscale image')
            cv2.imwrite('cube_02_gray.png', gray)
    else:
        gray = image


    # Blur image to reduce background noise
    if (False):
        blur = cv2.GaussianBlur(gray, (7, 7), 1.5, 1.5)
        
        if (debug):
            print('Bluring image')
            cv2.imwrite('cube_03_blur.png', blur)
    else:
        blur = gray


    # Perform edge detection
    if (False):
        edges = cv2.Canny(blur, 0, 30, 3)
        
        if (debug):
            print('Edges image')
            cv2.imwrite('cube_04_edge.png', edges)
    else:
        edges = blur


    # Perform edge dilation
    if (False):
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)        
        
        if (debug):
            print('Dilated Edges image')
            cv2.imwrite('cube_05_dilated.png', dilated)
    else:
        dilated = edges
        
    
    # Find contours
    if (False):
        squares = []
        contours, hierarchy = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Test each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            if ((area > AREA_MIN) and (area < AREA_MAX)):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Contour must be a square
                if (abs(w - h) < HIGHT_WIDTH_DIFF_MAX):                
                    squares.append((x, y, w, h))

        # Remove duplicates rectangles
        tiles  = []
        offset = DUPLICATE_OFFSET
        
        for square in squares:
            append = True
            
            for tile in tiles:
                if ((square[0] >= (tile[0] - offset)) and 
                    (square[0] <= (tile[0] + offset)) and
                    (square[1] >= (tile[1] - offset)) and
                    (square[1] <= (tile[1] + offset))):
                    append = False
            
            if (append):
                tiles.append(square)

        if (debug):
            # Update image
            for tile in tiles:
                (x,y,w,h) = (tile[0], tile[1], tile[2], tile[3])
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)                
                print("{0} {1} {2} {3}".format(x, y, w, h))
            
            print('Countours image')
            cv2.imwrite('cube_06_tiles.png', image)
    else:
        tiles = []
    
    
    # Stop of no squares are found
    if (len(tiles) != 9):
        if (verbose):
            print("WARNING:  Could not process image correctly. Using ideal locations.")
            
        if (debug):
            print(tiles)

        # Continue with ideal tiles        
        tiles = TILES


    # Sort the squares
    #   - There can be some slop in the squares so we need to get common x and y
    #     so we can properly sort the cubes
    if (True):
        max_width  = max(tiles, key=lambda item: item[2])[2]
        max_height = max(tiles, key=lambda item: item[3])[3]
        nearest    = max_height * 1.2                  # Might have issues

        sorted_tiles = sorted(tiles, key=lambda r: (int(nearest * round(float(r[1])/nearest)) * max_width + r[0]))
    else:
        sorted_tiles = tiles
    
    if (debug):
        print(sorted_tiles)


    # Find color of squares
    #   - Crop squares so there are no problems
    results = []
    
    for idx, result in enumerate(sorted_tiles):
        (x,y,w,h) = (result[0], result[1], result[2], result[3])

        # Use inner 1/4 of cube for color measurement        
        x1_crop = int(x + w/4)
        y1_crop = int(y + h/4)
        x2_crop = int(x1_crop + w/2)
        y2_crop = int(y1_crop + h/2)
        try:
            roi     = image[y1_crop:y2_crop, x1_crop:x2_crop]
        except:
            print("ERROR:  BAD IMAGE")
            return results

        # Get color
        color = cv2.mean(roi)
        c     = match_color(color, verbose)

        # Add to Face
        results.append(c)
        
        if (debug):
            cv2.imwrite('cube_07_{0}_roi.png'.format(idx), roi)


    if (verbose):
        total_time = time.time() - start_time
        print("    Processing Time = {0:10.2f} seconds".format(total_time))
    
    if 'X' in results:
        results = init_face(cube, camera, debug, verbose)
    
    print(results)
    return results

# End def


def calibrate_color(camera, debug=False, verbose=False):
    

    tiles   = TILES
    
    rgb_image = capture_image(camera, IMAGE_WIDTH, IMAGE_HEIGHT, debug, verbose)
    show_cube_alignment(rgb_image)
    lab_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2LAB)
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2HSV)

    # Find color of squares
    #   - Crop squares so there are no problems
    rgb          = { 0 : [],
                     1 : [],
                     2 : [] }
    lab          = { 0 : [],
                     1 : [],
                     2 : [] }
    hsv          = { 0 : [],
                     1 : [],
                     2 : [] }
    color_spaces = {"RGB" : rgb,
                    "LAB" : lab, 
                    "HSV" : hsv }

    for idx, tile in enumerate(tiles):
        (x,y,w,h) = (tile[0], tile[1], tile[2], tile[3])

        # Use inner 1/4 of cube for color measurement        
        x1_crop = int(x + w/4)
        y1_crop = int(y + h/4)
        x2_crop = int(x1_crop + w/2)
        y2_crop = int(y1_crop + h/2)
        
        try:
            rgb_roi     = rgb_image[y1_crop:y2_crop, x1_crop:x2_crop]
            lab_roi     = lab_image[y1_crop:y2_crop, x1_crop:x2_crop]
            hsv_roi     = hsv_image[y1_crop:y2_crop, x1_crop:x2_crop]
        except:
            print("ERROR:  BAD IMAGE")
            return

        # Get color
        rgb_color = cv2.mean(rgb_roi)
        lab_color = cv2.mean(lab_roi)
        hsv_color = cv2.mean(hsv_roi)

        # Add to results
        rgb[0].append(rgb_color[0])
        rgb[1].append(rgb_color[1])
        rgb[2].append(rgb_color[2])
        
        lab[0].append(lab_color[0])
        lab[1].append(lab_color[1])
        lab[2].append(lab_color[2])

        hsv[0].append(hsv_color[0])
        hsv[1].append(hsv_color[1])
        hsv[2].append(hsv_color[2])


    output_str = ""
    
    # Generate single RGB value
    for space in color_spaces.keys():
        
        min_0 = min(color_spaces[space][0])
        max_0 = max(color_spaces[space][0])
        val_0 = int(min_0 + ((max_0 - min_0) / 2))

        min_1 = min(color_spaces[space][1])
        max_1 = max(color_spaces[space][1])
        val_1 = int(min_1 + ((max_1 - min_1) / 2))

        min_2 = min(color_spaces[space][2])
        max_2 = max(color_spaces[space][2])
        val_2 = int(min_2 + ((max_2 - min_2) / 2))

        output_str += "{0}\t{1}\t{2}\t{3}\t".format(space, val_0, val_1, val_2)

    print(output_str)

    return (None, None, None)
# End def


def init_face(cube, camera, debug=False, verbose=False):
    success = False
    
    while not success:
        image   = capture_image(camera, IMAGE_WIDTH, IMAGE_HEIGHT, debug, verbose)
        show_cube_alignment(image)

        results = process_cube_image(cube, camera, image, debug, verbose)

        if results:
            success = cube.update_face(FRONT, Face(tiles=results)) 
        else:
            return
    
# End def    



def init_cube(debug=False, verbose=False):
    cube   = None
    repeat = True
    camera = cv2.VideoCapture(0)

    if (verbose):
        print("Initialize Cube")

    while repeat:
        cube = Cube()
        
        # Move sequence to cover all faces
        if (verbose):
            cube.print_cube()
        
        # Step 1
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 2
        move_arms()
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 3
        move_arms()
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 4
        move_arms()
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
    
        # Infer centers of the sides at this point
        cube.infer_side_centers()
    
        if (verbose):
            cube.print_cube()
            
        # Step 5
        move_arms()
        cube.rotate_cube_face(BACK, CLOCKWISE)
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 6
        move_arms()
        cube.rotate_cube(ROTATE_FORWARD)
        cube.rotate_cube_face(BACK, COUNTER_CLOCKWISE)
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 7
        move_arms()
        cube.rotate_cube_face(BACK, COUNTER_CLOCKWISE)
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
    
        # Step 8
        move_arms()
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        if (verbose):
            cube.print_cube()
        
        # Step 9
        move_arms()
        cube.rotate_cube_face(BACK, CLOCKWISE)
        cube.rotate_cube(ROTATE_FORWARD)
        init_face(cube, camera, debug, verbose)
        
        # Infer last tile
        cube.infer_last_tile()
        
        if (verbose):
            cube.print_cube()
    
        if cube.verify_cube():
            repeat = False
        else:
            # Pause to reset cube
            move_arms()
            
    # End while
        
    # Create cube output string
    output = cube.create_string()
        
    if (verbose):
        print("Cube String:  {0}".format(output))

    # Release camera
    camera.release()            
    
    return output
# End def


def move_arms():
    # DUMMY FUNCTION - Will be expanded 
    # Wait for key proess
    try:
        input("Press Enter to continue...")
    except:
        pass
    
# End def


def usage(exit_level=None):
    import sys
    
    print("Usage:  read_rubiks_cube.py [hdva]")
    
    if exit_level is not None:
        sys.exit(exit_level)
# End def


#-----------------------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import getopt

    debug      = False
    verbose    = False
    align      = False
    calibrate  = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "hdvac", 
                                   ["help", "debug", "verbose", "align", "calibrate"])
    except getopt.GetoptError:
        usage(exit_level=2)
 
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(exit_level=0)
        elif opt in ("-d", "--debug"):
            debug      = True
        elif opt in ("-v", "--verbose"):
            verbose    = True
        elif opt in ("-a", "--align"):
            align      = True
        elif opt in ("-c", "--calibrate"):
            calibrate  = True


    if (align):
        print("Showing cube alignment")
        camera = cv2.VideoCapture(0)
        image = capture_image(camera, IMAGE_WIDTH, IMAGE_HEIGHT, debug, verbose)
        show_cube_alignment(image)
        camera.release()
    elif (calibrate):
        print("Color calibration")
        
        for i in range(9):
            camera = cv2.VideoCapture(0)
            color = calibrate_color(camera, debug, verbose)
            camera.release()
        
    else:
        cube_str = init_cube(debug, verbose)            
        print(cube_str)
    

            
            
    """
    g_face = Face(color=GREEN)
    w_face = Face(color=WHITE)
    y_face = Face(color=YELLOW)
    r_face = Face(color=RED)
    b_face = Face(color=BLUE)
    o_face = Face(color=ORANGE)
    
    faces  = [w_face, g_face, r_face, b_face, o_face, y_face]

    cube = Cube(faces)
    
    # Move sequence to cover all faces
    print("Cube Move sequence")
    
    # set last tile to unknown
    cube.get_face(LEFT ).update_tile(3, COLOR_UNKNOWN)
    
    # set left / right centers to unknown
    cube.get_face(LEFT ).update_tile(4, COLOR_UNKNOWN)
    cube.get_face(RIGHT).update_tile(4, COLOR_UNKNOWN)
    
    
    # Step 1
    cube.print_cube()

    # Step 2
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Step 3
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Step 4
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Infer centers of the sides at this point
    cube.infer_side_centers()
        
    # Step 5
    cube.rotate_cube_face(BACK, CLOCKWISE)
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Step 6
    cube.rotate_cube(ROTATE_FORWARD)
    cube.rotate_cube_face(BACK, COUNTER_CLOCKWISE)
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Step 7
    cube.rotate_cube_face(BACK, COUNTER_CLOCKWISE)
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()

    # Step 8
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()
    
    # Step 9
    cube.rotate_cube_face(BACK, CLOCKWISE)
    cube.rotate_cube(ROTATE_FORWARD)
    cube.print_cube()
    
    # Infer last tile
    cube.infer_last_tile()
    cube.print_cube()

    print(cube.create_string())



    """     
    """
    # Get camera
    camera = cv2.VideoCapture(0)

    print("Capture Image")
    image = capture_image(camera, IMAGE_WIDTH, IMAGE_HEIGHT, debug, verbose)
    
    if (align):
        print("Showing cube alignment")
        show_cube_alignment(image)
    else:
        print("Process Image")
        results = process_cube_image(image, debug, verbose)
        
        print(results)
        
        print("Results:")
        output = ""
        for result in results:
            if ((result[0] % 3) == 0):
                output += "| "
            
            if type(result[1]) is tuple:
                output += "({:>3},".format(int(result[1][0]))
                output += " {:>3},".format(int(result[1][1]))
                output += " {:>3}) ".format(int(result[1][2]))
            else:
                output += "{0} ".format(result[1])
            
            if ((result[0] % 3) == 2):
                output += "|\n"
        print(output)        

    # Release camera
    camera.release()            
    """

# End main
