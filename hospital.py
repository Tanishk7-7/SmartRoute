import json
with open("data/hospitals.json","r") as file:
    hospitals = json.load(file)

def  save_hospitals():
    with open("data/hospitals.json", "w") as file:
        json.dump(hospitals, file, indent=4)

def find_hospitals_by_specialzation(emergency_type):
    suitable = []
    for name , details in hospitals.items():
        if emergency_type in details["specializations"] and details["icu"]>0 and details["beds"]>0:
            suitable.append(name)
    
    return suitable
def add_hospital(name, location, specializations, beds, icu):
    hospitals[name] = {
        "location": location,
        "specializations": specializations,
        "beds": beds,
        "icu": icu
    }
    save_hospitals()
def edit_hospital(name, location, specializations, beds, icu):
    hospitals[name]["location"] = location
    hospitals[name]["specializations"] = specializations
    hospitals[name]["beds"] = beds
    hospitals[name]["icu"] = icu
    save_hospitals()

def remove_hospital(name):
    del hospitals[name]
    save_hospitals()
