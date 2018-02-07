# -*- coding: utf-8 -*-
"""
--------------------------------------------------------------------------
Rubik's Cube Solver Demo
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

See README for setup / run instructions

"""
import time
import queue
import threading
import multiprocessing

import rcpy.button as button

import cube_solver.solver as sv
import image_processing.read_rubiks_cube as img
import motor_driver.ServoControl as mot

# Twitter api
import twitter
# Image Processing
from PIL import Image, ImageDraw, ImageFont


#-----------------------------------------------------------------------------
# Global Variables
#-----------------------------------------------------------------------------
stop_flag = False

#-----------------------------------------------------------------------------
# Class Definitions
#-----------------------------------------------------------------------------
class MotorThread(threading.Thread):
    q            = None
    timeout      = None
    done         = None
    motors       = None
    stop_event   = None
    func_options = None
    
    def __init__(self, loop_time = 1.0/60):
        self.q            = queue.Queue()
        self.timeout      = loop_time
        self.done         = False
        self.motors       = mot.move()
        self.stop_event   = threading.Event()
        self.func_options = {'rotate_cube'     : self.rotate_cube,
                             'default_position': self.default_position,
                             'rotate_back'     : self.rotate_back,
                             'move_interpretor': self.move_interpretor
                            }
        
        self.stop_event.clear()
        
        super(MotorThread, self).__init__()

    def onThread(self, function, *args, **kwargs):
        self.done = False
        self.q.put((function, args, kwargs))
        while not self.done:
            time.sleep(0.02)

    def run(self):
        while not self.stop_event.is_set():
            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function_name = self.func_options[function]
                function_name(*args, **kwargs)
                self.done = True
            except queue.Empty:
                self.idle()

    def idle(self):
        # Call the grip function
        self.motors.hold_cube()

    def rotate_cube(self, number):
        self.motors.rotate_cube(number)

    def default_position(self):
        self.motors.move_reposition_default()

    def rotate_back(self, number):
        self.motors.rotate_back(number)

    def move_interpretor(self, move):
        self.motors.move_interpretor(move)

    def stop_thread(self):
        self.stop_event.set()
        
# End Class

class SolveThread(threading.Thread):
    timeout      = None
    done         = None
    stop_event   = None
    
    def __init__(self, loop_time = 1.0/60):
        self.timeout      = loop_time
        self.done         = False
        self.stop_event   = threading.Event()

        self.stop_event.clear()
        
        super(SolveThread, self).__init__()

    def run(self):
        while not self.stop_event.is_set():
            global stop_flag
            stop_flag = False
            start_solve()
            self.done = True

    def stop_thread(self):
        self.stop_event.set()
        print('in the stop function\n')
        global stop_flag
        stop_flag = True
        
# End Class



#-----------------------------------------------------------------------------
# Function Definitions
#-----------------------------------------------------------------------------
def init_cube(camera, motors, debug=False, verbose=False):
    cube   = None
    repeat = True

    if (verbose):
        print("Initialize Cube")

    while repeat:
        cube = img.Cube()
        
        # Move sequence to cover all faces
        if (verbose):
            cube.print_cube()
        
        # Step 1
        if not stop_flag:    
            motors.onThread("default_position")
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
    
        # Step 2
        if not stop_flag:    
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
    
        # Step 3
        if not stop_flag:    
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        # Step 4
        if not stop_flag:
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
    
            # Infer centers of the sides at this point
            cube.infer_side_centers()
    
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
            
        # Step 5
        if not stop_flag:
            motors.onThread("rotate_back", 1)
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube_face(img.BACK, img.CLOCKWISE)
            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        # Step 6
        if not stop_flag:    
            motors.onThread("rotate_cube", 1)
            motors.onThread("rotate_back", 3)  # Should be -1
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube(img.ROTATE_FORWARD)
            cube.rotate_cube_face(img.BACK, img.COUNTER_CLOCKWISE)
            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        # Step 7
        if not stop_flag:    
            motors.onThread("rotate_back", 3)  # Should be -1
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube_face(img.BACK, img.COUNTER_CLOCKWISE)
            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        # Step 8
        if not stop_flag:    
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        # Step 9
        if not stop_flag:    
            motors.onThread("rotate_back", 1)
            motors.onThread("rotate_cube", 1)
            motors.onThread("default_position")

            cube.rotate_cube_face(img.BACK, img.CLOCKWISE)
            cube.rotate_cube(img.ROTATE_FORWARD)
            img.init_face(cube, camera, debug, verbose)
        
            # Infer last tile
            cube.infer_last_tile()
        
            if (verbose):
                cube.print_cube()
            
            if (debug):
                pause()
        else:
            repeat = False
        
        if not stop_flag:
            if cube.verify_cube():
                repeat = False
            else:
                # Pause to reset cube
                pause()
        else:
            repeat = False
        
            
    # End while
    if not stop_flag:    
        # Create cube output string
        output = cube.create_string()
        cube.image_cube()
        
        if (verbose):
            print("Cube String:  {0}".format(output))
    else:
        output = None
    # Release camera
    camera.release()            
    
    return output
