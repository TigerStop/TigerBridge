# TigerBridge

## Establishing Communication
In order to establish communication with the TigerStop Pro® controller (a.k.a. `the controller`), the client will connect via TCP/IP using the controller's IP address on port 7071. This IP address can be found in the controller's interface under the `My Machine` section of the settings, so long as it is connected via ethernet to a DHCP network. It's necessary that the client's computer is also connected to this same DHCP network for communication to function.
### Communication Structure
All messages are fundamentally ASCII strings. Data may have a type but should always be represented as a string when formatted into a message.
#### Sending Messages
Messages sent to the controller should begin with a string matching the requested function and end with a newline character `\n`.
Some functions will require additional parameters, which should be delimited by pipe `|` characters.

|Message|Identifier|Description|Sent Parameters|
|---|---|---|---|
|`stop`|	Requests| the positioner to stop moving	|None|
|`move_to`|	Requests| the positioner to move to the provided position value	|Position|
|`get_setting`|	Requests| a setting value from the controller	|Setting Name|
|`get_position`|	Requests| the current position of the positioner	|None|
|`calibrate`|	Sets| the positioner's position in relation to the tool	|Position|
|`home`|	Sends| the positioner to the far end of the beam (relative to the tool), allowing for a consistent reference point for positioning	|None|


#### Receiving Messages
Messages received from the controller will begin with a unique integer code that specifies the type of message and end in a newline character `\n`.
Certain messages will contain additional data, delimited by a pipe `|` character after the identifier code.
#### Message Codes
|Message Code|	Description|	Received Data|
|---|---|---|
|0	|Movement has finished	|None|
|1|	Received a setting from the controller	|Setting Name, Setting Value|
|2|	Received the current position of the positioner from the controller	|Position Value|
|3|	Received an error	|Error Code|
|4|	Tool has been engaged	|None|
|5|	Tool has been disengaged	|None|
|6|	Calibration succeeded	|None|

#### Error Codes
|Error Code|Description|
|---|---|
|101|	The requested destination is beyond the minimum limit of the machine|
|102|	The requested destination is beyond the maximum limit of the machine|
|103|	The positioner was unexpectedly halted during movement|
|104|	The positioner was unexpectedly moved while at rest|
|105|	The requested position value is not a valid number|
|106|	The requested command is unrecognized|
|107|	The requested setting is unavailable|
|108|	Unable to begin movement due to positioner already being in motion|
|109|	The machine is below the voltage threshold for standard operation|
|110|	The machine is above the voltage threshold for standard operation|
|111|	The temperature of the amplifier has exceeded safe operating threshold|
|112|	The temperature is increasing at an unsafe rate|
|113|	The electrical current through the machine has exceeded safe operating threshold|
|114|	The machine was signaled to stop while moving|
|115|	A movement was attempted while the tool was engaged|
|116|	The tool was engaged while the positioner was moving|
|117|	The requested calibration position is not a valid number|

## Functions
Areas of this section surrounded in quotes represent string literals, or sequences of bytes to be sent across a TCP connection. Sections of a string literal surrounded in curly braces represent the name of a value that will appear in that section. For example, for a message formatted by the string `2|{position}`, {position} could be a value of 50, and the message string would really be `2|50`. Additionally, `\n` in a string represents the newline character.
### Stop Function
This function causes the positioner to stop if moving. If the positioner is at rest, nothing should happen
#### Request
* Identifier: `stop`
* Parameters: None

#### Response
* Possible Error Codes
  * 114
### Move To Position Function
Basic movement of the positioner is accomplished through this function. The desired position is passed to the TigerStop in millimeters, which will cause the positioner to move to the provided position, if possible
#### Request
* Identifier: `move_to`
* Parameters: position
  * Type: float
  * Note: position values must be sent in metric millimeters
#### Response
* Message Code: 0
* Possible Error Codes
  * 101, 102, 103, 105, 108, 109, 110, 111, 112, 113, 114, 115, 116
### Get Setting Function
There are specific settings from the TigerStop, whose values can be read. The setting name determines which setting to get, and both name and value are sent back upon success.
#### Request
* Identifier: `get_setting`
* Parameters: Setting Name
* Available Settings:
  * `minlim`
    * The minimum limit of the machine (mm)
  * `maxlim`
    * The maximum limit of the machine (mm)
#### Response
* Message format: `1|{Setting Name}|{Setting Value}\n`
  * Message Code: 1
  * Setting Name: The name of the requested setting
  * Setting Value: The value of the requested setting
* Possible error codes
  *  107
### Get Position Function
Provides the current position of the positioner, relative to the tool, in millimeters.
#### Request
* Identifier: `get_position`
* Parameters: None
#### Response
* Message format: `2|{position}\n`
  * Message Code: 2
  * Position: The current position of the positioner (in millimeters)
    * Note: Position will be a float, but will be represented as a string in the response message
### Calibrate Function
Calibration specifies where the positioner is relative to the tool. The current position becomes the calibrated position, and the end limits are shifted by the difference between the calibrated position and the pre-calibrated position.
For example, say you have a minimum limit of 0, a maximum limit of 100, and a current position of 5. After calibrating to 0, your minimum limit will be -5, maximum limit will be 95, and current position will be 0.
#### Request
* Identifier: `calibrate`
* Parameters: position
  * Type: float
  * Note: position values must be sent in metric millimeters

#### Response
* Message format: `6\n`
  * Message Code: 6
* Possible Error Codes:
  * 117
### Home Routine Function
Sends the positioner to the far end of the beam (relative to the tool), allowing for a consistent reference point for positioning. The controller will respond with message code 0 four consecutive times during a successful home routine, with each one signaling a separate step of the routine. The fourth message in the series indicates a successfully completed routine. 
#### Request
* Identifier: `home`
* Parameters: None
#### Response
* Message format: `0\n`
  * Message Code: 0
* Possible Error Codes:
  * 103, 108, 109, 110, 111, 112, 113, 114, 115, 116
## Signals
Signals are messages that occur during certain operations of the TigerStop. These messages may occur independently of any function calls.
### Received Position Signal
This signal occurs during active movement of the TigerStop's positioner.
* Message Format: `2|{position}\n`
* Message Code: 2
### Tool Engaged Signal
This signal occurs when a tool connected  via a standard interconnect kit engages.
* Message Format: `4\n`
* Message Code: 4

### Tool Disengaged Signal
This signal occurs when a tool connected via a standard interconnect kit disengages.
* Message Format: `5\n`
* Message code: 5
