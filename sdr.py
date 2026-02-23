# RTL-SDR python program; utilizies python to signal lock and nodejs to decode and rationalize telemetry


from tokenize import String

import numpy as np
from rtlsdr import RtlSdr

sdr = RtlSdr()

sdr.sample_rate = 2.4e6
sdr.center_freq = 137.7e6  # Meteor downlink
sdr.gain = "auto"

samples = sdr.read_samples(256 * 1024)

print("First samples:", samples[:10])

sdr.close
# tle decoding


def decodeTLEData():
    from datetime import datetime

    from sgp4.api import Satrec, jday

    # Default TLE (Meteor M2-3 02/23/2026)
    # I will include auto downloads later, but for now you can get your TLE from NASA or Ny2O
    line1 = "57166U 23091A   26053.92188655 -.00000010  00000-0  14463-4 0  9994"
    line2 = "57166  98.6247 111.1596 0004811 133.1685 226.9897 14.24035955138258"

    sat = Satrec.twoline2rv(line1, line2)

    now = datetime.utcnow()
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

    e, r, v = sat.sgp4(jd, fr)

    print("Position (km):", r)
    print("Velocity (km/s):", v)


# testing

decodeTLEData()
