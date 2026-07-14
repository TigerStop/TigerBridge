from tiger_bridge import TSPro

import signal
import sys
import os

def move_finished_handler():
    print("\nmove finished!")

def received_position_handler(*args):
    position = float(args[0])
    print(f"\nreceived a position: {position}")

def error_handler(*args):
    error_code = int(args[0])
    print(f"received an error {TSPro.ERROR_CODES(error_code).name}")

def tool_engaged_handler():
    print("tool down")

def tool_disengaged_handler():
    print("tool UP")

def get_setting_handler(*args):
    print("received setting data:", args)

def edge_detect_sensor_activated_handler():
    print("edge detect sensor activated")

def edge_detect_sensor_deactivated_handler():
    print("edge detect sensor deactivated")

def defect_sensor_activated_handler():
    print("defect sensor activated")

def disconnection_handler():
    print("socket connection lost. exiting...")
    os._exit(1)

def clamps_engaged_handler():
    print("clamps engaged")

def tool_enabled_handler():
    print("tool enabled")

def tool_left_rest_handler():
    print("tool left rest position")

def tool_extended_handler():
    print("tool at extension")

def tool_left_extension_handler():
    print("tool left extended position")

def tool_at_rest_handler():
    print("tool reached rest position")

def clamps_disengaged_handler():
    print("clamps disengaged")

def tool_cycle_completed_handler():
    print("tool cycle completed")

def tool_motor_enabled_handler():
    print("tool motor enabled")

def print_help():
    print("""
Here's a list of valid commands:
    - move_to {position}
    - stop
    - get_position
    - get_setting
    - home
    - calibrate {position}
    - cycle_tool
    """)

def parse_command(tsp: TSPro, command: str):
    segments = command.split(" ")
    command_id = segments[0]

    if command_id == "move_to":
        position = segments[1]

        try:
            position = float(position)
            tsp.request_move_to_position(position)
        except ValueError:
            print_help()
            return
    elif command_id == "stop":
        tsp.request_stop()
    elif command_id == "get_position":
        tsp.request_current_position()
    elif command_id == "exit":
        os._exit(1)
    elif command_id == "home":
        tsp.request_home()
    elif command_id == "calibrate":
        if len(segments) < 2:
            print("no position value provided")
            return
        
        position = segments[1]

        try:
            position = float(position)
            tsp.request_calibrate(position)
        except ValueError:
            print_help()
            return
    elif command_id == "get_setting":
        if len(segments) < 2:
            print("no setting name provided")
            return
        
        setting_name = segments[1]
        tsp.request_setting(setting_name)
    elif command_id == "cycle_tool":
        tsp.request_cycle_tool()
    else:
        print_help()
        return


def main():
    print("Welcome to the TigerBridge command-line interface example. Press Ctrl+C at any point to exit.")
    tsp = TSPro()
    ip = ""

    if len(sys.argv) >= 2:
        ip = sys.argv[1] 
    else:
        ip = input("Enter a TigerStop Pro's IP address: ")
        
    while True:    
        result = tsp.connect(ip)

        if not result:
            print("failed to connect")
            ip = input("Enter a TigerStop Pro's IP address: ")
            continue
        else:
            break

    tsp.set_event_hook(TSPro.MESSAGE_CODES.MOVE_FINISHED, move_finished_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.RECEIVED_POSITION, received_position_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.ERROR, error_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.SIK_TOOL_DISENGAGED, tool_disengaged_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.SIK_TOOL_ENGAGED, tool_engaged_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.EDGE_DETECT_SENSOR_ACTIVATED, edge_detect_sensor_activated_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.EDGE_DETECT_SENSOR_DEACTIVATED, edge_detect_sensor_deactivated_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.DEFECT_SENSOR_ACTIVATED, defect_sensor_activated_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.DISCONNECTED, disconnection_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.CLAMPS_ENGAGED, clamps_engaged_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_ENABLED, tool_enabled_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_LEFT_REST, tool_left_rest_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_EXTENDED, tool_extended_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_LEFT_EXTENSION, tool_left_extension_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_AT_REST, tool_at_rest_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.CLAMPS_DISENGAGED, clamps_disengaged_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_CYCLE_COMPLETED, tool_cycle_completed_handler)
    tsp.set_event_hook(TSPro.MESSAGE_CODES.TOOL_MOTOR_ENABLED, tool_motor_enabled_handler)

    while True:
        parse_command(tsp, input("Enter a command: "))

if __name__ == "__main__":
    # set the SIGINT handler back to the kernel default
    # python by default changes this, which breaks CTRL + C input
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        main()
    except KeyboardInterrupt:
        exit()
