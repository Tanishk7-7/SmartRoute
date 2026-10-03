hospitals = {
    "City Care": {
        "location": "B",
        "specializations": ["Cardiology", "Emergency"],
        "beds": 5,
        "icu": 2
    },

    "Metro Hospital": {
        "location": "C",
        "specializations": ["Trauma", "Emergency"],
        "beds": 8,
        "icu": 3
    },

    "LifeLine Hospital": {
        "location": "D",
        "specializations": ["Cardiology", "Trauma", "Emergency"],
        "beds": 12,
        "icu": 4
    }
}
def find_hospitals_by_specialzation(emergency_type):
    suitable = []
    for name , details in hospitals.items():
        if emergency_type in details["specializations"] and details["icu"]>0 and details["beds"]>0:
            suitable.append(name)
    
    return suitable

#print(find_hospitals_by_specialzation("Cardiology"))