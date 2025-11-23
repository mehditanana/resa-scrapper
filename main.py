### TODO : REFACTORING GENERAL DU CODE
### TODO : AJOUTER DES COMMENTS
### TODO : AJOUTER UN README / UNE DOCUMENTATION

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
import os
import sys
import time

SALLES_SOLO = ["e.090", "e.008", "e.092"]
SALLES_GROUPES = ["e.010", "e.012", "e.091"]

def unpack_time_slot(timeslot):
    start_str, end_str = timeslot.split("-")
    sh, sm = map(int, start_str.split(":"))
    eh, em = map(int, end_str.split(":"))
    return (sh, sm), (eh, em)

def is_timeslot_legit(timeslot):
    (sh, sm), (eh, em) = unpack_time_slot(timeslot)
    start_minutes = sh * 60 + sm
    end_minutes = eh * 60 + em
    duration = end_minutes - start_minutes
    return 0 < duration <= 119

def load_credentials():
    load_dotenv()
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    TITLE = os.getenv("TITLE")
    return USERNAME, PASSWORD, TITLE

def read_booking_date():
    if 3 <= len(sys.argv) <= 4:
        date = sys.argv[1]  # format: YYYY-MM-DD
        time_slot = sys.argv[2]  # format: HH:MM-HH:MM
        room_type = sys.argv[3] if len(sys.argv) == 4 else "_" # "solo" or "group" or "_"
        
        if not is_timeslot_legit(time_slot):
            print("Invalid time slot duration. It must be between 1 and 119 minutes.")
            sys.exit(1)
        return date, time_slot, room_type
    else: 
        print("Usage: python main.py <date: YYYY-MM-DD> <time_slot: HH:MM-HH:MM> <room_type: solo/group/_>")
        sys.exit(1)

def login(driver, username, password):
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")

    username_input.clear()
    password_input.clear()

    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

def select_date(driver):
    driver.implicitly_wait(5)
    date_button = driver.find_element(By.XPATH, f".//li[@data-date=\"{date}\"]")
    date_button.click()
    # bouton_valider = driver.find_element(By.CLASS_NAME, "Cal__Day__selection")
    # bouton_valider.click()

def select_time_slot(driver, time_slot):
    (sh, sm), (eh, em) = unpack_time_slot(time_slot)
    
    driver.implicitly_wait(5)
    heure_debut_input = driver.find_element(By.XPATH, "(//input[@type='number'])[1]")
    minute_debut_input = driver.find_element(By.XPATH, "(//input[@type='number'])[2]")
    heure_fin_input = driver.find_element(By.XPATH, "(//input[@type='number'])[3]")
    minute_fin_input = driver.find_element(By.XPATH, "(//input[@type='number'])[4]")

    heure_debut_input.clear()
    minute_debut_input.clear()
    heure_fin_input.clear()
    minute_fin_input.clear()

    heure_debut_input.send_keys(str(sh))
    minute_debut_input.send_keys(str(sm))
    heure_fin_input.send_keys(str(eh))
    minute_fin_input.send_keys(str(em))

    bouton_success = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[3]/div/div/div/div/div/div[2]/button")
    bouton_success.click()

def filter_search(driver):
    driver.implicitly_wait(5)
    music_room_checkbox = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[1]/div/div[2]/div/div[7]/label")
    music_room_checkbox.click()
    saclay_room_checkbox = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[1]/div/div[2]/div/div[13]/label")
    saclay_room_checkbox.click()
    unavailable_room_checkbox = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[1]/div/div[2]/div/div[23]/label")
    unavailable_room_checkbox.click()

def format_event_time(event_time):
    event_time = event_time.split("&nbsp;")
    start = event_time[1]
    end = event_time[3]
    sh, sm = map(int, start.split("h"))
    eh, em = map(int, end.split("h"))
    return sh, sm, eh, em

def clean_innerHTML(innerHTML):
    replacements = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": "\"",
        "&#39;": "'",
        "&nbsp;": " ",
    }
    for old, new in replacements.items():
        innerHTML = innerHTML.replace(old, new)
    return innerHTML