# End def



def pause():
    # Wait for key proess
    try:
        input("Press Enter to continue...")
    except:
        pass
    
# End def


def usage(exit_level=None):
    import sys
    
    print("Usage:  solve_rubiks_cube.py [hdv]")
    
    if exit_level is not None:
        sys.exit(exit_level)


#End def

def start_solve():
    
    quit = False
    # start execution of scan and solve
    while not quit:
        if (button.mode.is_pressed()):
            print("STARTING SOLVER")
            
            start_time   = time.time()
            
            camera       = cv2.VideoCapture(0)
            motor_thread = MotorThread()
            
    
            # Enable the servo motors
            rcpy.servo.enable()

            # Start motor thread
            motor_thread.start()

            # Enable the servo motors
            rcpy.servo.enable()

            # Initialize the cube    
            if not stop_flag:
                cube_str = init_cube(camera, motor_thread, debug, verbose)
            else:
                quit = True

            #if (verbose):
            #rprint("Cube String: {0}".format(cube_str))
    
            # Get the solver moves
            if not stop_flag:   
                solver_moves = sv.solve(cube_str, 20, 2)
            else:
                quit = True
    
            # Stop motor thread
            motor_thread.stop_thread()
    
            im = Image.open("pil_text_font.png")
            fnt = ImageFont.truetype('/usr/share/fonts/Helvetica-Regular.ttf', 20)
            d = ImageDraw.Draw(im)
            d.text((100, 600), solver_moves, font=fnt, fill=(0, 0, 0))
            im.save('pil_text_font.png')
            if not stop_flag:
                solver_split = solver_moves.split()
                solver_split = solver_split[0 : (len(solver_split) - 1)]
                print(solver_split)
            else:
                quit = True
    
            if not stop_flag:
                if (verbose):
                    print("Sovlver Moves: {0}".format(solver_moves))
            else:
                quit = True
    
            # Execute the solver moves
            if not stop_flag:    
                Rubikssolve = mot.move()
            else:
                quit = True
    
            if not stop_flag:
                move_prev = 'F'
                for (move) in solver_split:
                   if not stop_flag:
                        print([move[0], int(move[1])])
                        if move[0] == 'L':
                            if move_prev == 'R':
                                Rubikssolve.rotate_back(1)
                                Rubikssolve.rotate_back(3)
                        Rubikssolve.move_interpretor([move[0], int(move[1])])
                        if move[0] == 'L':
                            Rubikssolve.rotate_back(1)
                            Rubikssolve.rotate_back(3)
                        move_prev = move[0]
                   else:
                       quit = True
            else:
                quit = True
                    
            if not stop_flag:    
                # Return arms to original position
                Rubikssolve.move_reposition_default()
                
                api = twitter.Api(consumer_key='consumer key',
                      consumer_secret='consumer secret',
                      access_token_key='access token',
                      access_token_secret='access token secret')
                #status = api.PostUpdate("I solved a Rubiks cube in " + str(len(solver_split)) + " moves and I took {:3.2f}  seconds to do it!".format(time.time() - start_time))
                status = api.PostMedia("I solved a Rubiks cube in " + str(len(solver_split)) + " moves and I took {:3.2f}  seconds to do it!".format(time.time() - start_time), 'pil_text_font.png', possibly_sensitive=None, in_reply_to_status_id=None, latitude=None, longitude=None, place_id=None, display_coordinates=False)
            else:
                quit = True
            # Disable servo motors
            rcpy.servo.disable()


#-----------------------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    import getopt
    import cv2
    import rcpy

    debug      = False
    verbose    = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "hdv", 
                                   ["help", "debug", "verbose"])
    except getopt.GetoptError:
        usage(exit_level=2)
 
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(exit_level=0)
        elif opt in ("-d", "--debug"):
            debug      = True
        elif opt in ("-v", "--verbose"):
            verbose    = True

    t_solve = SolveThread()
    t_solve.start()
    
    while True:
        if button.pause.pressed():
            print('Pause button asserted\n')
            t_solve.stop_thread()
            t_solve.join()
            t_solve = SolveThread()
            t_solve.start()
            time.sleep(2)