"""Version 5 image derivatives from 'Assets from Client/October 26, 2026' (and earlier folders).
- Originals are never modified.
- 'crop' (left, top, right, bottom as fractions) removes the phone's "vivo Y27 / date" mark in the
  bottom-left corner of staff photos; full-size cleaned copies go to edited-images/v5/.
- Web derivatives (JPEG + WebP) go to assets/img/v5/.
Run from the project root:  python _tools/build_v5_images.py
"""
import os, subprocess, tempfile
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW = os.path.join(ROOT, 'Assets from Client', 'October 26, 2026')
OUT = os.path.join(ROOT, 'assets', 'img', 'v5')
CLEAN = os.path.join(ROOT, 'edited-images', 'v5')
os.makedirs(OUT, exist_ok=True); os.makedirs(CLEAN, exist_ok=True)

MARK_L = (0, 0, 1, .89)   # landscape staff photo: trim the bottom strip holding the phone mark
MARK_P = (0, 0, 1, .92)   # portrait staff photo
N2 = 'Assets from Client/November 2, 2026/Enhanced Photo'
N5 = 'Assets from Client/November 5'
N7 = 'Assets from Client/November 7'

# id, source file, crop, output widths
JOBS = [
    # The resort
    ('dusk-pool',        'IMG_1857 2.JPG', None, (640, 1215)),
    ('main-building',    'viber_image_2026-10-20_16-40-24-711.jpg', MARK_P, (640, 1200)),
    ('lobby-lounge',     'viber_image_2026-10-21_06-38-24-660.jpg', MARK_L, (800, 1424)),
    ('reception',        'viber_image_2026-10-21_08-30-39-336.jpg', MARK_P, (640, 1200)),
    ('beach-palms',      'viber_image_2026-10-21_08-43-10-706.jpg', MARK_L, (800, 1424)),
    ('tower-blue',       'viber_image_2026-10-21_08-43-10-998.jpg', MARK_P, (640, 1200)),
    ('tower-wide',       'viber_image_2026-10-21_08-43-11-069.jpg', MARK_L, (800, 1424)),
    ('tower-storm',      'IMG_8835.HEIC', None, (640, 1100)),
    ('palms-sky',        'IMG_1077.HEIC', None, (640, 1100)),
    ('corridor',         'viber_image_2026-10-20_16-40-23-831.jpg', MARK_P, (640, 1200)),
    # Pool Suite Room (matches the Pool Suite photo on the resort's own rate sheet)
    ('poolsuite-room',   'IMG_2159 2.HEIC', None, (800, 1200)),
    ('poolsuite-bed',    'IMG_2160 2.HEIC', None, (800, 1200)),
    ('poolsuite-bar',    'IMG_2161 2.HEIC', None, (800, 1200)),
    ('poolsuite-pantry', 'IMG_2162 2.HEIC', None, (800, 1200)),
    ('poolsuite-family', 'IMG_2168 2.HEIC', None, (800, 1200)),
    ('poolsuite-loft',   'IMG_2171.HEIC', None, (800, 1200)),
    ('poolsuite-bath',   'IMG_2166 2.HEIC', None, (800, 1200)),
    # Luxury Kubo
    ('kubo-exterior',    'IMG_1068.HEIC', None, (640, 1100)),
    ('kubo-living',      'IMG_2176.HEIC', None, (800, 1200)),
    ('kubo-bedroom',     'IMG_2181 2.JPG', None, (800, 1080)),
    ('kubo-loftbeds',    'IMG_2183 2.JPG', None, (800, 1080)),
    ('kubo-bath',        'IMG_2182 2.JPG', None, (640, 976)),
    # Main-building rooms (matched by bed set-up to the rate sheets; see notes)
    ('room-single',      'viber_image_2026-10-20_18-20-57-643.jpg', MARK_L, (800, 1424)),
    ('room-superior',    'viber_image_2026-10-20_18-42-48-996.jpg', MARK_L, (800, 1424)),
    ('room-deluxe',      'viber_image_2026-10-20_16-41-17-547.jpg', MARK_L, (800, 1424)),
    ('room-suiteloft',   'viber_image_2026-10-20_16-45-33-108.jpg', MARK_L, (800, 1424)),
    ('room-execloft',    'viber_image_2026-10-20_17-15-20-146.jpg', MARK_P, (640, 1200)),
    ('room-loftsingles', 'viber_image_2026-10-20_17-06-58-304.jpg', MARK_L, (800, 1424)),
    ('room-bath',        'viber_image_2026-10-20_16-44-51-697.jpg', MARK_P, (640, 1200)),
    # Tents
    ('tent',             '309AD28B-9FEB-4664-9C5C-4FA98A62EBED.heic', None, (640, 1100)),
    # Campsite tents: the resort's social post; crop inside the white frame line and above the logo/text
    ('tents-campsite',   'Initial Images/469518456_605136372186168_174922518552061940_n.jpg', (72/1080, 54/1080, 1008/1080, 932/1080), (800, 936)),
    # Water and island
    ('kayak-clear',      'IMG_2380.HEIC', None, (640, 1100)),
    ('kayak-clear-2',    'IMG_2372.HEIC', None, (640, 1100)),
    ('boat-longinus',    'IMG_9169.JPG', MARK_L, (800, 1424)),
    ('boat-rogelius',    'IMG_9170.JPG', MARK_L, (800, 1424)),
    ('boat-omon',        'IMG_9171.JPG', MARK_L, (800, 1424)),
    ('ecart',            'RESORT PRINTABLES (2).png', None, (640, 1200)),
    ('bikes',            'IMG_1159.jpg', None, (640, 1100)),
    ('biker', 'Initial Images/Activities/pexels-enrico-musitelli-1035698384-34377533.jpg', None, (640, 1100)),
    ('vball', 'Initial Images/Pexels/pexels-helder-pereira-326724210-33490287.jpg', None, (640, 1100)),
    ('pingpong2', 'Initial Images/Pexels/pexels-haydar-acer-1111927873-33063727.jpg', None, (640, 1100)),
    ('darts2', 'Initial Images/Pexels/pexels-kevin-malik-8763232.jpg', (.1, 0, .8, 1), (800, 1200)),
    ('tents-bamboo', 'Assets from Client/October 30, 2026/images (2).jpg', None, (259,)),
    ('r-single-3', 'Assets from Client/October 30, 2026/room 4.jpg', MARK_P, (640, 1100)),
    ('r-single-bath2', 'Assets from Client/October 30, 2026/room 4 cr.jpg', MARK_P, (640, 1100)),
    ('r-single-bath3', 'Assets from Client/October 30, 2026/room 6 cr.jpg', MARK_P, (640, 1100)),
    ('r-superior-4', 'Assets from Client/October 30, 2026/room 5 (1).jpg', MARK_L, (800, 1424)),
    ('r-superior-bath2', 'Assets from Client/October 30, 2026/room 5 cr (1).jpg', MARK_P, (640, 1100)),
    ('r-superior-bath3', 'Assets from Client/October 30, 2026/room 2 cr.jpg', MARK_P, (640, 1100)),
    ('r-suite-bath2', 'Assets from Client/October 30, 2026/room 1 cr (1).jpg', MARK_P, (640, 1100)),
    ('r-suite-bath3', 'Assets from Client/October 30, 2026/room 8 cr.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-4', 'Assets from Client/October 30, 2026/room 28 deluxe (1).jpg', MARK_P, (640, 1100)),
    ('r-deluxe-bath2', 'Assets from Client/October 30, 2026/room 28, cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-5', 'Assets from Client/October 30, 2026/room 25 suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-6', 'Assets from Client/October 30, 2026/room 25 suite loft (1).jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-7', 'Assets from Client/October 30, 2026/room 26.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-8', 'Assets from Client/October 30, 2026/room 26 (1).jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-9', 'Assets from Client/October 30, 2026/room 26 suite loft (1).jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-10', 'Assets from Client/October 30, 2026/room 26, suite loft.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-11', 'Assets from Client/October 30, 2026/room 26, suite loft (1).jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-bath2', 'Assets from Client/October 30, 2026/room 25 cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-bath3', 'Assets from Client/October 30, 2026/room 26 cr.jpg', MARK_P, (640, 1100)),
    ('r-exec-4', 'Assets from Client/October 30, 2026/room 27 executive loft (1).jpg', MARK_L, (800, 1424)),
    ('r-exec-bath2', 'Assets from Client/October 30, 2026/room 27 cr (1).jpg', MARK_P, (640, 1100)),
    ('ps-020', 'Assets from Client/October 30, 2026/pool suite room (1).HEIC', None, (800, 1200)),
    ('ps-021', 'Assets from Client/October 30, 2026/pool suite room (10).HEIC', None, (800, 1200)),
    ('ps-022', 'Assets from Client/October 30, 2026/pool suite room (11).HEIC', None, (800, 1200)),
    ('ps-023', 'Assets from Client/October 30, 2026/pool suite room (12).HEIC', None, (800, 1200)),
    ('ps-024', 'Assets from Client/October 30, 2026/pool suite room (13).HEIC', None, (800, 1200)),
    ('ps-025', 'Assets from Client/October 30, 2026/pool suite room (2).HEIC', None, (800, 1200)),
    ('ps-026', 'Assets from Client/October 30, 2026/pool suite room (3).HEIC', None, (800, 1200)),
    ('ps-027', 'Assets from Client/October 30, 2026/pool suite room (4).HEIC', None, (800, 1200)),
    ('ps-028', 'Assets from Client/October 30, 2026/pool suite room (5).HEIC', None, (800, 1200)),
    ('ps-029', 'Assets from Client/October 30, 2026/pool suite room (6).HEIC', None, (800, 1200)),
    ('ps-030', 'Assets from Client/October 30, 2026/pool suite room (7).HEIC', None, (800, 1200)),
    ('ps-031', 'Assets from Client/October 30, 2026/pool suite room (8).HEIC', None, (800, 1200)),
    ('ps-032', 'Assets from Client/October 30, 2026/pool suite room (9).HEIC', None, (800, 1200)),
    ('ps-033', 'Assets from Client/October 30, 2026/pool suite room.HEIC', None, (800, 1200)),
    ('ps-034', 'Assets from Client/October 30, 2026/pool suite room.HEIC.HEIC', None, (800, 1200)),
    ('lobby2', 'Assets from Client/October 30, 2026/lobby.jpg', MARK_L, (800, 1424)),
    ('reef-raft2', 'Assets from Client/October 30, 2026/MORION REEF RAFT.png', None, (572,)),
    # Client-enhanced photos (Assets from Client/November 1, 2026)
    ('e-sandbar-people', 'Assets from Client/November 1, 2026/Enhanced Photo/Aerial sandbar with turquoise waters-8.png', None, (800, 1400)),
    ('e-vball', 'Assets from Client/November 1, 2026/Enhanced Photo/Beach volleyball by the outrigger boat-4.png', None, (800, 1400)),
    ('e-pavilion', 'Assets from Client/November 1, 2026/Enhanced Photo/Cloudy garden pavilion cocktail setup-16.png', None, (640, 1100)),
    ('e-room-blue', 'Assets from Client/November 1, 2026/Enhanced Photo/Compact blue accent-wall room-8.png', None, (640, 1100)),
    ('e-beach-dining', 'Assets from Client/November 1, 2026/Enhanced Photo/Dusk beach dining under string lights-10.png', None, (800, 1400)),
    ('e-pool-elevated', 'Assets from Client/November 1, 2026/Enhanced Photo/Elevated resort pool with palms and people-2.png', None, (800, 1400)),
    ('e-fire', 'Assets from Client/November 1, 2026/Enhanced Photo/Fire Performer with Curved Light Trails-1.png', None, (800, 1400)),
    ('e-sunset-coast', 'Assets from Client/November 1, 2026/Enhanced Photo/Golden Sunset Over Rocky Coast-6.png', None, (800, 1400)),
    ('e-statues', 'Assets from Client/November 1, 2026/Enhanced Photo/Historic plaza with statues and palms-4.png', None, (800, 1400)),
    ('e-pool-night', 'Assets from Client/November 1, 2026/Enhanced Photo/Illuminated resort pool beneath a dark sky-13.png', None, (640, 1100)),
    ('e-room-loft', 'Assets from Client/November 1, 2026/Enhanced Photo/Loft room with twin wooden beds-4.png', None, (800, 1400)),
    ('e-pool-pergola', 'Assets from Client/November 1, 2026/Enhanced Photo/Nighttime resort pool behind pergola beams-3.png', None, (640, 1100)),
    ('e-palad', 'Assets from Client/November 1, 2026/Enhanced Photo/Palad Sandbar Under Open Skies-2.png', None, (800, 1400)),
    ('e-vball-wide', 'Assets from Client/November 1, 2026/Enhanced Photo/Panoramic beach volleyball by the shore-11.png', None, (800, 1400)),
    ('e-wedding-aisle', 'Assets from Client/November 1, 2026/Enhanced Photo/Peach sunset beach wedding aisle-7.png', None, (640, 1100)),
    ('e-room-red', 'Assets from Client/November 1, 2026/Enhanced Photo/Refreshed red-accent resort bedroom-6.png', None, (640, 1100)),
    ('e-room-family', 'Assets from Client/November 1, 2026/Enhanced Photo/Resort family room with multiple beds-10.png', None, (800, 1400)),
    ('e-loungers', 'Assets from Client/November 1, 2026/Enhanced Photo/Resort poolside loungers and palms-5.png', None, (800, 1400)),
    ('e-room-two', 'Assets from Client/November 1, 2026/Enhanced Photo/Resort room with two neatly made beds-5.png', None, (800, 1400)),
    ('e-sandbar-aerial', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored aerial view of a tropical sandbar-7.png', None, (640, 1100)),
    ('e-cliff-tree', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored cliffside tree by the sea-8.png', None, (640, 1100)),
    ('e-kubo-palms', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored cottage under swaying palms-12.png', None, (640, 1100)),
    ('e-room-three', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored resort bedroom with three beds-9.png', None, (800, 1400)),
    ('e-kubo-cart', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored thatched cottage among palms-10.png', None, (640, 1100)),
    ('e-sunglasses', 'Assets from Client/November 1, 2026/Enhanced Photo/Sunglasses, lifeguard tower, and ocean view-1.png', None, (640, 1100)),
    ('e-pool-bikes', 'Assets from Client/November 1, 2026/Enhanced Photo/Sunlit courtyard pool with bicycles-12.png', None, (800, 1400)),
    ('e-sunset-rocks', 'Assets from Client/November 1, 2026/Enhanced Photo/Sunset over Marinduque’s coastal rocks-9.png', None, (800, 1400)),
    ('e-room-teal', 'Assets from Client/November 1, 2026/Enhanced Photo/Teal resort bedroom with trundle bed-11.png', None, (800, 1400)),
    ('e-vans', 'Assets from Client/November 1, 2026/Enhanced Photo/Two white vans with blurred plates-3.png', None, (800, 1400)),
    ('e-ungab', 'Assets from Client/November 1, 2026/Enhanced Photo/Ungab Rock Arch by Calm Waters-3.png', None, (800, 1400)),
    ('e-boat-beach', 'Assets from Client/November 1, 2026/Enhanced Photo/WhatsApp Image 2026-10-31 at 6.34.44 AM (1).jpeg', None, (640, 1100)),
    ('e-boat-water', 'Assets from Client/November 1, 2026/Enhanced Photo/WhatsApp Image 2026-10-31 at 6.34.44 AM.jpeg', None, (640, 1100)),
    ('e-resort-path', 'Assets from Client/November 1, 2026/Enhanced Photo/White Resort by the Palm-Lined Pool-6.png', None, (800, 1400)),
    ('e-resort-pool', 'Assets from Client/November 1, 2026/Enhanced Photo/White resort beside a palm-lined pool-9.png', None, (800, 1400)),
    ('e-ecart-roses', 'Assets from Client/November 1, 2026/Enhanced Photo/White resort shuttle cart with yellow roses-14.png', None, (640, 1100)),
    ('e-kayak', 'Assets from Client/November 1, 2026/Enhanced Photo/Woman paddling a transparent kayak-5.png', None, (800, 1400)),
    ('e-room-yellow', 'Assets from Client/November 1, 2026/Enhanced Photo/Yellow-green resort room with twin beds-7.png', None, (800, 1400)),
    ('e-beach-tower', 'Assets from Client/November 1, 2026/Enhanced Photo/Tropical beach resort with mountain views.png', None, (800, 1400)),
    ('e-pool-night-c', 'Assets from Client/November 1, 2026/Enhanced Photo/Illuminated resort pool beneath a dark sky-13.png', (0, 0, 1, .64), (800, 1086)),
    ('e-kubo-cart-c', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored thatched cottage among palms-10.png', (0, 0, .80, 1), (640, 869)),
    ('e-kayak-lake', 'Assets from Client/November 1, 2026/Enhanced Photo/Woman kayaking across a sunlit mountain lake-11.png', None, (800, 1400)),
    ('e-beach-tower-p', 'Assets from Client/November 1, 2026/Enhanced Photo/Tropical loungers overlooking sea and mountains.png', None, (640, 1086)),
    ('e-dusk', 'Assets from Client/November 1, 2026/Enhanced Photo/Islas Moriones Beach Resort at Dusk-4.png', None, (800, 1400)),
    ('e-morion-bust', 'Assets from Client/November 1, 2026/Enhanced Photo/Morion warrior bust beneath the reef-8.png', (.36, 0, 1, 1), (640, 877)),
    ('e-octopus', 'Assets from Client/November 1, 2026/Enhanced Photo/Blue-ringed octopus in seagrass-2.png', None, (800, 1254)),
    ('e-dog', 'Assets from Client/November 1, 2026/Enhanced Photo/Bulldog on a sandy resort path-1.png', None, (800, 1254)),
    ('e-entrance', 'Assets from Client/November 1, 2026/Enhanced Photo/Islas Moriones Beach Resort Entrance-6.png', None, (800, 1400)),
    ('e-sign', 'Assets from Client/November 1, 2026/Enhanced Photo/Islas Moriones Beach Resort Sign-7.png', None, (800, 1400)),
    ('e-sand-morion', 'Assets from Client/November 1, 2026/Enhanced Photo/Morion warrior sand sculpture by the beach-11.png', None, (640, 1086)),
    ('e-tent-lime', 'Assets from Client/November 1, 2026/Enhanced Photo/Restored lime green tent in palm garden-3.png', None, (800, 1254)),
    ('e-turtle', 'Assets from Client/November 1, 2026/Enhanced Photo/Sea turtle on moonlit sand-10.png', None, (800, 1254)),
    ('e-tent-teal', 'Assets from Client/November 1, 2026/Enhanced Photo/Turquoise Tent Among Coconut Palms-9.png', None, (800, 1254)),
    ('e-pool-night2', 'Assets from Client/November 1, 2026/Enhanced Photo/White resort pool at night-5.png', None, (800, 1400)),
    ('e-seastars', 'Assets from Client/November 1, 2026/Enhanced Photo/Orange and blue sea stars on reef-1.png', None, (800, 1254)),
    ('e-warrior-l', 'Assets from Client/November 1, 2026/Enhanced Photo/Underwater Warrior Statue Amid Colorful Corals.png', (.481, .17, 1, .861), (867,)),
    ('e-warrior-p', 'Assets from Client/November 1, 2026/Enhanced Photo/Morion Reef Warrior Beneath Blue Waters.png', (.40, .262, 1, .863), (652,)),
    ('e-warrior-w', 'Assets from Client/November 1, 2026/Enhanced Photo/Underwater Warrior Statue Amid Colorful Corals.png', None, (900, 1400)),
    ('e-tidepool-p', 'Assets from Client/November 1, 2026/Enhanced Photo/Golden-hour rocks above a turquoise tidal pool.png', None, (640, 1086)),
    ('e-campsite', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Sunny Campsite Beneath Coconut Palms-2.png', None, (640, 1024)),
    ('e-sanddollars', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Five Sand Dollars Over Turquoise Water.png', None, (640, 1024)),
    ('e-pickleball', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Aerial garden pickleball court-1.png', None, (800, 1400)),
    ('e-tt-w', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Tropical Table Tennis by the Sea-4.png', None, (800, 1400)),
    ('e-tt-p', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Tropical table tennis by the sea-3.png', None, (640, 1024)),
    ('e-bikes-w', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Mountain Bikes Among Coconut Palms-2.png', None, (800, 1400)),
    ('e-bikes-p', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Mountain Bikes Beneath Coconut Palms-1.png', None, (640, 1024)),
    ('e-sanddollars-w', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Five Sand Dollars Over Turquoise Water.png', (0, .35, 1, .85), (640, 1024)),
    ('e-rock-w', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Pitted Coastal Rock at Golden Sunset-2 (1).png', None, (800, 1400)),
    ('e-rock-p', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Pitted Rock and Golden Sunset-1 (1).png', None, (640, 1024)),
    ('tents-campsite-full', 'Initial Images/469518456_605136372186168_174922518552061940_n.jpg', None, (1400,)),
    ('darts2-full', 'Initial Images/Pexels/pexels-kevin-malik-8763232.jpg', None, (1400,)),
    ('e-morion-bust-full', 'Assets from Client/November 1, 2026/Enhanced Photo/Morion warrior bust beneath the reef-8.png', None, (1400,)),
    ('e-warrior-p-full', 'Assets from Client/November 1, 2026/Enhanced Photo/Morion Reef Warrior Beneath Blue Waters.png', None, (1400,)),
    ('maniwaya-cove-full', 'IMG_1188.HEIC', None, (1400,)),
    ('sunset-boat-beach-full', 'edited-images/sunset-boat.jpg', None, (1400,)),
    ('deck-table-full', 'Assets from Client/October 30, 2026/203add1d0cc6e9e797221bf8adcd6392bb06b5e0.jpg', None, (1400,)),
    ('e-campsite-bamboo', 'Assets from Client/November 1, 2026/Enhanced Photo/10PM/Sunlit bamboo campsite by the palms-1.png', None, (800, 1400)),
    ('cafe-logo', 'Assets from Client/November 1, 2026/WhatsApp Image 2026-10-31 at 6.34.46 AM (2).jpeg', None, (480,)),
    ('bikes-crop',       'IMG_1159.jpg', (0, .40, 1, 1), (800, 1400)),
    ('kayak-pov',        'IMG_2380.HEIC', (0, .50, 1, 1), (800, 1400)),
    ('kayak-pov-2',      'IMG_2372.HEIC', (0, .50, 1, 1), (800, 1400)),
    ('ungab',            'IMG_4354.heic', None, (640, 1100)),
    ('ungab-arch',       'IMG_4355.heic', None, (640, 1100)),
    ('sandbar-aerial',   'image (1).png', None, (800, 1080)),
    ('reef-raft',        'Screenshot 2025-10-02 at 8.57.18 AM.png', None, (572,)),
    ('maniwaya-rocks',   'IMG_1156.jpg', None, (640, 1100)),
    ('pingpong-darts',   'viber_image_2026-10-20_16-40-24-808.jpg', MARK_L, (800, 1424)),
    ('darts',            '1df6a445c2cbbc474487db571a2e7874.jpg', None, (600,)),
    ('kayak-float',      '37d7ae8d44e5e5d5804f941192a827ea.jpg', None, (895,)),
    # Photos extracted from ISLAS BROCHURE 2026 (1).pdf (pypdf) into edited-images/brochure/
    ('pool-loungers',    'edited-images/brochure/pool-loungers.jpg', None, (640, 908)),
    ('main-palms',       'edited-images/brochure/main-building-palms.jpg', None, (800, 1210)),
    ('resort-sign',      'edited-images/brochure/resort-sign.jpg', None, (800, 1600)),
    ('morion-statues',   'edited-images/brochure/morion-statues.jpg', None, (540,)),
    ('century-tree-b',   'edited-images/brochure/century-cliff-tree.jpg', None, (768,)),
    ('sunong-bato-b',    'edited-images/brochure/sunong-bato.jpg', None, (756,)),
    ('beach-loungers',   'viber_image_2026-10-21_08-43-10-768.jpg', MARK_L, (800, 1424)),
    ('bonfire-smores',   '749f2544-eec8-425f-98f1-c7b7e0e02762-md.jpeg', None, (800,)),
    ('maniwaya-cove',    'IMG_1188.HEIC', (0, .25, .62, .53), (800, 1300)),
    ('sandbar-boat',     'Screenshot 2025-12-20 at 12.26.39 AM.png', None, (738,)),
    ('sunset-boat-beach', 'edited-images/sunset-boat.jpg', (0, .22, .68, 1), (800, 1206)),
    # Client-labelled photos (Assets from Client/October 30, 2026)
    ('r-single-1', 'Assets from Client/October 30, 2026/room 3 single standard.jpg', MARK_L, (800, 1424)),
    ('r-single-2', 'Assets from Client/October 30, 2026/room 6, single standard.jpg', MARK_P, (640, 1100)),
    ('r-single-bath', 'Assets from Client/October 30, 2026/room 3 cr.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-1', 'Assets from Client/October 30, 2026/room 23, deluxe.jpg', MARK_L, (800, 1424)),
    ('r-deluxe-2', 'Assets from Client/October 30, 2026/23, delux.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-3', 'Assets from Client/October 30, 2026/room 28 deluxe.jpg', MARK_P, (640, 1100)),
    ('r-deluxe-bath', 'Assets from Client/October 30, 2026/23, cr.jpg', MARK_P, (640, 1100)),
    ('r-superior-1', 'Assets from Client/October 30, 2026/room 5 superior room.jpg', MARK_L, (800, 1424)),
    ('r-superior-2', 'Assets from Client/October 30, 2026/room 2, superior.jpg', MARK_L, (800, 1424)),
    ('r-superior-3', 'Assets from Client/October 30, 2026/room 5.jpg', MARK_L, (800, 1080)),
    ('r-superior-bath', 'Assets from Client/October 30, 2026/room 5 cr.jpg', MARK_P, (640, 1100)),
    ('r-suite-1', 'Assets from Client/October 30, 2026/room 1, suite.jpg', MARK_L, (800, 1424)),
    ('r-suite-2', 'Assets from Client/October 30, 2026/room 8 suite room.jpg', MARK_L, (800, 1424)),
    ('r-suite-bath', 'Assets from Client/October 30, 2026/room 1 cr.jpg', MARK_P, (640, 1100)),
    ('r-suiteloft-1', 'Assets from Client/October 30, 2026/room 25, suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-2', 'Assets from Client/October 30, 2026/room 24, suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-3', 'Assets from Client/October 30, 2026/room 26 suite loft.jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-4', 'Assets from Client/October 30, 2026/suite loft 24.jpg', MARK_L, (800, 1424)),
    ('r-loftbeds', 'Assets from Client/October 30, 2026/loft beds .jpg', MARK_L, (800, 1424)),
    ('r-suiteloft-bath', 'Assets from Client/October 30, 2026/room 24, cr.jpg', MARK_P, (640, 1100)),
    ('r-exec-1', 'Assets from Client/October 30, 2026/room 27, executive loft.jpg', MARK_P, (640, 1100)),
    ('r-exec-2', 'Assets from Client/October 30, 2026/room 27 executive loft.jpg', MARK_L, (800, 1424)),
    ('r-exec-3', 'Assets from Client/October 30, 2026/loft (every suite loft and executive).jpg', MARK_L, (800, 1424)),
    ('r-exec-bath', 'Assets from Client/October 30, 2026/room 27 cr.jpg', MARK_P, (640, 1100)),
    ('kubo-ext2', 'Assets from Client/October 30, 2026/20910854c5c0d67368b83fc7afb197a13e21c86f.jpg', None, (705,)),
    ('kubo-lounge2', 'Assets from Client/October 30, 2026/KUBO.HEIC', None, (800, 1200)),
    ('kubo-bed2', 'Assets from Client/October 30, 2026/KUBO.JPG', None, (800, 1080)),
    ('kubo-living2', 'Assets from Client/October 30, 2026/KUBO (1).JPG', None, (800, 1071)),
    ('kayak-sign', 'Assets from Client/October 30, 2026/526872481.jpg', None, (576,)),
    ('maniwaya-aerial', 'Assets from Client/October 30, 2026/Marinduque-1-edited-scaled.jpg', None, (800, 1600)),
    ('rock-cove', 'Assets from Client/October 30, 2026/rock-formation.jpg', None, (800, 1200)),
    ('snorkel2', 'Assets from Client/October 30, 2026/pexels-pixabay-163313.jpg', None, (800, 1400)),
    ('sea-rocks', 'Assets from Client/October 30, 2026/images (3).jpg', None, (554,)),
    ('snorkel3', 'Assets from Client/October 30, 2026/pexels-thomas-balabaud-735585-6507342.jpg', None, (800, 1400)),
    ('sandbar-hop', 'image (1) (1).png', None, (800, 1080)),
    ('deck-table', 'Assets from Client/October 30, 2026/203add1d0cc6e9e797221bf8adcd6392bb06b5e0.jpg', (0, 0, 1, .76), (705,)),
    ('badminton',        '69d30c820f458aa14e24c2487352050a.jpg', None, (640, 736)),
    # The Genesis Events Place
    ('genesis-hall',     'IMG_1212.HEIC', None, (800, 1200)),
    ('genesis-tables',   'IMG_1213.HEIC', None, (800, 1200)),
    ('genesis-setup',    'IMG_1216.HEIC', None, (800, 1200)),
    ('genesis-dinner',   'IMG_1225.heic', None, (800, 1200)),
    ('genesis-lawn',     'IMG_1250.heic', None, (800, 1200)),
    ('genesis-front',    'IMG_1249.heic', None, (800, 1200)),
    # Dining
    ('skylight',         'viber_image_2026-10-20_16-40-23-113.jpg', MARK_L, (800, 1424)),
    ('skylight-2',       'viber_image_2026-10-20_16-40-23-429.jpg', MARK_L, (800, 1424)),
    # November 2 client photos
    ('n-beach-sports', f'{N2}/02_beach_and_water_sports_full_original_ratio.jpg', None, (800, 1400)),
    ('n-breakfast', f'{N2}/01_beachfront_breakfast_full_original_ratio.jpg', None, (640, 1200)),
    ('n-breakfast-brand', f'{N2}/03_resort_breakfast_and_branding_portrait.jpg', None, (640, 1024)),
    ('n-boodle-p', f'{N2}/04_boodle_feast_portrait.jpg', None, (640, 1024)),
    ('n-seafood-p', f'{N2}/03_seafood_feast_portrait.jpg', None, (640, 1024)),
    ('n-watermelon-p', f'{N2}/05_watermelon_beach_portrait.jpg', None, (640, 1024)),
    ('n-longtable', f'{N2}/05_outdoor_dining_portrait.jpg', None, (640, 1024)),
    ('n-dive-shop', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_26 PM-9.png', None, (800, 1448)),
    ('n-dive-gear', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_19 PM-5.png', None, (800, 1448)),
    ('n-hall-floral', f'{N2}/04_event_hall_floral_tables_full_original_ratio.jpg', None, (640, 1200)),
    ('n-hall-round', f'{N2}/01_event_hall_landscape.jpg', None, (800, 1400)),
    ('n-celebrate-w', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_12 PM-1.png', None, (800, 1448)),
    ('n-celebrate-p', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_15 PM-2.png', None, (640, 1122)),
    ('n-cake', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_17 PM-3.png', None, (800, 1448)),
    ('n-coconut', f'{N2}/WhatsApp Image 2026-11-02 at 8.47.23 AM (2).jpeg', None, (800, 1400)),
    ('n-tower-sunset-w', f'{N2}/ChatGPT Image Nov 2, 2026, 01_16_26 PM-4.png', None, (800, 1400)),
    ('n-tower-sunset-p', f'{N2}/ChatGPT Image Nov 2, 2026, 01_16_25 PM-3.png', None, (640, 1122)),
    ('n-sunset-sea', f'{N2}/03_sunset_landscape.jpg', None, (800, 1400)),
    ('n-sandbar', f'{N2}/02_sandbar_landscape.jpg', None, (800, 1400)),
    ('n-rock-arch', f'{N2}/02_rock_arch_landscape.jpg', None, (800, 1400)),
    ('n-beach-sports-p', f'{N2}/02_beach_and_water_sports_full_original_ratio.jpg', None, (640, 1200)),
    ('darts-terrace-d', 'Assets from Client/Dart poised before the dartboard.png', (.143, .107, .827, .791), (800, 1050)),
    ('n5-anemone-w', f'{N5}/Four Fish Beside a Sea Anemone-2.png', None, (800, 1400)),
    ('n5-anemone-p', f'{N5}/Anemone with Four Reef Fish-5.png', None, (640, 1086)),
    ('n5-dog-w', f'{N5}/Bulldog by the ocean at dusk-8.png', None, (800, 1400)),
    ('n5-dog-p', f'{N5}/Bulldog by the Evening Ocean-7.png', None, (640, 1086)),
    ('n5-birds-w', f'{N5}/Two Birds with Prey-6.png', None, (800, 1400)),
    ('n5-birds-p', f'{N5}/Two birds perched with prey-1.png', None, (640, 1086)),
    ('n5-nest-w', f'{N5}/Three nestlings in a woven nest-4.png', None, (640, 1086)),
    ('n5-nest-p', f'{N5}/Three hungry nestlings in a woven nest-3.png', None, (640, 1086)),
    ('n7-banana-c', 'edited-images/v5/n7-beach-clean.png', (95/1672, 12/941, 1185/1672, 1), (640, 1090)),
    ('n7-clown', f'{N7}/WhatsApp Image 2026-11-07 at 10.55.28 AM.jpeg', None, (800, 1400)),
    ('n7-chow-p', f'{N7}/Fluffy Chow Chow by the Sea-2.png', None, (640, 1122)),
    ('n7-chow-w', f'{N7}/Fluffy Chow Chow by the Sea-3.png', None, (800, 1400)),
    ('n7-beach-p', f'{N7}/Beach Resort With Kayaks and Banana Boat-8.png', None, (640, 1122)),
    ('n7-bikes-p', f'{N7}/Resort corridor with wall-mounted bicycles-5.png', None, (640, 1122)),
    ('n7-dog-w', f'{N7}/Pale dog on a beach-3.png', None, (800, 1400)),
    ('n7-dog-p', f'{N7}/Pale dog on a tropical beach-6.png', None, (640, 1122)),
    ('n7-stage', f'{N7}/Empty stage with geometric wall-1.png', None, (800, 1400)),
    ('n-kayak-w', f'{N2}/ChatGPT Image Nov 2, 2026, 01_16_40 PM-10.png', None, (800, 1400)),
    ('n-kayak-p', f'{N2}/ChatGPT Image Nov 2, 2026, 01_16_38 PM-9.png', None, (640, 1122)),
    ('n-dive-shop-p', f'{N2}/ChatGPT Image Nov 2, 2026, 01_55_27 PM-10.png', None, (640, 1122)),
    ('kubo-bed3', 'IMG_2174.HEIC', None, (800, 1200)),
    ('r-exec-5', 'viber_image_2026-10-20_17-16-02-324.jpg', MARK_L, (800, 1424)),
    ('n-rocky-coast', f'{N2}/05_rocky_coast_landscape.jpg', None, (800, 1400)),
    ('n-picnic', f'{N2}/ChatGPT Image Nov 2, 2026, 01_50_32 PM-2.png', None, (800, 1400)),
    ('n-palm-lawn', f'{N2}/ChatGPT Image Nov 2, 2026, 01_50_38 PM-6.png', None, (800, 1400)),
]

def load(name):
    path = os.path.join(ROOT, *name.split('/')) if ('/' in name) else os.path.join(NEW, name)
    if not os.path.exists(path):  # some filenames contain a narrow no-break space
        key = name.replace(' ', '').lower()
        match = [f for f in os.listdir(NEW) if f.replace(' ', '').replace(' ', '').lower() == key]
        path = os.path.join(NEW, match[0])
    if name.lower().endswith('.heic'):
        tmp = os.path.join(tempfile.gettempdir(), 'v5_heic.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-frames:v', '1', tmp], check=True)
        return Image.open(tmp).convert('RGB')
    return ImageOps.exif_transpose(Image.open(path)).convert('RGB')

manifest = []
PREV = {}
if os.path.exists(os.path.join(OUT, 'manifest.txt')):
    for line in open(os.path.join(OUT, 'manifest.txt'), encoding='utf-8').read().splitlines():
        parts = line.split('|')
        if len(parts) == 3:
            PREV[parts[0]] = (parts[1], parts[2])
for jid, src, crop, widths in JOBS:
    # Skip jobs already built from the same source (a changed crop needs a new id)
    done = PREV.get(jid)
    if done and done[1] == src and all(os.path.exists(os.path.join(OUT, f'{jid}-{s.split("x")[0]}.webp')) for s in done[0].split()):
        manifest.append(f'{jid}|{done[0]}|{src}')
        continue
    im = load(src)
    W, H = im.size
    if crop:
        l, t, r, b = crop
        im = im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))
        im.save(os.path.join(CLEAN, jid + '.jpg'), quality=92)
    sizes = []
    for w in widths:
        w = min(w, im.width)
        h = round(im.height * w / im.width)
        r = im.resize((w, h), Image.LANCZOS)
        r.save(os.path.join(OUT, f'{jid}-{w}.jpg'), quality=80, optimize=True, progressive=True)
        r.save(os.path.join(OUT, f'{jid}-{w}.webp'), quality=78, method=5)
        sizes.append(f'{w}x{h}')
    manifest.append(f'{jid}|{" ".join(sizes)}|{src}')
with open(os.path.join(OUT, 'manifest.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(manifest) + '\n')
print(len(manifest), 'images')
