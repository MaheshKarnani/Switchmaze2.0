#Switchmaze2RIGHT, all servos on arduino, digital line comm
#2024May
#28
from __future__ import print_function
import serial
import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice
import os
import pandas as pd
import statistics as stats
import sys
from datetime import datetime
import numpy as np
import qwiic_rfid
import PyNAU7802
import smbus2

savepath="/home/raspberrypi/Documents/Data/"
#Choose "Animal" or "Test" below
#trial_type = "Test"
trial_type = "Animal"
print(trial_type)
if trial_type == "Test":
    subjects = ["335490249236"]
if trial_type == "Animal":  
    subjects = ["94331472" ,"x", "y"] #out of study,  ""

#general variables
light=10 #light limit for weight based sensing
heavy=40 #heavy limit for weight based sensing
scale_cal=13080150.000 #use a calibration code and 20g weight to find out
nest_timeout=300000 #nest choice timeout in ms
acquisition_end_timeout=10000 #scope timeout after return to nest
scale_interval_scan=500 #scan interval in ms when sensing
weighing_time=1000 #duration of weight aqcuisition in ms
safety_delay=2000 #ms delay to confirm putative maze exit

#timestamp miniscope frames
# frame_in_port=5#10 
# GPIO.setup(frame_in_port, GPIO.IN)
# LastFrameState=GPIO.input(frame_in_port)
# frame_counter=0

#trigger miniscope
# start_scope_port=9
# GPIO.setup(start_scope_port, GPIO.OUT)
# GPIO.output(start_scope_port,False)

#drink module
# water_reset_port=12
# GPIO.setup(water_reset_port, GPIO.OUT)
water = DigitalOutputDevice(24)
lick = DigitalInputDevice(25)
neopix = DigitalInputDevice(26)

if lick.value == 1:
    print("lick detected")
water.on()
time.sleep(0.02)
water.off()

water_duration=50 # in ms 50ms=10ul
water_flag=False
water_stop_dose_flag=False

#food module
food = DigitalOutputDevice(18)
eat = DigitalInputDevice(17)

#beams
#SEM
b0=DigitalInputDevice(22)
b1=DigitalInputDevice(23)
#start
b2=DigitalInputDevice(12) #proximity sensor operates in reverse!


#RFID
def scan_tag():
    my_RFID = qwiic_rfid.QwiicRFID(0x7D)
    if my_RFID.begin() == False:
        print("\nThe Qwiic RFID Reader isn't connected to the system. Please check your connection", file=sys.stderr)
        return
    tag = my_RFID.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    return tag
def clear_scanner():
    my_RFID = qwiic_rfid.QwiicRFID(0x7D)
    if my_RFID.begin() == False:
        print("\nThe Qwiic RFID Reader isn't connected to the system. Please check your connection", file=sys.stderr)
        return
    my_RFID.clear_tags()


