from tiger_bridge import TSPro

import signal

def move_finished_handler():
    print("\nmove finished!")

def received_position_handler(*arg: tuple[str]):
    position = float(arg[0])
    print(f"\nreceived a position: {position}")

def error_handler(*arg: tuple[str]):
    error_code = int(arg[0])
    print(f"received an error {error_code}")

def tool_down_handler():
    print("tool down")

def tool_up_handler():
    print("tool UP")

def get_setting_handler(*arg: tuple[str]):
    print("received setting:", arg)

def print_help():
    print("""
Here's a list of valid commands:
    - move_to {position}
    - stop
    - get_position
    - get_setting
    - home
    - calibrate {position}
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
        exit()
    elif command_id == "home":
        tsp.request_home()
    elif command_id == "calibrate":
        position = segments[1]

        try:
            position = float(position)
            tsp.request_calibrate(position)
        except ValueError:
            print_help()
            return
    elif command_id == "get_setting":
        setting_name = segments[1]
        tsp.request_setting(setting_name)
    else:
        print_help()
        return


def main():
    print("Welcome to the TigerBridge command-line interface example. Press Ctrl+C at any point to exit.")
    tsp = TSPro()

    while True:
        ip = input("Enter a TigerStop Pro's IP address: ")
        result = tsp.connect(ip)

        if not result:
            print("failed to connect")
            continue
        else:
            break

    tsp.set_event_hook(TSPro.EVENT_CODES.MOVE_FINISHED, move_finished_handler)
    tsp.set_event_hook(TSPro.EVENT_CODES.RECEIVED_POSITION, received_position_handler)
    tsp.set_event_hook(TSPro.EVENT_CODES.ERROR, error_handler)
    tsp.set_event_hook(TSPro.EVENT_CODES.TOOL_DISENGAGED, tool_up_handler)
    tsp.set_event_hook(TSPro.EVENT_CODES.TOOL_ENGAGED, tool_down_handler)

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
