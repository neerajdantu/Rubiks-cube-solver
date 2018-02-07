# -*- coding: utf-8 -*-
"""
--------------------------------------------------------------------------
Rubik's Cube Solver Sevo Control
--------------------------------------------------------------------------
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

--------------------------------------------------------------------------

Authors:   Neeraj Dantu (neeraj.dantu [at] octavosystems.com)
License:   Copyright 2017, Octavo Systems. All rights reserved.
           Distributed under the Octavo Systems license (LICENSE)
          
Description: This file contains all the classes and methods to control the arms 
of the Rubik's cube solver demo

Class ServoMotor:
    - Members
      - HoldServo, RotateServo
    - Methods
      - position
      - channel

Class HoldServo:
    - Members
      - left_arm.HoldServo, right_arm.HoldServo, back_arm.HoldServo
    - Methods
      - hol_set_position
      - hol_get_position
      
Class RotateServo:
    - Members
      - left_arm.RotateServo, right_arm.RotateServo, back_arm.RotateServo
    - Methods
      - rot_set_position
      - rot_get_position

Class RobotArm:
    - Members
      - left_arm, right_arm, back_arm
    - Methods
      - arm_loaction
      - get_current_position
      - get_current_motor_position
      - move_rep_vert_close
      - move_rep_neg_horz
      - move_rep_pos_horz
      - move_rotate_clwise
      - move_rotate_ccwise
      - move_rep_vert_open
      - set_position
      
Class Move:
    - Members
      
    - Methods
      - rotate_cube
      - rotate_right
      - rotate_left
      - rotate_back
      - rotate_down
      - rotate_front
      - rotate_top
      - execute
      - hold_cube
      - execute_seq
      - move_interpretor
      - move_reposition_default

Class move_struct:
    - Members
    
    - Methods
      - add_seq_chan
      - get_move_struct

------------------------------------------------------------------------------
Known Issues:
          
           
"""

import rcpy.servo as servo
import time

#-----------------------------------------------------------------------------
# Global Variables
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------

class ServoMotor:
    
    def __init__(self, position, channel):
        #properties
        self.position = position
        self.pulse_interval = 0.02
        self.channel = channel
    
    @property
    def position(self):
        '''Get current position of servo motor'''
        return self._position
    
    @position.setter
    def position(self, p):
        if (p < -2) or (p > 2):
            raise Exception('Motor position not valid')
        else:
            self._position = p

    @property
    def channel(self):
        '''Get the channel of  servo motor'''
        
        return self._channel
    
    @channel.setter
    def channel(self, ch):
        
        if (ch <= 0) or (ch > 6):
            raise Exception('Motor channel number is invalid')
        else:
            self._channel = ch



class RotateServo(ServoMotor):
    
    def __init__(self, channel, horz_pos, vert_nue, horz_neg):
        # position disctionlaries 
        self.rot_position_dict = {'horz_positive' : horz_pos, 
                                  'vert_nuetral'  : vert_nue, 
                                  'horz_negative' : horz_neg }
        
        self.rot_revposition_dict = {horz_pos : 'horz_positive', 
                                     vert_nue : 'vert_nuetral', 
                                     horz_neg : 'horz_negative'}
    
        self.duty = self.rot_position_dict['vert_nuetral']
        super().__init__(self.duty, channel)
    
    def rot_get_position(self):
        
        return self.rot_revposition_dict[self.duty]
        
    def rot_set_postion(self, rot_position):
        
        self.position = self.rot_position_dict[rot_position]



class HoldServo(ServoMotor):
    # servo position dicitionaries
    hol_position_dict = {'open' : 1.0, 'close' : 0.3}
    hol_revposition_dict = {1.0 : 'open', 0.3 : 'close'}
    
    def __init__(self, channel):
        
        self.duty = self.hol_position_dict['close']
        super().__init__(self.duty, channel)
        
    def hol_get_position(self):
        
        return self.hol_revposition_dict[self.duty]
        
    def hol_set_position(self, hol_position):
        
        self.position = self.hol_position_dict[hol_position]

