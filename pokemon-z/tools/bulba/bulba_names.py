import json,re,sys,urllib.parse,urllib.request,time
API="https://bulbapedia.bulbagarden.net/w/api.php"
def wikitext(titles):
    q=urllib.parse.urlencode({"action":"query","titles":"|".join(titles),"prop":"revisions",
        "rvprop":"content","rvslots":"main","format":"json","redirects":"1"})
    r=urllib.request.Request(API+"?"+q,headers={"User-Agent":"name-research/1.0"})
    d=json.load(urllib.request.urlopen(r,timeout=60))
    out={}
    for p in d["query"]["pages"].values():
        if "revisions" in p: out[p["title"]]=p["revisions"][0]["slots"]["main"]["*"]
    return out
def names(w):
    i=w.find("==Names==")
    if i<0: return {}
    tbl=w[i:w.find("|}",i)]
    rows=tbl.split("|-")
    res={}
    for r in rows:
        cells=[c.strip() for c in re.split(r"\n\s*\|",r)[1:] if c.strip()]
        if len(cells)<2: continue
        langs=re.sub(r"<br\s*/?>"," ",cells[0])
        nm=re.sub(r"''.*?''","",cells[1]).strip()
        for L in [x.strip() for x in langs.split(",")]:
            if L: res.setdefault(L,nm)
    return res
titles=sys.argv[1:]
for i in range(0,len(titles),20):
    for t,w in wikitext(titles[i:i+20]).items():
        n=names(w)
        es=n.get("European Spanish") or n.get("Spanish")
        print(f"{t}\tES={es}\tKO={n.get('Korean')}\tJA={n.get('Japanese')}")
    time.sleep(1)
