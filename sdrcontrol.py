import math
import subprocess
import time
from datetime import timedelta

import requests
from skyfield.api import EarthSatellite, Topos, load

# set all of the settings here
# even though meteor is the only satellites to even use anymore
SAT_NAME = "Meteor M-2 4"
MIN_ELEVATION = 20  # degrees (ignore garbage passes)

VERSION = "0.1PR"

# location; default is detriot, MI
LAT = 42.3297
LON = -83.0425
LOC_NICKNAME = "Detriot, MI"  # just for refrence in your config; optional

OUTPUT_DIR = "output"  # where satdump saves data

# RECORDER

SAMPLE_RATE = 1.24e6
FREQ = 1.379e8
BASEBAND_FORMAT = "cs16"

subprocess.run("clear")

print(
    f"CONFIG OVERVIEW\n\nVERSION: {VERSION}\n\nTarget Sat: {SAT_NAME}\nMinimum Elevation: {MIN_ELEVATION}\n\nLatitude: {LAT}\nLongitude: {LON}\nLocation Name {LOC_NICKNAME}\n\nOutput Directory: {OUTPUT_DIR}\n\nSleeping for 5 seconds before clearing"
)


time.sleep(5)
subprocess.run("clear")


# =========================
# FETCH TLE
# =========================
def pull_tle(name):
    url = "https://celestrak.org/NORAD/elements/weather.txt"

    response = requests.get(url)
    response.raise_for_status()

    lines = response.text.strip().splitlines()

    for i in range(len(lines)):
        if name in lines[i]:
            return {
                "name": lines[i].strip(),
                "line1": lines[i + 1].strip(),
                "line2": lines[i + 2].strip(),
            }

    raise Exception("Satellite not found")


# =========================
# SETUP SKYFIELD
# =========================
ts = load.timescale()

tle = pull_tle("METEOR-M2 4")

sat = EarthSatellite(tle["line1"], tle["line2"], tle["name"], ts)

observer = Topos(latitude_degrees=LAT, longitude_degrees=LON)


# =========================
# FIND PASSES
# =========================
def get_passes(hours=24):
    t0 = ts.now()
    t1 = ts.utc(t0.utc_datetime() + timedelta(hours=hours))

    times, events = sat.find_events(observer, t0, t1, altitude_degrees=MIN_ELEVATION)

    passes = []
    current_pass = {}

    for t, event in zip(times, events):
        if event == 0:  # AOS
            current_pass["start"] = t
        elif event == 1:  # MAX
            current_pass["max"] = t
        elif event == 2:  # LOS
            current_pass["end"] = t
            passes.append(current_pass)
            current_pass = {}

    return passes


# =========================
# RECORD WITH SATDUMP
# =========================
def record_pass(time, nameModifier):
    print("Starting recording...")

    # satdump record pass1 --source rtlsdr --samplerate 1.24e+6 --frequency 1.379e+8 --baseband_format cs16
    # reference pass ^

    subprocess.run(
        [
            "satdump",
            "record",
            str(nameModifier),
            "--source",
            "rtlsdr",
            "--samplerate",
            str(SAMPLE_RATE),
            "--frequency",
            str(FREQ),
            "--baseband_format",
            str(BASEBAND_FORMAT),
            "--timeout",
            str(time + 30),
        ]
    )

    print("Recording finished.")


# where the magic happens
# lowk dont know how this shit is working but if it aint broke dont fix it
while True:
    print("Checking for passes...\n")

    passes = get_passes(24)

    if not passes:
        print("No passes found.\n")
        time.sleep(300)
        continue

    for p in passes:
        start_time = p["start"].utc_datetime()
        now = ts.now().utc_datetime()
        end_time = p["end"].utc_datetime()
        wait_seconds = (start_time - now).total_seconds()
        total_pass = (end_time - start_time).total_seconds()
        if wait_seconds > 0:
            remaining = int(wait_seconds)

            while remaining > 0:
                subprocess.run("clear")
                print(f"Next pass at {start_time}\n\n")
                print(
                    f"Starting in\n\n{remaining}s\n{math.floor(remaining / 60)}m\n{math.floor(remaining / 60 / 60)}h"
                )
                print(
                    f"\n\n\nYou are using SDRLock version {VERSION}. Protected under MIT License (2026)."
                )
                time.sleep(1)
                remaining -= 1
            record_pass(total_pass, start_time)

    # wait before checking again
    time.sleep(300)