class RobotArm():
    
    def __init__(self, arm_location):
        
        self.arm_location = arm_location

        # Servo calibration values        
        if self.arm_location == 'left':
            # can be chnaged according to setup
            self.horz_pos   = -1.47#-1.45
            self.vert_nue   = 0.1#0.1
            self.horz_neg   = 1.7#1.7
            self.hold_open  = 1.0#1.0
            self.hold_close = 0.3#0.3
            self.motor_hol  = HoldServo(6)
            self.motor_rot  = RotateServo(5, self.horz_pos, self.vert_nue, self.horz_neg)
        
        elif self.arm_location == 'back':
            # can be chnaged according to setup
            self.horz_neg   = -1.37#-1.32
            self.vert_nue   = 0.15#0.15
            self.horz_pos   = 1.5#1.5
            self.hold_open  = 1.0#1.0
            self.hold_close = 0.3#0.3
            self.motor_hol  = HoldServo(4)
            self.motor_rot  = RotateServo(3, self.horz_pos, self.vert_nue, self.horz_neg)

        elif self.arm_location == 'right':
            # can be chnaged according to setup
            self.horz_neg   = -1.4#-1.4
            self.vert_nue   = -0.05#-0.05
            self.horz_pos   = 1.4#1.4
            self.hold_open  = 1.0#1.0
            self.hold_close = 0.3#0.3
            self.motor_hol  = HoldServo(2)
            self.motor_rot  = RotateServo(1, self.horz_pos, self.vert_nue, self.horz_neg)

        else:
            raise Exception('Motor position not valid')

        # Lookup tables        
        self.arm_position_dict = {'horz_pos_open' : [self.horz_pos, self.hold_open], 
                                  'horz_pos_clos' : [self.horz_pos, self.hold_close], 
                                  'horz_neg_open' : [self.horz_neg, self.hold_open], 
                                  'horz_neg_clos' : [self.horz_neg, self.hold_close], 
                                  'vert_open'     : [self.vert_nue, self.hold_open], 
                                  'vert_clos'     : [self.vert_nue, self.hold_close]}
                                  
        self.arm_position_lookup = { (self.horz_pos, self.hold_open)  : 'horz_pos_open', 
                                     (self.horz_pos, self.hold_close) : 'horz_pos_clos', 
                                     (self.horz_neg, self.hold_open)  : 'horz_neg_open', 
                                     (self.horz_neg, self.hold_close) : 'horz_neg_clos', 
                                     (self.vert_nue, self.hold_open)  : 'vert_open', 
                                     (self.vert_nue, self.hold_close) : 'vert_clos'}

        # Initial position
        self.arm_position       = 'vert_clos'
        
    @property
    def arm_location(self):
        '''Get current location of the arm'''
        
        return self._arm_location
    
    @arm_location.setter
    def arm_location(self, p):
        
        if p != 'left' and p != 'right' and p != 'back':
            raise Exception('Motor location not valid')
        else:
            self._arm_location = p
    
    def get_current_position(self):
        
        return self.arm_position
    
    def get_current_motor_position(self):
        
        return self.arm_position_dict[self.arm_position]
    
    
    def move_rep_vert_close(self):
        # generates move sequence to reposition the arm in vertical close position    
        if self.arm_position == 'vert_clos':
            return []
            
        elif self.arm_position == 'vert_open':
            return [self.vert_nue, self.hold_close]
            
        elif self.arm_position_dict[self.arm_position][1] != self.hold_open:
            move_seq = [[self.arm_position_dict[self.arm_position][0], self.hold_open]]
            move_seq.append([self.vert_nue, self.hold_open])
            move_seq.append([self.vert_nue, self.hold_close])
            return move_seq
        
        else:
            move_seq.append([self.vert_nue, self.hold_open])
            move_seq.append([self.vert_nue, self.hold_close])
            return move_seq
    
    
    def move_rep_neg_horz(self):
        # generates move sequence to reposition the arm in horizontal anti-clockwise close position
        if self.arm_position == 'horz_neg_clos':
            return []
        
        elif arm_position_dict[self.arm_position][1] != self.hold_open:
            move_seq = [[arm_position_dict[self.arm_position][0], self.hold_open]]
            move_seq.append([self.horz_neg, self.hold_open])
            move_seq.append([self.horz_neg, self.hold_close])
            return move_seq
            
        else:
            move_seq.append([self.horz_neg, self.hold_open])
            move_seq.append([self.horz_neg, self.hold_close])
            return move_seq
    
    def move_rep_pos_horz(self):
        # generates move sequence to reposition the arm in horizontal clockwise close position
        if self.arm_position == 'horz_pos_clos':
            return []
        
        elif arm_position_dict[self.arm_position][1] != self.hold_open:
            move_seq = [[arm_position_dict[self.arm_position][0], self.hold_open]]
            move_seq.append([self.horz_pos, self.hold_open])
            move_seq.append([self.horz_pos, self.hold_open])
            return move_seq
        
        else:
            move_seq.append([self.horz_pos, self.hold_open])
            move_seq.append([self.horz_pos, self.hold_close])
            return move_seq
    
    def move_rotate_clwise(self):
        # generates move sequence to rotate the arm 90 degrees in clockwise direction
        move_seq = []
        current_pos_str = self.get_current_position()
        current_pos = self.arm_position_dict[current_pos_str]
        
        if current_pos[0] == self.horz_pos:
            move_seq = self.move_rep_vert_close()
            move_seq.append([self.horz_pos, self.hold_close])
        
        elif current_pos[0] == self.vert_nue:
            move_seq = [self.horz_pos, self.hold_close]
        
        elif current_pos[0] == self.horz_neg:
            move_seq = [self.vert_nue, self.hold_close]
        return move_seq
    
    
    def move_rotate_ccwise(self):
        # generates move sequence to rotate the arm 90 degrees in anti-clockwise direction
        move_seq = []
        current_pos_str = self.get_current_position()
        current_pos = self.arm_position_dict[current_pos_str]
        
        if current_pos[0] == self.horz_neg:
            move_seq = self.move_rep_vert_close()
            move_seq.append([self.horz_neg, self.hold_close])
        
        elif current_pos[0] == self.vert_nue:
            move_seq = [self.horz_neg, self.hold_close]
        
        elif current_pos[0] == self.horz_pos:
            move_seq = [self.vert_nue, self.hold_close]
        return move_seq
        
    def move_rep_vert_open(self):
        # generates move sequence to reposition the arm in vertical open position
        if self.arm_position == 'vert_open':
            return []
            
        elif self.arm_position == 'vert_clos':
            return [self.vert_nue, self.hold_open]
            
        elif self.arm_position_dict[self.arm_position][1] != self.hold_open:
            move_seq = [[self.arm_position_dict[self.arm_position][0], self.hold_open]]
            move_seq.append([self.vert_nue, self.hold_open])
            return move_seq
        
        else:
            move_seq.append([self.vert_nue, self.hold_open])
            return move_seq        
        
    def set_position(self, p):
        # set position
        self.arm_position = p
        self.motor_rot.position = arm_position_dict[p][0]
        self.motor_hol.position = arm_position_dict[p][1]

