import json,time,importlib.util,sys
spec=importlib.util.spec_from_file_location("bn","bulba_names.py")
# reuse funcs by exec without argv loop
src=open("bulba_names.py").read().split("titles=sys.argv")[0]
ns={}; exec(src,ns)
titles=json.load(open("bulba_titles.json"))
extra=["Professor Sycamore","Serena (game)","Calem","Shauna","Tierno","Trevor (game)","Alexa","AZ","Emma (Looker)","Dexio","Sina","Grace","Blanche (Pokémon GO)"]
titles=sorted(set(titles)|set(extra))
res={}
for i in range(0,len(titles),50):
    try:
        for t,w in ns["wikitext"](titles[i:i+50]).items():
            n=ns["names"](w)
            res[t]={"es":n.get("European Spanish") or n.get("Spanish"),"ko":n.get("Korean"),"ja":n.get("Japanese")}
    except Exception as e: print("ERR",i,e,file=sys.stderr)
    time.sleep(0.4)
json.dump(res,open("bulba_map.json","w"),ensure_ascii=False,indent=0)
print(len(res),"pages;", sum(1 for v in res.values() if v["es"] and v["ko"]),"with both es+ko")
