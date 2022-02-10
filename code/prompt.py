path = "/home/manousos/myfiles/thesis"
places = {
    1: (35.512, 24.012),
    2: (35.364, 24.471),
    3: (35.343, 25.153),
    4: (35.185, 25.706),
    5: (35.050, 24.877)
}


print("Select pre-defined place from the list below (1-5) "
      +"or press 6 to provide custom coordinates:")

choice = int(input("[1] Chania\n[2] Rethymno\n"
                   +"[3] Heraklio\n[4] Ag.Nikolaos\n"
                   +"[5] Moires\n[6] Custom\n"))

while choice > 6 or choice < 1:
    print("\nInvalid answer. Please choose one of the below:")
    choice = int(input("[1] Chania\n[2] Rethymno\n"
                       +"[3] Heraklio\n[4] Ag.Nikolaos\n"
                       +"[5] Moires\n[6] Custom\n"))


if choice == 6:
    lat = input("Latitude of area: ")
    while float(lat) < -90.0 or float(lat) > 90.0 :
        print("Invalid range for latitude...")
        lat = input("Please provide valid input (-90, 90): ")

    lon = input("Longitude of area: ")
    while float(lon) < -180.0 or float(lon) > 180.0 :
        print("Invalid range for longitude...")
        lat = input("Please provide valid input (-180, 180): ")
else:
    lat = str(places[choice][0])
    lon = str(places[choice][1])


solar = int(input("\nTotal installed solar power in the area (kWp): "))
while solar <= 0:
    print("Installed kWp cannot be below zero...")
    solar = int(input("Please provide valid input (kWp): "))


print("\nChoose project duration:")
dur = int(input("[1] Day\n[2] Year\n"))

while dur > 2 or choice < 1:
    print("\nInvalid answer. Please choose one of the below:")
    dur = int(input("[1] Day\n[2] Year\n"))