# end class

class move:
    # defines arms and moves on arms
    left_arm = RobotArm('left')
    back_arm = RobotArm('back')
    right_arm = RobotArm('right')
    
    def __init__(self):    
        # orientation of cube w.r.t default position(white center on top). 
        # Positive value indicates rotation of the cube w.r.t and towards the camera view point
        # Negative value indicates a rotation of the cube w.r.t and away from the camera view point
        self.orientation = 0
    
    def rotate_cube(self, number_rotations):
        # generate move sequence to rotate the cube
        self.orientation += number_rotations
        if self.orientation > 0:
            self.orientation = (self.orientation % 4)
        else:
            self.orientation = (self.orientation % -4)
            
        if number_rotations > 0:
            for i in range(0, number_rotations):
                if self.left_arm.arm_position == 'horz_pos_clos' or self.left_arm.arm_position == 'horz_pos_open':
                    move_seq = self.left_arm.move_rep_vert_close()
                    move_input = move_struct() 
                    move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                    
                if self.right_arm.arm_position == 'horz_pos_clos' or self.right_arm.arm_position == 'horz_pos_open':
                    move_seq = self.right_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                    
                move_seq = self.back_arm.move_rep_vert_open()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input) 
                del move_input
                
                move_seq = self.right_arm.move_rotate_clwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                move_seq = self.left_arm.move_rotate_clwise()
                move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
                
                move_seq = self.back_arm.move_rep_vert_close()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input                
        
        elif number_rotations < 0:
            for i in range(0, -number_rotations):
                if self.left_arm.arm_position == 'horz_neg_clos' or self.left_arm.arm_position == 'horz_neg_open':
                    move_seq = self.left_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                    
                if self.right_arm.arm_position == 'horz_neg_clos' or self.right_arm.arm_position == 'horz_neg_open':
                    move_seq = self.right_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                
                move_seq = self.back_arm.move_rep_vert_open()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
                
                move_seq = self.right_arm.move_rotate_ccwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                move_seq = self.left_arm.move_rotate_ccwise()
                move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input

                move_seq = self.back_arm.move_rep_vert_close()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input 

        
        else:
            pass
    
    
    def rotate_right(self, no_of_rotations):
        # generate move sequence to rotate right face
        if self.back_arm.arm_position == 'horz_pos_clos' or self.back_arm.arm_position == 'horz_pos_open' or self.back_arm.arm_position == 'horz_neg_open' or self.back_arm.arm_position == 'horz_neg_clos':
            move_seq = self.back_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input        
        
        if no_of_rotations < 0:
            for i in range(0, -no_of_rotations):
                if self.right_arm.arm_position == 'horz_neg_clos' or self.right_arm.arm_position == 'horz_neg_open':
                    move_seq = self.right_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.right_arm.move_rotate_clwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
        elif no_of_rotations > 0:
            for i in range(0, no_of_rotations):
                if self.right_arm.arm_position == 'horz_pos_clos' or self.right_arm.arm_position == 'horz_pos_open':
                    move_seq = self.right_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.right_arm.move_rotate_ccwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
    
    
    def rotate_left(self, no_of_rotations):
        # generate move sequence to rotate left face
        if self.back_arm.arm_position == 'horz_pos_clos' or self.back_arm.arm_position == 'horz_pos_open' or self.back_arm.arm_position == 'horz_neg_open' or self.back_arm.arm_position == 'horz_neg_clos':
            move_seq = self.back_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input  
        
        if no_of_rotations > 0:
            for i in range(0, no_of_rotations):
                if self.left_arm.arm_position == 'horz_neg_clos' or self.left_arm.arm_position == 'horz_neg_open':
                    move_seq = self.left_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.left_arm.move_rotate_clwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
        elif no_of_rotations < 0:
            for i in range(0, -no_of_rotations):
                if self.left_arm.arm_position == 'horz_pos_clos' or self.left_arm.arm_position == 'horz_pos_open':
                    move_seq = self.left_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.left_arm.move_rotate_ccwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
    
    
    
    def rotate_back(self, no_of_rotations):
        # generate move sequence to rotate back face
        if self.left_arm.arm_position == 'horz_pos_clos' or self.left_arm.arm_position == 'horz_pos_open' or self.left_arm.arm_position == 'horz_neg_open' or self.left_arm.arm_position == 'horz_neg_clos':
            move_seq = self.left_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input
                    
        if self.right_arm.arm_position == 'horz_neg_clos' or self.right_arm.arm_position == 'horz_neg_open' or self.right_arm.arm_position == 'horz_pos_open' or self.right_arm.arm_position == 'horz_pos_clos':
            move_seq = self.right_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input
        
        if no_of_rotations < 0:
            for i in range(0, -no_of_rotations):
                if self.back_arm.arm_position == 'horz_neg_clos' or self.back_arm.arm_position == 'horz_neg_open':
                    move_seq = self.left_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.back_arm.move_rotate_clwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
        elif no_of_rotations > 0:
            for i in range(0, no_of_rotations):
                if self.back_arm.arm_position == 'horz_pos_clos' or self.back_arm.arm_position == 'horz_pos_open':
                    move_seq = self.back_arm.move_rep_vert_close()
                    move_input = move_struct()
                    move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                    self.execute_seq(move_input)
                    del move_input
                
                move_seq = self.back_arm.move_rotate_ccwise()
                move_input = move_struct()
                move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
                self.execute_seq(move_input)
                del move_input
                
    def rotate_down(self, no_of_rotations):
        # generate move sequence to rotate down face
        self.rotate_cube(1)
        self.rotate_back(no_of_rotations)
        
                
    def rotate_front(self, no_of_rotations):
        # generate move sequence to rotate front face
        self.rotate_cube(2)
        self.rotate_back(no_of_rotations)
    
    def rotate_top(self, no_of_rotations):
        # generate move sequence to rotate top face
        self.rotate_cube(-1)
        self.rotate_back(no_of_rotations)
    
    
    def execute(self, motor_postion_sequence):
        # execute move sequence send pwm
        servo_dict = {1 : servo.servo1, 2 : servo.servo2, 3 : servo.servo3, 4 : servo.servo4, 5 : servo.servo5, 6 : servo.servo6}
        
        for i in range(0, 20):
            servo.servo1.pulse(motor_postion_sequence[0])
            servo.servo2.pulse(motor_postion_sequence[1])
            servo.servo3.pulse(motor_postion_sequence[2])
            servo.servo4.pulse(motor_postion_sequence[3])
            servo.servo5.pulse(motor_postion_sequence[4])
            servo.servo6.pulse(motor_postion_sequence[5])
            time.sleep(0.02)
        
        #updating motor positions according to input
        self.left_arm.arm_position = self.left_arm.arm_position_lookup[(motor_postion_sequence[4], motor_postion_sequence[5])]
        self.back_arm.arm_position = self.back_arm.arm_position_lookup[(motor_postion_sequence[2], motor_postion_sequence[3])]
        self.right_arm.arm_position = self.right_arm.arm_position_lookup[(motor_postion_sequence[0], motor_postion_sequence[1])]
        
    
    def hold_cube(self):
        # hold cube in position
        left_position = self.left_arm.arm_position_dict[self.left_arm.arm_position]
        right_position = self.right_arm.arm_position_dict[self.right_arm.arm_position]
        back_position = self.back_arm.arm_position_dict[self.back_arm.arm_position]
        
        #send pulse on 6 channels
        servo.servo1.pulse(right_position[0])
        servo.servo2.pulse(right_position[1])
        servo.servo3.pulse(back_position[0])
        servo.servo4.pulse(back_position[1])
        servo.servo5.pulse(left_position[0])
        servo.servo6.pulse(left_position[1])
        time.sleep(0.01)
    
    
    def execute_seq(self, move_input):
        # execute move sequence
        if len(move_input.move_seq) != len(move_input.move_motors):
            raise Exception('execute_seq was not given input in proper format')
        else:
            #Finding maximum length of sequence
            max_length = 0
            for sequence in move_input.move_seq:
                if len(sequence) > max_length:
                    max_length = len(sequence)
            
            #pad move_seq to prolong
            for sequence in move_input.move_seq:
                if len(sequence) < max_length:
                    sequence.append(sequence[len(sequence) - 1]* (max_length - len(sequence)))
            #Now all move sequences have same length
            for i in range(0, len(move_input.move_seq[0])):
                motor_pos_seq = self.right_arm.get_current_motor_position() + self.back_arm.get_current_motor_position() + self.left_arm.get_current_motor_position()
                for j in range(0, len(move_input.move_motors)):
                    motor_pos_seq[move_input.move_motors[j][0] - 1] = move_input.move_seq[j][i][0]
                    motor_pos_seq[move_input.move_motors[j][1] - 1] = move_input.move_seq[j][i][1]
                self.execute(motor_pos_seq)
    
    def move_interpretor(self, move_string):
        # interpret move command
        down_orientation_dict = {-2 : -1, -1 : 2, 0 : 1, 2 : -1, 3 : 2}
        front_orientation_dict = {-3 : 1, -1 : -1, 0 :2, 1 : 1, 3 : -1}
        top_orientation_dict = {-3 : 2, -2 : 1, 0 : -1, 1 : 2, 2 : 1}
        
        if move_string[0] != 'R' and move_string[0] != 'L' and move_string[0] != 'B' and move_string[0] != 'D' and move_string[0] != 'F' and move_string[0] != 'U':
            raise Exception('Not a valid move face input')
        elif move_string[1] > 0 and move_string[1] < 4:
            if move_string[0] == 'R':
                self.rotate_right(move_string[1])
            elif move_string[0] == 'L':
                self.rotate_left(move_string[1])
            elif move_string[0] == 'B':
                if self.orientation == 0:
                    self.rotate_back(move_string[1])
                else:
                    self.rotate_cube(-self.orientation)
                    self.rotate_back(move_string[1])
            elif move_string[0] == 'D':
                if (self.orientation == 1) or (self.orientation == -3):
                    self.rotate_back(move_string[1])
                else:
                    self.rotate_cube(down_orientation_dict[self.orientation])
                    self.rotate_back(move_string[1])
            elif move_string[0] == 'F':
                if (self.orientation == 2) or (self.orientation == -2):
                    self.rotate_back(move_string[1])
                else:
                    self.rotate_cube(front_orientation_dict[self.orientation])
                    self.rotate_back(move_string[1])
            elif move_string[0] == 'U':
                if (self.orientation == 3) or (self.orientation == -1):
                    self.rotate_back(move_string[1])
                else:
                    self.rotate_cube(top_orientation_dict[self.orientation])
                    self.rotate_back(move_string[1])
        else:
            raise Exception('Not a valid range for nu,ber of rotations')
            
    def move_reposition_default(self):
        # move to default location - all arms to vertical close position
        if self.back_arm.arm_position != 'vert_clos':
            move_seq = self.back_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.back_arm.motor_rot.channel, self.back_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input
        
        if self.left_arm.arm_position != 'vert_clos':
            move_seq = self.left_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.left_arm.motor_rot.channel, self.left_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input
        
        if self.right_arm.arm_position != 'vert_clos':
            move_seq = self.right_arm.move_rep_vert_close()
            move_input = move_struct()
            move_input.add_seq_chan(move_seq, [self.right_arm.motor_rot.channel, self.right_arm.motor_hol.channel])
            self.execute_seq(move_input)
            del move_input
        
        

class move_struct:
    # structure to define move
    def __init__(self):
        self.move_seq = []          # list of move sequences
        self.move_motors = []        # list of motors
    
    def add_seq_chan(self, move_seq, channel):
        
        if isinstance(move_seq[0], list):
            self.move_seq.append(move_seq)
        else:
            self.move_seq.append([move_seq])
            
        self.move_motors.append(channel)
        
    def get_move_struct(self):
        return [self.move_seq, self.move_motors]


if __name__ == '__main__':
    # example usage
    Rubikssolve = move()
    
    # enable servo power rail -- needs battery for BB Blue
    servo.enable()

    # pass moves
    Rubikssolve.move_interpretor(['B', 1])
    Rubikssolve.move_interpretor(['D', 3])
    Rubikssolve.move_interpretor(['L', 1])
    
    # disable servo power rail
    servo.disable()