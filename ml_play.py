"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import numpy as np
import pickle
from os import path
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn import metrics

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    
    def transformCommand(command):
        if 'RIGHT' in str(command):
            return 2
        elif 'LEFT' in str(command):
            return 1
        else:
            return 0
        pass


    def get_ArkanoidData(filename):
        Frames = []
        Balls = []
        Commands = []
        PlatformPos = []
        log = pickle.load((open(filename, 'rb')))
        for sceneInfo in log:
            Frames.append(sceneInfo.frame)
            Balls.append([sceneInfo.ball[0], sceneInfo.ball[1]])
            PlatformPos.append(sceneInfo.platform)
            Commands.append(transformCommand(sceneInfo.command))

        commands_ary = np.array([Commands])
        commands_ary = commands_ary.reshape((len(Commands), 1))
        frame_ary = np.array(Frames)
        frame_ary = frame_ary.reshape((len(Frames), 1))
        data = np.hstack((frame_ary, Balls, PlatformPos, commands_ary))
        return data

    
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
            
            
            
    
    def cut_ball(cut_dirc) :
        """
        0加速 1原路徑 2向右 3向左

        """
        if cut_dirc == 0 : #切球反方向
            if scene_info["ball_speed"][0] > 0:
                return 1
            else:
                return 2
        elif cut_dirc == 1:
            if scene_info["ball_speed"][0] > 0:
                return 2
            else:
                return 1
        elif cut_dirc == 2:
            return 1
        else:
            return 2
                    
    def pred_block_1P():
        
        if scene_info["ball_speed"][1] > 0 and scene_info["ball"][1] > 420 and scene_info["ball"][1] < 240 :
            x= ( scene_info["ball"][1]-scene_info["blocker"][1] + 180) // scene_info["ball_speed"][1] # 幾個frame以後會遇到block  # x means how many frames before catch the ball
            pred_nc = scene_info["ball"][0] + x * scene_info["ball_speed"][0]
            bound = pred_nc // 200
            block_pos = scene_info["blocker"][0]    
            bound_b = block_pos // 200
            print("xx")
            if bound > 0:
                if bound%2 == 0:
                    pred_nc = pred_nc - 200*bound
                else:
                    pred_nc = 200 - (pred_nc - 200*bound)
            else:
                if bound%2 ==1:
                    pred_nc = abs(pred_nc - (bound+1)*200)
                else:
                    pred_nc = pred_nc + (abs(bound)*200)
            
            if bound_b > 0:
                if bound_b%2 == 0:
                    block_pos = block_pos - 200*bound_b
                else:
                    block_pos = 200 - (block_pos - 200*bound_b)
            else:
                if bound_b%2 ==1:
                    block_pos = abs(block_pos - (bound_b+1)*200)
                else:
                    block_pos = block_pos + (abs(bound_b)*200)
            print("blcok ",block_pos," ball ",pred_nc)
            if (block_pos + 30 - pred_nc) < 35 and (block_pos + 30 - pred_nc) > -5:
                return 1
            else:
                return 0
    
    def block_speed(x,pre_x):
        vector_x = x - pre_x
        return vector_x
        
    
                    

    def ml_loop_for_1P():
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            
            x = ( scene_info["platform_1P"][1]-scene_info["ball"][1] ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)  # 預測最終位置 # pred means predict ball landing site 
            bound = pred // 200 # Determine if it is beyond the boundary
            if (bound > 0): # pred > 200 # fix landing position
                if (bound%2 == 0) : 
                    pred = pred - bound*200                    
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) : # pred < 0
                if (bound%2 == 1) :
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            if x<=2 and move_to( '1P' , pred) == 0:
               if (scene_info["blocker"][0] > 135 or scene_info["blocker"][0] < 35) and scene_info["frame"] < 1000:
                   return cut_ball(0)
               elif scene_info["frame"] > 1000:
                   return cut_ball(0)
            return move_to(player = '1P', pred = pred)
        else : # 球正在向上 # ball goes up
  #          pred = 
            return move_to(player = '1P',pred = 100)



    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0 : 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
            bound = pred // 200 
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            if x<=2 and move_to( '2P' , pred) == 0:
                if scene_info['platform_2P'][0] < 50 and scene_info['blocker'][0] > 150 :
                    return cut_ball(0)
                elif scene_info['platform_2P'][0] < 100 and scene_info['blocker'][0] > 100 :
                    return cut_ball(0)
                elif scene_info['platform_2P'][0] < 150 and scene_info['blocker'][0] > 75 :
                    return cut_ball(0)
                elif scene_info['platform_2P'][0] < 180 and scene_info['blocker'][0] > 80 :
                    return cut_ball(0)
                else:
                    return cut_ball(0)
                    
            else:
                return move_to(player = '2P',pred = pred)
    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        feature = []
        feature.append(scene_info["blocker"][0])
        feature.append(scene_info["ball"][0])
        feature.append(scene_info["ball"][1])
        feature.append(scene_info["ball_speed"][0])
        feature.append(scene_info["ball_speed"][1])
        print(feature)
        
        

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
