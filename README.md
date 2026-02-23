# sdrlock

SDRLock is a application which is built to use a bridge of python and Node.JS to allow you to automate your RTL-SDR. 

Following features will be included 

Signal lock w/ doppler shift correction
AGC
Live processing/decoding
Motor movements
Automatic TLE updates
Automatic decoded file upload
Signal scan
Eventually support for high bandwith (above 1.7Ghz)

This project was designed with use for the Meteor-M satellites in mind. It will allow you to run this program to auto lock the signal, then decode it with 72k QPSK live. It will be designed with other satellites in mind, just in case the meteor program ends like NOAA APT.