#init scale
# Create the bus
bus = smbus2.SMBus(1)
# Create the scale and initialize it.. hardware defined address is 0x2A. mux required for multiple
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Scale connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()
# Calculate the zero offset
print("Calculating scale zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))
# print("Put a known mass on the scale.")
# cal = float(input("Mass in kg? "))
# # Calculate the calibration factor
# print("Calculating the calibration factor...")
# scale.calculateCalibrationFactor(cal)
# print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))
scale.setCalibrationFactor(scale_cal) #20g 12843262.500 30g 12902791.667 20g 12993162.500

#init flags
rec_licks_flag=False
drink_flag=False
# social_flag=False
# wheel_flag=False
# rec_wheel_flag=False
food_flag=False
# animal_found_flag=False
# sense_SEM_flag=False

#doors
d0=DigitalInputDevice(20)
d1=DigitalInputDevice(21)
#define functions
def open_door(d):
    if d==1:
        d0.on()
    if d==2:
        d1.on()

def close_door(d):
    if d==1:
        d0.off()
    if d==2:
        d1.off()
        
class SaveData:
    def append_weight(self,m,w,animaltag):

        weight_list = {
        "m": [],
        "w": [],
        "Date_Time": []
        }
        weight_list.update({'m': [m]})
        weight_list.update({'w': [w]})
        weight_list.update({'Date_Time': [datetime.now()]})
        
        df_w = pd.DataFrame(weight_list)
        #print(df_w)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_weight.csv"):
            df_w.to_csv(savepath + animaltag + "_weight.csv", encoding="utf-8-sig", index=False)
            #print("File created sucessfully")
        else:
            df_w.to_csv(savepath + animaltag + "_weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
            #print("File appended sucessfully")
        
    def append_event(self,amount_consumed,latency_to_consumption,event_type,animaltag):
        """
        Function used to save event parameters to a .csv file
        example use save.append_event("", "", "initialize", animaltag)
        """
        global event_list

        event_list = {
            "Date_Time": [],
            "amount_consumed": [],
            "latency_to_consumption": [],
            "Type" : [],   
        }
        amount_consumed=str(amount_consumed)
        latency_to_consumption=str(latency_to_consumption)
        
        event_list.update({'amount_consumed': [amount_consumed]})
        event_list.update({'latency_to_consumption': [latency_to_consumption]})
        event_list.update({'Type': [event_type]})
        event_list.update({'Date_Time': [datetime.now()]})

        df_e = pd.DataFrame(event_list)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_events.csv"):
            df_e.to_csv(savepath + animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

#initialize

print("beam check")   
print('sem safety')
print(b0.value)
print('exit')
print(b1.value)
print('centre')
print(b2.value)
food.on()
water.on()
time.sleep(0.05)
food.off()
water.off()
#serial to ard nano servos
ser = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(3)
close_door(1)
close_door(2)
close_door(3)
close_door(4)
input("turn servo power on and press enter")
open_door(4)
time.sleep(0.5)
open_door(3)
time.sleep(0.5)
open_door(2)
time.sleep(0.5)
open_door(1)
time.sleep(1)
close_door(1)
time.sleep(0.5)
close_door(2)
time.sleep(0.5)
close_door(3)
time.sleep(0.5)
close_door(4)
time.sleep(0.5)

save = SaveData()
for x in range(np.size(subjects)):
    animaltag=subjects[x]
    save.append_event("", "", "initialize", animaltag)
mode=0
generic_timer=int(round(time.time()*1000))
# frame_counter=0
# GPIO.output(start_scope_port,True) #start acquisition
#execution loop    
while True:
    #command loop changes door targets, records beams and controls rewards
    millis = int(round(time.time() * 1000))

    if mode==0: #SEM open for entry
        open_door(1)
        close_door(2)
        w=int(10)
        tag=0
        animal_found_flag=False
        mode=1
    if mode==1: 
        if millis-generic_timer>500 and not animal_found_flag:
            generic_timer=int(round(time.time()*1000))
            n=scale.getWeight() * 1000
            print("Mass {0:0.3f} g".format(n))
            tag=int(scan_tag())
            if tag>999:
                print(tag)
                if n>light and n<heavy and b0.value==1:
                    mode=2
                    close_door(1)
                    weight_aqcuisition_timer=int(round(time.time()*1000))
                    m=[] #mass measurement points
    if mode==2:     
        while int(round(time.time() * 1000))-weight_aqcuisition_timer<weighing_time:
            n=scale.getWeight() * 1000
            m.append(n)
        w=stats.mean(m)
        print(w)
        print(m)
        if w<light:
            mode=0
        if w>heavy:
            mode=0
        if w>light and w<heavy:
            save.append_weight(w,m,animaltag)                               
            mode=3
            print("m3")
            w=int(10)
    if mode==3: #SEM open to maze
        open_door(2)
        mode=4
        print("m4")
        maze_entry_flag=False #animal must change this flag to exit maze = enter at least one pod
        pod_entry_flag=False  #flag for detecting each beam break only once
        save.append_event("", "", "block_start", animaltag)
        
    if mode==4: #maze operational
        if not maze_entry_flag:
            if b2.value==0:
                save.append_event("", "", "start", animaltag)
                maze_entry_flag=True
                neopix.on() #water available signal
                print("in maze")
                food_flag=True
                TTL_timer=int(round(time.time() * 1000))          
        if maze_entry_flag and not pod_entry_flag:
            if eat.value==1:
                save.append_event("", "", "eat", animaltag)
                pod_entry_flag=True
                print("eat")
            if lick.value==1:
                save.append_event("", "", "drink", animaltag)
                drink_flag=True
                print("drink")
                drink_timer=int(round(time.time() * 1000))
                pod_entry_flag=True
#                 rec_licks_flag=True
            if b1.value==0:
                save.append_event("", "", "exit", animaltag)
                open_door(1)
                close_door(2)
                maze_entry_flag=False
                print("exit")
                mode=5
        elif b2.value==0:
            save.append_event("", "", "start", animaltag)
            pod_entry_flag=False
            food_flag=True
            TTL_timer=int(round(time.time() * 1000))
            print("start")
        
        if food_flag:
            food.on()
            if millis-TTL_timer>500:
                food.off()
                food_flag=False
        if drink_flag:
            water.on()
            if millis-drink_timer>water_duration:
                water.off()
                neopix.off() #water unavailable signal
                drink_flag=False
    
    if mode==5: #wait for exit
        if millis-generic_timer>500:
            generic_timer=int(round(time.time()*1000))
            n=scale.getWeight() * 1000
            print("Mass {0:0.3f} g".format(n))
            if n<light and b0.value==1:
                save.append_event("", "", "block_end", animaltag)
                mode=0
                close_door(1)
                clear_scanner()
                time.sleep(1)
                
#         if not GPIO.input(beaml[2]) and not pod_entry_flag: #enter unit1
#             pod_entry_flag=True
#             #print("unit1")
#             close_door(3)
#             open_door(4)
#             save.append_event("", "", "enter_explore", animaltag)
#             unit1_timer=int(round(time.time() * 1000))
#         if not GPIO.input(beaml[3]) and pod_entry_flag: #exit
#             pod_entry_flag=False
#             #print("ex1")
#             close_door(4)
#             open_door(3)
#             exploration_consumed = int(round(time.time() * 1000))-unit1_timer
#             save.append_event(exploration_consumed, "", "exit_explore", animaltag)
#         if not GPIO.input(beaml[4]) and not pod_entry_flag: #enter unit2
#             pod_entry_flag=True
#             #print("unit2")
#             close_door(5)
#             open_door(6)
#             save.append_event("", "", "enter_run", animaltag)
#             unit2_timer=int(round(time.time() * 1000))
#             rec_wheel_flag=True
#             limit=cycle
#             open_door(13) #running wheel 
#             wheel_timer=int(round(time.time() * 1000))
#             wheel_flag=True
#             save_flag=True
#             latency_to_run=[]  
#             counter=0
#         if rec_wheel_flag:
#             #record running wheel 
#             clkState=GPIO.input(wheel_in_port)
#             if clkState != clkLastState:
#                 counter += 1  
#                 clkLastState = clkState
#             if save_flag and counter>limit/4: #detect latency to run start at first quarter revolution
#                 latency_to_run = int(round(time.time() * 1000))-unit2_timer
#                 save_flag=False
#                 #print("run start")
#                 save.append_event("", "", "run", animaltag) 
#             if counter >= limit:
#                 #print(counter)    
#                 limit=counter+cycle
#         if wheel_flag and millis-wheel_timer>wheel_duration:
#             close_door(13)
#             wheel_flag=False
#         if not GPIO.input(beaml[5]) and pod_entry_flag: #exit
#             pod_entry_flag=False
#             #print("ex2")
#             close_door(6)
#             open_door(5)
#             rec_wheel_flag=False
#             wheel_flag=False
#             revs=counter/cycle
#             save.append_event(revs, latency_to_run, "exit_run", animaltag)
#         if not GPIO.input(beaml[6]) and not pod_entry_flag: #enter unit3
#             pod_entry_flag=True
#             #print("unit3")
#             close_door(7)
#             open_door(8)
#             food_timer=int(round(time.time() * 1000))
#             save.append_event("", "", "enter_feed", animaltag)
#             food_flag=True
#             GPIO.output(FED_in,False)
#             pellets=0
#             food_delay=[]
#         if food_flag and GPIO.input(FED_out): #rec delay to feed
#             save.append_event("", "", "retrieve_pellet", animaltag) 
#             food_delay=int(round(time.time() * 1000))-food_timer
#             #print("food delay was")
#             #print(food_delay)
#             food_flag=False
#             pellets=1
#         if not GPIO.input(beaml[7]) and pod_entry_flag: #exit
#             pod_entry_flag=False
#             #print("ex3")
#             close_door(8)
#             open_door(7)
#             save.append_event(pellets, food_delay, "exit_feed", animaltag)
#             GPIO.output(FED_in,True) #prep next pellet
#         if not GPIO.input(beaml[9]) and not pod_entry_flag: #enter unit4            
#             pod_entry_flag=True
#             #print("unit4")
#             close_door(9)
#             open_door(10)
#             open_door(14)#social
#             GPIO.output(water_reset_port,True)
#             save.append_event("", "", "enter_social", animaltag)
#             social_timer=int(round(time.time() * 1000))
#             social_flag=True
#             GPIO.output(water_reset_port,False)
#         if social_flag and millis-social_timer>social_duration:
#             close_door(14)#social
#             social_flag=False
#         if not GPIO.input(beaml[8]) and pod_entry_flag: #exit
#             pod_entry_flag=False
#             #print("ex4")
#             close_door(10)
#             open_door(9)
#             social_consumed=int(round(time.time() * 1000))-social_timer
#             save.append_event(social_consumed, "", "exit_social", animaltag)
#             social_flag=False
#         if not GPIO.input(beaml[10]) and not pod_entry_flag: #enter unit5
#             pod_entry_flag=True
#             #print("unit5")
#             close_door(11)
#             open_door(12)
#             save.append_event("", "", "enter_drink", animaltag)
#             lick_timer=int(round(time.time() * 1000))
#             rec_licks_flag=True
#             water_flag=True
#             water_stop_dose_flag=False
#             licks=0
#             drink_delay=[]
#         if rec_licks_flag:
#             #record licking
#             if GPIO.input(lick_in_port):
#                 licks=licks+1
#                 if water_flag:
#                     drink_delay=int(round(time.time() * 1000))-lick_timer
#                     save.append_event("", "", "drink", animaltag) 
#                     GPIO.output(lick_out_port,True) # start giving water
#                     water_dose_timer=int(round(time.time() * 1000))
#                     water_flag=False
#                     water_stop_dose_flag=True
#             if water_stop_dose_flag and millis-water_dose_timer>water_duration:
#                 GPIO.output(lick_out_port,False)
#                 water_stop_dose_flag=False
#                 #print("drink delay was")
#                 #print(drink_delay)                   
#         if not GPIO.input(beaml[11]) and pod_entry_flag: #exit
#             pod_entry_flag=False
#             #print("ex5")
#             close_door(12)
#             open_door(11)
#             rec_licks_flag=False
#             save.append_event(licks, drink_delay, "exit_drink", animaltag)
#         
#         if not GPIO.input(beaml[0]) and maze_entry_flag and not sense_SEM_flag: #putative leave maze
#             #print("putative return to SEM")
#             scale_timer=int(round(time.time() * 1000))
#             sense_SEM_flag=True
#         if sense_SEM_flag and millis-scale_timer>scale_interval_scan:
#             w = scale.getWeight() * 1000
#             #print("Mass is {0:0.3f} g".format(w))
#             scale_timer=int(round(time.time() * 1000))
#             if w>15: #definite leave maze
#                 close_door(2)
#                 open_door(1)
#                 save.append_event("", "", "block_end", animaltag)
#                 mode=5
#                 #print("m5")
#                 another_entered=False
#                 sense_SEM_flag=False
#                 exit_safety_timer_flag=True
#             if w<3 and GPIO.input(beaml[0]):
#                 sense_SEM_flag=False
# 
#     if mode==5: #wait for exit or entry of other
#         if millis-scale_timer>scale_interval_scan:
#             w = scale.getWeight() * 1000
#             #print("Mass is {0:0.3f} g".format(w))
#             scale_timer=int(round(time.time() * 1000))
#         if w<3 and GPIO.input(beaml[1]):
#             #print("putative exit")
#             if exit_safety_timer_flag:
#                 exit_safety_timer=int(round(time.time() * 1000))
#                 exit_safety_timer_flag=False
#             w = scale.getWeight() * 1000
#             if not exit_safety_timer_flag and w<3 and GPIO.input(beaml[1]) and millis-exit_safety_timer>safety_delay:
#                 close_door(1)
#                 nest_timer=int(round(time.time() * 1000))
#                 acquisition_end_timer=int(round(time.time() * 1000))
#                 mode=6
#                 #print("m6")
#         if w>heavy:
#             another_entered=True
#             #print("sub")
#         if another_entered and w<heavy and w>10 and GPIO.input(beaml[1]):
#             mode=1
#             #print("m1 sub")
#             w=int(10)
#             generic_timer=int(round(time.time() * 1000))
#             animal_found_flag=False
#     if mode==6: #wait for nest choice time out
#         if millis-acquisition_end_timer>acquisition_end_timeout:
#             GPIO.output(start_scope_port,False) #stop acquisition
#         if millis-nest_timer>nest_timeout:
#             for x in range(np.size(subjects)):
#                 animaltag=subjects[x]
#                 save.append_event("", "", "block_available", animaltag)
#             mode=0
#             #print("m0")
#      
#     #Frame rec loop records miniscope frame timestamps in behaviour time
#     if GPIO.input(frame_in_port) != LastFrameState: #rising or falling edge
#         frame_counter=frame_counter+1
#         save.append_event("", frame_counter, "frame", animaltag)
# #         print("frame")
# #         print(frame_counter)
#     LastFrameState=GPIO.input(frame_in_port)
#     
#     #troubleshoot loop time
# #     print(millis)
