# Creates optimized, responsive JPEG derivatives in assets/img from "Initial Images".
# Originals are never modified. Crops listed here only remove baked-in text, watermarks and
# the white inset frame lines from the resort's social posts,
# or extract a room photo from the resort's own dated rate sheets.
# Run from the project root:  powershell -ExecutionPolicy Bypass -File _tools/build-images.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Add-Type -AssemblyName System.Drawing
if (-not ('ImageTools' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'ImageTools.cs') -ReferencedAssemblies System.Drawing }

$in  = Join-Path $root 'Initial Images'
$out = Join-Path $root 'assets\img'
New-Item -ItemType Directory -Force $out | Out-Null
# Full-resolution cleaned copies (overlays removed by cropping) for reuse and review.
$clean = Join-Path $root 'edited-images'
New-Item -ItemType Directory -Force $clean | Out-Null

# id | source file (prefix) | crop x,y,w,h ('' = none) | widths
$jobs = @(
  # Hero slideshow
  'hero-aerial|468962364||800'
  'hero-dusk-pool|480668276|0,0,1536,1880|720,1100,1536'
  'pool-grounds-day|480789432||720,1100,1600'
  'beach-outrigger|480677027||720,1100,1290'
  'night-facade|469778213||720,1100,1600'
  'bamboo-raft|481042792||720,1100,1200'
  'beach-dusk-tower|844278644||720,1100,1320'
  'night-pool-building|480819549|600,0,1000,1050|720,1000'
  'sign-dusk|480669228||720,1200'
  # Rooms: photos taken from the resort's rate sheets (effective 15 Feb 2026)
  'room-single-standard|634704403|580,262,570,404|570'
  'room-double-standard|634704403|580,674,570,364|570'
  'room-deluxe|634704403|580,1046,570,392|570'
  'room-superior|636649353|0,286,520,368|520'
  'room-suite|636649353|0,661,520,398|520'
  'room-executive-loft-sheet|635305335|562,262,588,406|588'
  'room-pool-suite|635305335|562,1036,588,402|588'
  # Rooms: standalone photographs
  'suite-loft-room|469693827|72,64,936,856|560,936'
  'executive-loft-room|469682649|72,64,936,856|560,936'
  'loft-single-beds|469731082|72,64,936,856|560,936'
  'kubo-exterior|469412982|72,64,936,856|560,936'
  'kubo-interior-loft|475776678|72,64,936,856|560,936'
  'kubo-lounge|476108318|72,64,936,856|560,936'
  'kubo-night-lounge|469793924|72,64,936,856|560,936'
  'double-bed-room|469848103|72,64,936,856|560,936'
  'bathroom-glass-shower|469886797|72,64,936,856|560,936'
  # Grounds, beach, dining
  'beach-sunset-path|468160939||560,900,1200'
  'garden-path-beach|469314100|72,64,936,856|560,936'
  'kubo-distant-palms|469824427|72,64,936,856|560,936'
  'campsite-tents|469518456|72,64,936,856|560,936'
  'bonfire-circle|475815964|72,64,936,856|560,936'
  'bonfire-night|469399386|372,62,638,954|560,638'
  'beach-volleyball|469315209|72,63,1774,837|720,1400,1774'
  'sunset-boat|469439934|72,63,1774,837|720,1400'
  'palms-bike|469419844|72,63,1774,837|720,1400'
  'dining-veranda-night|469677365|72,64,936,856|560,936'
  'dining-table|469677365|72,320,600,600|600'
  'pingpong-veranda|469802942|72,64,936,856|560,936'
  'deck-dining|475846753|72,64,936,856|560,936'
  'kitchen|476082802|72,185,936,827|560,936'
  # Nearby destinations (not resort grounds)
  'palad-sandbar|280550992|0,180,940,608|720,940'
  'ungab-rock-cove|469585919|0,0,940,596|720,940'
  'sunong-bato|469676281|0,200,940,588|720,940'
  'century-tree|471282341|0,0,940,600|720,940'
  'morion-reef|283639303|0,140,940,648|720,940'
  'maniwaya-map|476633415||760,1528'
  # From "Assets from Client" (Oct 2026): real boat and raft photos cropped out of the resort's graphics
  'boat-rogelius|IMG_5191|42,350,401,402|401'
  'boat-st-longinus|IMG_5191|519,350,401,402|401'
  'boat-omon-express|IMG_5191|996,350,401,402|401'
  'morion-reef-raft|IMG_5193|610,1075,365,270|365'
  # Activity photos from the client's "Paid amenities & activities" sheet (IMG_5180)
  'act-bikes|IMG_5180|114,232,229,218|229'
  'act-kayak|IMG_5180|424,232,229,218|229'
  'act-ecart|IMG_5180|732,232,229,218|229'
  'act-karaoke|IMG_5180|114,555,229,218|229'
  'act-massage|IMG_5180|424,555,229,218|229'
  'act-laundry|IMG_5180|114,877,229,219|229'
  'act-snorkel|IMG_5180|424,877,229,219|229'
  # The resort's rental van (frame and logo cropped out)
  'van|469332244|400,64,1446,926|720,1100'
  # Illustrative activity photos supplied by the client (Pexels, Initial Images/Activities)
  'exp-kayak|pexels-efrem||800,1400'
  'exp-bike|pexels-enrico||700,1200'
  'exp-snorkel|pexels-jess||700,1200'
  'exp-karaoke|pexels-karla||800,1400'
  'exp-laundry|pexels-tima-miroshnichenko-8774531||800,1400'
  'exp-massage|pexels-tommaso||800,1400'
  # The resort's own guides and menus, shown whole in the lightbox (no crop)
  'guide-commute|IMG_5188||1073'
  'guide-drive|IMG_5189||1143'
)

$files = @(Get-ChildItem $in -File) + @(Get-ChildItem (Join-Path $root 'Assets from Client') -File) + @(Get-ChildItem (Join-Path $in 'Activities') -File)
foreach ($j in $jobs) {
  $id, $prefix, $crop, $widths = $j.Split('|')
  $file = $files | Where-Object { $_.Name.StartsWith($prefix) } | Select-Object -First 1
  if (-not $file) { throw "Missing source for $id ($prefix)" }
  if ($crop) { $c = $crop.Split(',') | ForEach-Object { [int]$_ } } else { $c = 0,0,0,0 }
  $bmp = [ImageTools]::Load($file.FullName, $c[0], $c[1], $c[2], $c[3])
  if ($crop) { [ImageTools]::SaveJpeg($bmp, (Join-Path $clean "$id.jpg"), $bmp.Width, 92) | Out-Null }
  $sizes = foreach ($w in $widths.Split(',')) {
    [ImageTools]::SaveJpeg($bmp, (Join-Path $out "$id-$w.jpg"), [int]$w, 80)
  }
  "{0,-28} {1}  <- {2}" -f $id, ($sizes -join ' '), $file.Name
  $bmp.Dispose()
}
