from telethon.telegram_client import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import configparser
import csv
import time

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    print("[!] run python3 setup.py first !!\n")
    sys.exit(1)

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input('[+] Enter the code: '))

    chats = []
    last_date = None
    groups=[]

    result = await client(GetDialogsRequest(
                 offset_date=last_date,
                 offset_id=0,
                 offset_peer=InputPeerEmpty(),
                 limit=100,
                 hash = 0
             ))
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup== True:
                groups.append(chat)
        except:
            continue

    print('[+] Choose a group to scrape members:')
    i=0
    for g in groups:
        print('['+str(i)+']' + ' - ' + g.title)
        i+=1

    g_index = input("[+] Enter a Number : ")
    target_group=groups[int(g_index)]

    print('[+] Fetching Members...')
    time.sleep(1)
    all_participants = []
    participants = await client.get_participants(target_group, aggressive=True, limit=None)
    all_participants.extend(participants)

    while participants:
        participants = await client.get_participants(target_group, aggressive=True, limit=None, offset=len(all_participants))
        all_participants.extend(participants)
        time.sleep(1)

    print('[+] Saving In file...')
    time.sleep(1)
    with open("members.csv","w",encoding='UTF-8') as f:
        writer = csv.writer(f,delimiter=",",lineterminator="\n")
        writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
        for user in all_participants:
            if not user.bot:
                if user.username:
                    username= user.username
                else:
                    username= ""
                if user.first_name:
                    first_name= user.first_name
                else:
                    first_name= ""
                if user.last_name:
                    last_name= user.last_name
                else:
                    last_name= ""
                name= (first_name + ' ' + last_name).strip()
                writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])      

    print('[+] Members scraped successfully.')

with client:
    client.loop.run_until_complete(main())
