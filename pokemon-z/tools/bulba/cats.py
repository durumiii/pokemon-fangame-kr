import json,urllib.parse,urllib.request,time
API="https://bulbapedia.bulbagarden.net/w/api.php"
def cat(c):
    out=[];cont=None
    while True:
        p={"action":"query","list":"categorymembers","cmtitle":"Category:"+c,"cmlimit":"500","format":"json","cmnamespace":"0"}
        if cont:p["cmcontinue"]=cont
        r=urllib.request.Request(API+"?"+urllib.parse.urlencode(p),headers={"User-Agent":"name-research/1.0"})
        d=json.load(urllib.request.urlopen(r,timeout=60))
        out+=[m["title"] for m in d["query"]["categorymembers"]]
        cont=d.get("continue",{}).get("cmcontinue")
        if not cont:break
    return out
names=set()
for c in ["Gym Leaders","Elite Four members","Champions","Pokémon Professors","Team Flare","Kalos characters","Characters with a Mega Stone","Rivals"]:
    try:
        m=cat(c); print(c,len(m)); names|=set(m)
    except Exception as e: print(c,"ERR",e)
    time.sleep(0.5)
json.dump(sorted(names),open("bulba_titles.json","w"))
print("total",len(names))
