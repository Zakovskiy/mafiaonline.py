# simple mafia online bot
from zafiaonline.exceptions import ListenExampleErrorException
from zafiaonline.zafiaonline import Client
from zafiaonline.structures import PacketDataKeys

Mafia = Client()
Mafia.sign_in("email", "password")

Mafia.join_global_chat() # join in global chat

while 1:
	try:
		result = Mafia.listen()
	except ListenExampleErrorException as e:
		print("listen error", e)
		continue

	if result[PacketDataKeys.TYPE] == PacketDataKeys.MESSAGE: # if new message
		message = result[PacketDataKeys.MESSAGE]
		message_type = message[PacketDataKeys.MESSAGE_TYPE]

		if message_type == 1: # if message type "text"
			uu = message[PacketDataKeys.USER] # message user info
			content = message[PacketDataKeys.TEXT]

			print(content)

			user_id = uu[PacketDataKeys.OBJECT_ID]
			user_name = uu[PacketDataKeys.USERNAME]

			Mafia.send_message_global(content) # send message to global chat
