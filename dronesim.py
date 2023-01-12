import math
import time
import re
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil
from tkinter import filedialog
import os
from tkinter import *
import tkinter as tk

connection_string = "127.0.0.1:14550"
drone = connect(connection_string,wait_ready=True,timeout=100)




gndSpeed = 30
def keyButtonClicked():
    root.bind_all('<KeyPress>', key)
    key()
def manualControl(drone,vx,vy,vz):
    msg = drone.message_factory.set_position_target_local_ned_encode(
        0,
        0, 0,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b0000111111000111,  # -- BITMASK -> Consider only the velocities
        0, 0, 0,  # -- POSITION
        vx, vy, vz,  # -- VELOCITY
        0, 0, 0,  # -- ACCELERATIONS
        0, 0)
    drone.send_mavlink(msg)
    drone.flush()
def key(event):
    drone.mode = VehicleMode("GUIDED")

    if event.char == event.keysym:
        if event.keysym == 'r':
            print("RTL MODE IS ON ! ")
            drone.mode = VehicleMode("RTL")
            print("***RTL is succesfull***")
    else:
        if event.keysym == 'Up':
            print("move to up")
            manualControl(drone,gndSpeed,0,0)

        elif event.keysym == 'Down':
            print("move to down")
            manualControl(drone,-gndSpeed,0,0)
        elif event.keysym == 'Left':
            print("move to left")
            manualControl(drone,0,-gndSpeed,0)
        elif event.keysym == 'Right':
            print("move to right")
            manualControl(drone,0,gndSpeed,0)
    #drone.mode = VehicleMode("AUTO")
root = tk.Tk()
global cmd
root.geometry("1000x600")
#root.minsize(1000, 600)

# # set maximum window size value
#root.maxsize(1000, 600)
xVariable = tk.StringVar()
yVariable = tk.StringVar()
targetVariable = tk.StringVar()


def showTelemetry():
    positionText = drone.location.global_relative_frame
    attitudeText = drone.attitude
    velocityText = drone.velocity
    groundSpeedText = drone.groundspeed
    modeText = drone.mode.name
    velocityMs = math.sqrt(pow(velocityText[0],2) + pow(velocityText[1],2) + pow(velocityText[2],2))
    # print("Position: %s"%drone.location.global_relative_frame)
    # print('Attitude : %s'%drone.attitude)
    # print('Velocity: %s'%drone.velocity)
    # print('Groundspeed : %s'%drone.groundspeed)
    # print('Mode : %s'%drone.mode.name)
    speedLabel.config(text="Position : "+str(positionText) + "\n"+str(attitudeText)+"\nVelocity : "+str(velocityMs)+"m/s"+"\nGroundspeed : "+str(groundSpeedText)+ "\nMode : "+str(modeText),bg="blue")
    speedLabel.after(1000,showTelemetry)
def showSpeedUpdate():
    speedLabel.config(text="New Text")
def rtlSubmit():
    drone.mode = VehicleMode("RTL")
    print("***RTL is succesfull***")
    #cmd = drone.commands
    # cmd.clear()
    # time.sleep(1)
    # print("RTL Mode on!")
    # cmd.add(
    #     Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
    #             mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,
    #             0, 0,
    #             0,
    #             0, 0, 0, 0, 0))
    # cmd.upload()
    # cmd.next = 0
    # while True:
    #     nextWaypoint = cmd.next
    #
    #     print(f"Next command {nextWaypoint}")
    #     time.sleep(1)
    #
    #     if nextWaypoint == 3:
    #         print("***Mission completed***")
    #
    #         break
    #drone.mode = VehicleMode("AUTO")
def takeoff(newTarget):

    while drone.is_armable == False:
        print("Cant arm")
        time.sleep(1)
    print("Drone is ready for arm")
    if(drone.mode.name == "LAND" or drone.mode.name == "STABILIZE" or drone.mode.name == "AUTO"):
        drone.mode = VehicleMode("GUIDED")
        while (drone.mode == "GUIDED"):
            print("Switching GUIDED mode")
            time.sleep(1)
        print("Switched GUIDED mode")
        drone.armed = True
        while drone.armed == False:
            print("Waiting for arm")
            time.sleep(1)
        print("Arm is activated")


        drone.simple_takeoff(targetHeight)
        while drone.location.global_relative_frame.alt <= newTarget * 0.94:
            print("Current height :  {} ".format(drone.location.global_relative_frame.alt))
            time.sleep(0.5)
        print("Takeoff completed...")
        drone.mode = VehicleMode("AUTO")
