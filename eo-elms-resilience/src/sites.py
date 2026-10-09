"""Pilot sampling sites: 5 agricultural locations per UK region (lat, lon).
Chosen a priori in arable/mixed-farming landscapes; each is the centre of a
6 x 6 km MODIS window. Region names match Defra's cereal survey labels."""
KM = 3  # half-width of window in km
SITES = {
 'North East': [(55.35,-1.70),(55.05,-1.80),(54.60,-1.45),(55.68,-2.10),(54.85,-1.60)],
 'North West and Merseyside': [(53.83,-2.90),(53.60,-2.85),(53.10,-2.75),(54.70,-2.75),(53.33,-3.05)],
 'Yorkshire & The Humber': [(54.05,-0.55),(53.80,-0.10),(54.00,-1.30),(53.70,-0.95),(54.20,-0.80)],
 'East Midlands': [(53.20,-0.40),(52.85,-0.10),(53.40,-0.20),(52.40,-0.85),(53.20,-0.95)],
 'West Midlands': [(52.75,-2.60),(52.10,-2.75),(52.25,-1.50),(52.85,-2.05),(52.15,-2.05)],
 'Eastern': [(52.35,0.05),(52.70,0.90),(52.25,1.00),(51.85,0.50),(52.05,-0.25)],
 'South East and London': [(51.15,-1.25),(51.65,-1.30),(51.25,1.10),(50.90,-0.70),(51.50,-1.10)],
 'South West': [(51.25,-1.85),(50.80,-2.25),(51.05,-2.65),(51.75,-1.85),(50.85,-3.30)],
 'Scotland': [(56.25,-3.05),(56.65,-2.75),(57.40,-2.30),(55.95,-2.65),(55.70,-2.30)],
 'Wales': [(51.45,-3.40),(51.75,-4.95),(51.75,-2.85),(53.25,-4.35),(53.20,-3.10)],
}
ENGLAND = [r for r in SITES if r not in ('Scotland', 'Wales')]
