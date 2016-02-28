from .help            import Help
from .management      import Management
from .ping            import Ping
from .unicode         import Unicode

from .podbaydoors     import PodBayDoors
from .cowsay          import CowSay
from .nethack         import NetHack
from .steamlocomotive import SteamLocomotive

def register(chatbot):
	chatbot.addPlugin(Help)
	chatbot.addPlugin(Management)
	chatbot.addPlugin(Ping)
	chatbot.addPlugin(Unicode)
	
	chatbot.addPlugin(CowSay)
	chatbot.addPlugin(PodBayDoors)
	chatbot.addPlugin(NetHack)
	chatbot.addPlugin(SteamLocomotive)
