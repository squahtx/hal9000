from chatbot import ChatBot
import config

chatbot = ChatBot()

import plugins.public
plugins.public.register(chatbot)

try:
	import plugins.private
	plugins.private.register(chatbot)
except ImportError as exception:
	chatbot.logger.log("ImportError: " + exception.msg)

chatbot.run(config)
