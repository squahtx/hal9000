import sys

config = sys.modules[__name__]

services = {}
services["discord"] = {
	"enabled": False,
	"type": "discord",
	"token": "a0a0a0a0a0a0a0a0a0a0a0a0.a0a_0a.0a0a0a0a0a0a0a0a0a0a0a0a0a0"
}

services["slack"] = {
	"enabled": True,
	"type": "slack",
	"token": "aaaa-99999999999-aaaaaaaaaaaaaaaaaaaaaaaa"
}

plugins = {}
plugins["nethack"] = {
	"chatService": "slack",
	"server": "150795408866541569",
	"channelName": "#nethack"
}

# logging = {
# 	"destinations": [
# 		{
# 			"chatService": "discord",
# 			"server": "999999999999999999",
# 			"channelName": "robot-wars"
# 		}
# 	]
# }