# def takeOffButton():
#     takeoff(newTarget)
def submit():

    global newTarget
    global xCoordinate
    global yCoordinate
    global targetHeight
    targetHeight = targetVariable.get()
    xCoordinate = xVariable.get()
    yCoordinate = yVariable.get()
    if len(targetHeight) == 0 or len(xCoordinate) == 0 or len(yCoordinate) == 0:
        print("Please fill all blank")


    else:
        print("The xCoordinate is : " + xCoordinate)
        print("The yCoordinate is : " + yCoordinate)
        print("The takeoff height is : " + targetHeight)

        global newXCoordinate
        global newYCoordinate

        newXCoordinate = float(xCoordinate)
        newYCoordinate = float(yCoordinate)
        newTarget = int(targetHeight)
        takeoff(newTarget)
        # regex = "^Click:\s[-|+]\d+.?\d+\s\d+.?\d+\s\(([-|+]?[0-9]+°[0-9]+'[0-9]+\.[0-9]+\")\s([-|+]?[0-9]+°[0-9]+'[0-9]+\.[0-9]+\")\)\s\(.*\)\s+Distance:\s(\d+.?\d+)m\s.*$"
        # # regex kuulanarak parse işlemi yap , x ve y koordinatlarını çek
        # matches = re.findall(regex, xCoordinate)
        # print(matches)
        # regexCoordinate = matches[2]
        # yCoordinate = matches[3]
        addMission()
    # def openMap():
    #     os.system('/home/mirza/Desktop/startsimulation.sh')
    #     mapButton = Button(root,text="Open Map",command=openMap)
    #     mapButton.pack(pady=20)
    #     label = Label(root,text="")
    #     label.pack(pady=20)
    # openMap()
def emergencyLand():
    drone.mode = VehicleMode("LAND")
targetLabel = tk.Label(root, text='Target height', font=('calibre', 10, 'bold'))

targetEntry = tk.Entry(root, textvariable=targetVariable, font=('calibre', 10, 'normal'))

xLabel = tk.Label(root, text='X value', font=('calibre', 10, 'bold'))

xEntry = tk.Entry(root, textvariable=xVariable, font=('calibre', 10, 'normal'))

yLabel = tk.Label(root, text='Y value', font=('calibre', 10, 'bold'))

yEntry = tk.Entry(root, textvariable=yVariable, font=('calibre', 10, 'normal'))

submitButton = tk.Button(root, text='START MISSION', command=submit)
rtlButton = tk.Button(root, text='RTL', command=rtlSubmit)
emergencyStop = tk.Button(root, text = 'EMERGENCY LANDING',bg='red',command=emergencyLand)

manualButton = tk.Button(root,text = 'MANUAL CONTROL', command=keyButtonClicked)
autoButton = tk.Button(root,text = 'AUTO CONTROL', command=keyButtonClicked)
# openMapButton = tk.Button(root,text='Open Map',command=openMap)
targetLabel.grid(row=2, column=0)
targetEntry.grid(row=2,column=1)
xLabel.grid(row=0, column=0)
xEntry.grid(row=0, column=1)
yLabel.grid(row=1, column=0)
yEntry.grid(row=1, column=1)
submitButton.grid(row=3, column=1)
rtlButton.grid(row=4, column=1)
manualButton.grid(row=5,column=1)
speedLabel = Label(root,text="",font=("Helvetica",14))
speedLabel.grid(row=6,column=1)
emergencyStop.grid(row=7,column=1)
# openMapButton.grid(row=4,column=1)
showTelemetry()

def addMission():

    drone.mode = VehicleMode("AUTO")

    cmd = drone.commands
    cmd.clear()
    time.sleep(1)

    # TAKEOFF
    cmd.add(
        Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0,
                0, 0, 0, 0, newTarget))

    # WAYPOINT

    cmd.add(
        Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
                0,
                0, 0, newXCoordinate, newYCoordinate, newTarget))

    # cmd.add(
    #     Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
    #             0,
    #             0, 0, newXCoordinate, newYCoordinate, newTarget))
    # cmd.add(
    #     Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0,
    #             0,
    #             0, 0, newXCoordinate, newYCoordinate, newTarget))



    #RTL
    # cmd.add(
    #     Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,
    #             0, 0,
    #             0,
    #             0, 0, 0, 0, 0))
    # # verification
    # cmd.add(
    #     Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,
    #             0, 0,
    #             0,
    #             0, 0, 0, 0, 0))
    cmd.upload()
    print("Commands are loading...")
    cmd.next = 0
    #drone.mode = VehicleMode("AUTO")

    while True:
        nextWaypoint = cmd.next

        print(f"Next command {nextWaypoint}")
        time.sleep(1)

        break
        # if nextWaypoint == 1:
        #     print("***Mission completed***")
        #     cmd.clear()
        #     break


def gotoWithLocation():
    location = LocationGlobalRelative(-35.36279794 , 149.16515588 , 50)
    drone.simple_goto(location)


def velocity(velocityX,velocityY, yawRate, velocityZ, drone):
    msg = drone.message_factory.set_position_target_local_ned_encode(
        0,
        0,0,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
        0b0000011111000111,
        0,0,0,
        velocityX,velocityY,velocityZ,
        0,0,0,
        0,math.radians(yawRate))
    drone.send_mavlink(msg)
def position(positionX, positionY,yawRate,positionZ,drone):
    msg = drone.message_factory.set_position_target_local_ned_encode(
        0,
        0, 0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000011111111000, #bitmask explanation : the last tree 0 means allows positions and the others 1 mean shouldn allow velocities and acceleration
        # 0 -> allow read, 1 -> dont allow read
        positionX, positionY, positionZ,
        #positions
        0, 0, 0,
        #velocities
        0, 0, 0,
        #accelaration
        0, math.radians(yawRate))
    drone.send_mavlink(msg)


root.mainloop()
#addMission()