def explore_rooms(driver, rooms_dict, available_rooms):
    driver.implicitly_wait(15)
    view_more_button = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[2]/ul[2]/div[1]/button")
    view_more_button.click()
    parent1 = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[2]/ul[2]")
    parent2 = driver.find_element(By.XPATH, "/html/body/div/div/section/div[1]/div[4]/div[2]/ul[2]/div/div/div")
    rooms = parent1.find_elements(By.XPATH, "./li")
    rooms.extend(parent2.find_elements(By.XPATH, "./li"))

    for room in rooms:
        room_name = clean_innerHTML(room.find_element(By.XPATH, ".//h2").get_attribute("innerHTML")).split(",")[0]

        rooms_dict[room_name] = {"AVAILABLE": False,
                                 "EVENTS": {}}

        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[@id=\"roomBookModal\"]"))
        )

        room_info_ul = room.find_element(By.XPATH, ".//ul")
        room_info_lis = room_info_ul.find_elements(By.XPATH, "./li")
        if len(room_info_lis) > 3:
            rooms_dict[room_name]["AVAILABLE"] = False
        else:
            available_rooms[room_name] = room
            rooms_dict[room_name]["AVAILABLE"] = True
        
        room.click()
        driver.implicitly_wait(3)
        events_h6 = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/div[2]/div/div/div[2]/div[1]/h6")
        events_innerHTML = events_h6.get_attribute("innerHTML")
        match events_innerHTML[0]:
            case "A": events_number = 0
            case "U": events_number = 1
            case _: events_number = int(events_innerHTML[0])
        
        
        if events_number > 0:
            events_parent = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/div[2]/div/div/div[2]/div[1]/div")
            events = events_parent.find_elements(By.XPATH, "./div")
            for event in events:
                event_title = event.find_element(By.XPATH, "./div")
                event_name = event_title.find_element(By.XPATH, "./h5").get_attribute("innerHTML")
                event_time = event_title.find_element(By.XPATH, "./span").get_attribute("innerHTML")
                event_author = clean_innerHTML(event.find_element(By.XPATH, "./span/a").get_attribute("innerHTML"))
                
                event_sh, event_sm, event_eh, event_em = format_event_time(event_time)

                event_dict = {
                    "TITLE": event_name,
                    "TIMESPAN": f"{event_sh}:{event_sm}-{event_eh}:{event_em}",
                    "AUTHOR": event_author,
                }

                rooms_dict[room_name]["EVENTS"][event_name] = event_dict

        cancel_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/div[2]/div/div/div[3]/button[1]")
        time.sleep(0.6)
        cancel_button.click()

def display_info(rooms_dict, available_rooms, date, time_slot):
    print("--------------------------------------------")
    print(f"LE {date} À {time_slot}")
    print("--------------------------------------------")
    for room_name, room_info in rooms_dict.items():
        print(f"SALLE: {room_name}")
        if room_info["AVAILABLE"]:
            print("  ETAT: DISPONIBLE")
        else:
            print("  ETAT: NON DISPONIBLE")
        if room_info["EVENTS"]:
            print("  RESERVATIONS:")
            for event_name, event_info in room_info["EVENTS"].items():
                print(f"    - {event_name}: {event_info['TIMESPAN']} | RÉSERVÉE PAR: {event_info['AUTHOR']}")
        print("--------------------------------------------")
    print(available_rooms)

def book_room(driver, room, TITLE):
    time.sleep(3)
    room.click()
    time.sleep(3)
    booking_title_input = driver.find_element(By.XPATH, "//*[@id=\"eventName\"]")
    booking_title_input.clear()
    booking_title_input.send_keys(TITLE)
    confirm_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/div[2]/div/div/div[3]/button[2]")
    confirm_button.click()

def main(USERNAME, PASSWORD, TITLE, date, time_slot, room_type):
    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://resa.centralesupelec.fr/")

    login(driver, USERNAME, PASSWORD)
    select_date(driver)
    select_time_slot(driver, time_slot)
    filter_search(driver)

    available_rooms = {}
    rooms_dict = {}
    explore_rooms(driver, rooms_dict, available_rooms)
    
    display_info(rooms_dict, available_rooms, date, time_slot)

    if room_type != "_":
        salle_disponible = False
        if room_type == "solo":
            for room_name in SALLES_SOLO:
                if room_name in available_rooms:
                    salle_disponible = True
                    room = available_rooms[room_name]
                    book_room(driver, room, TITLE)
                    print(f"DEMANDE DE RÉSERVATION DE LA {room_name} POUR LE {date} À {time_slot} ENVOYÉE.")
                    break
        elif room_type == "group":
            for room_name in SALLES_GROUPES:
                if room_name in available_rooms:
                    salle_disponible = True
                    print(f"Salle de groupe disponible: {room_name}")
                    room = available_rooms[room_name]
                    book_room(driver, room, TITLE)
                    print(f"DEMANDE DE RÉSERVATION DE LA {room_name} POUR LE {date} À {time_slot} ENVOYÉE.")
                    break
        if not salle_disponible: print("AUCUNE SALLE DISPONIBLE POUR TYPE DEMANDÉ.")

    driver.quit()
    

if __name__ == "__main__":
    USERNAME, PASSWORD, TITLE = load_credentials()
    date, time_slot, room_type = read_booking_date()
    main(USERNAME, PASSWORD, TITLE, date, time_slot, room_type)