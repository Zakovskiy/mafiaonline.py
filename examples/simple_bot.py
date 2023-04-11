# /Zakovskiy/mafiaonline.py/
# simple mafia online bot
from mafiaonline.mafiaonline import Client

Mafia = Client()
Mafia.sign_in("email", "password")

Mafia.join_global_chat() # join in global chat

while 1:
	try:
		result = Mafia.listen()
	except:
		continue

	if (result["ty"] == "m"): # if new message
		m = result["m"]
		message_type = m["t"]

		if (message_type == 1): # if message type "text"
			uu = m["uu"] # message user info 
			content = m["tx"]

			print(content)

			user_id = uu["o"]
			user_name = uu["u"]

			Mafia.send_message_global(content) # send message to global chat
