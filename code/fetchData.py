url = ("https://re.jrc.ec.europa.eu/api/seriescalc?lat="
     +lat+"&lon="+lon+"&startyear="+startyear+"&endyear="
     +endyear+"&peakpower="+str(solar/1000)+"&angle="+angle
     +"&loss="+loss+"&pvcalculation=1")
r = requests.get(url)

if r.status_code == 200:
    print("\nConnection Established!\nDownloading data...\n")
    os.system("curl \'"+url+"\' | tail -n+11 | head -n-11 >"+path+"/data/pv_production.csv")
    print("\nSaved data to file pv_production.csv")

else:
    sys.exit("\nConnection failed\nStatus Code: " + str(r.status_code))