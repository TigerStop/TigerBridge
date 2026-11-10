
# TigerBridge UI Overview

## Bridge Screen

<img width="1277" height="796" alt="bridge_sample_main" src="https://github.com/user-attachments/assets/1293409b-9ee5-4a40-a270-d2071f8fa593" />

### Top Bar:
 - **Tiger Eye**
	- On press, exits TigerBridge and returns back to the TigerStop Pro application
	- Any active connections will be dropped when exiting

- **Settings Cog**
	- On press, toggles an overlay with additional options
	- See *Settings Overlay* section for specifics
	> **NOTE**: The STOP button is still accessible while the overlay is active
	
- **Sun Icon**
	- On press, toggles light/dark mode

### Main Area:

- **STOP Button**
	- On touch, stops all motion and ends any tool cycles, if applicable
- **Connection Status**
	- Indicates whether TigerBridge has an active external connection
	- Options are
		- `Not Connected`
		- `Connected`
- **IP Address**
	- Displays the address used for external devices to connect to TigerBridge
    - When no IP address is found, the next `No IP` will be displayed
	
## Settings Overlay

<img width="1277" height="797" alt="bridge_sample_overlay" src="https://github.com/user-attachments/assets/6ab31f8d-657e-49c0-bfb0-47d12dfe672b" />

- **Version**
	- Current version of TigerBridge
- **Update**
	- On press, attempts to update TigerBridge via USB
	- A USB drive must be plugged into the Controller, with the TigerBridge.tar.gz file on said USB
		- If no USB is detected, the *UPDATE* text will flash red
> USB drives should be formatted as FAT32
	
- **Pull Logs**
	- On press, attempts to pull TigerBridge log files onto the USB
		- If no USB is detected, the *PULL LOGS* text will flash red
	- Log files will be stored under the `TigerLogs` directory on the root of the USB
	- Naming follows `{SERIAL#}_Bridge` format to differentiate from TigerStop Pro logs
		- e.x. if the machine's serial number is `123456789`, the TigerBridge log folder will be `123456789_Bridge`
> USB drives should be formatted as FAT32
- **Launch On Startup**
	- Toggles whether the Controller starts on TigerStop Pro, or TigerBridge when powered on
	- If the radio button is filled, startup on TigerBridge
	- If the radio button is empty, startup on TigerStop Pro








