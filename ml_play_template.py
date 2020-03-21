"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import numpy as np

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    previous = [75,400]
    now = [0,0]
    vector = [0,0]
    position = [0,0]
    last = [0,0]
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            ball_served = True
            for i in range(0):
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
        else:
            now=[scene_info.ball[0],scene_info.ball[1]]
            for i in range(2):
                vector[i] = now[i] - previous[i]
                
            for i in range(1):               
                if vector[1] >= 0 and vector[0] != scene_info.ball[0] :
                    #vector的向量異常大!!
                    #
                    position[0] = scene_info.ball[0]
                    position[1] = scene_info.ball[1]
                    

                    while position[1] < 399:
                        position[0] = position[0] + vector[0]
                        position[1] = position[1] + vector[1]

                    #需要用固定變數將結果存出
                    print(position,scene_info.frame)
                    #print(position,vector,scene_info.ball,scene_info.platform)
                    if position[0] < 0 :
                        position[0] = -position[0]
                    if position[0] > 200:
                        position[0]=400-position[0]
                    if last[0] != position[0] :
                        last[0] = position[0]
                        last[1] = position[1]
                    print(position,vector,scene_info.ball,scene_info.platform,last)
                    if last[0] > scene_info.platform[0]+20:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                    if last[0] < scene_info.platform[0]+20:
                        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)                
            previous = now
                        
            
