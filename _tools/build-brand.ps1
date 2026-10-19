# Builds logo, favicon and share-image derivatives from "Initial Images/Logo.jpg".
# The original logo file is never modified.
# Run from the project root:  powershell -ExecutionPolicy Bypass -File _tools/build-brand.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'ImageTools.cs') -ReferencedAssemblies System.Drawing

$src = Join-Path $root 'Initial Images\Logo.jpg'
$out = Join-Path $root 'assets\brand'
New-Item -ItemType Directory -Force $out | Out-Null

$full = [ImageTools]::Load($src, 0, 0, 0, 0)
$box = [ImageTools]::ContentBox($full, 24)
"Logo content box: $box"

# Trim surrounding white space only (the logo artwork itself is not cropped).
$pad = 6
$trim = New-Object System.Drawing.Rectangle ($box.X - $pad), ($box.Y - $pad), ($box.Width + 2*$pad), ($box.Height + 2*$pad)
$alpha = [ImageTools]::WhiteToAlpha($full)
$logo = [ImageTools]::CropArgb($alpha, $trim)
[ImageTools]::SavePngScaled($logo, (Join-Path $out 'logo-islas-moriones.png'), [Math]::Min(760, $logo.Width))
[ImageTools]::SavePngScaled($logo, (Join-Path $out 'logo-islas-moriones-380.png'), 380)

# Mark only (palms + roof): rows above the first text row. Detect the gap between mark and wordmark.
$markBottom = $box.Y
for ($y = $box.Y; $y -lt $box.Bottom; $y++) {
  $ink = $false
  for ($x = $box.X; $x -lt $box.Right; $x += 2) { $c = $full.GetPixel($x, $y); if ((255 - [Math]::Min($c.R, [Math]::Min($c.G, $c.B))) -gt 40) { $ink = $true; break } }
  if ($ink) { $markBottom = $y } elseif ($y - $box.Y -gt 20) { break }
}
"Mark rows: $($box.Y)..$markBottom"
$markRow = New-Object System.Drawing.Rectangle $box.X, $box.Y, $box.Width, ($markBottom - $box.Y + 1)
$markStrip = [ImageTools]::CropArgb($full, $markRow)
$mb = [ImageTools]::ContentBox($markStrip, 24)
$markRect = New-Object System.Drawing.Rectangle ($box.X + $mb.X - 4), ($box.Y + $mb.Y - 4), ($mb.Width + 8), ($mb.Height + 8)
"Mark box: $markRect"
$mark = [ImageTools]::CropArgb($alpha, $markRect)
[ImageTools]::SavePngScaled($mark, (Join-Path $out 'logo-mark.png'), [Math]::Min(512, $mark.Width))

$ivory = [System.Drawing.Color]::FromArgb(0xEE, 0xE8, 0xDA)
[ImageTools]::SaveIcon($mark, (Join-Path $root 'favicon-32.png'), 32, $ivory, 0.08, $true)
[ImageTools]::SaveIcon($mark, (Join-Path $root 'favicon-192.png'), 192, $ivory, 0.12, $true)
[ImageTools]::SaveIcon($mark, (Join-Path $root 'apple-touch-icon.png'), 180, $ivory, 0.14, $false)

# Sharing preview: dusk pool photo (building, pool and palms) + full logo on ivory.
$photo = Join-Path $root 'edited-images\hero-dusk-pool.jpg'   # cleaned copy (watermark removed); run build-images.ps1 first
$crop = New-Object System.Drawing.Rectangle 0, 300, 1536, 1382
[ImageTools]::SaveShareImage($photo, $crop, $logo, (Join-Path $root 'assets\img\share-preview.jpg'))
"brand assets done"

# Simplified 32px favicon: the central gable of the official mark (the full mark is too wide
# to stay legible at tab size). Separate asset; the original logo is untouched.
$gable = New-Object System.Drawing.Rectangle ($markRect.X + 144), $markRect.Y, 164, $markRect.Height
$gableMark = [ImageTools]::CropArgb($alpha, $gable)
[ImageTools]::SavePngScaled($gableMark, (Join-Path $out 'favicon-gable-source.png'), 164)
[ImageTools]::SaveIcon($gableMark, (Join-Path $root 'favicon-32.png'), 32, $ivory, 0.06, $true)
[ImageTools]::SaveIcon($gableMark, (Join-Path $root 'favicon-48.png'), 48, $ivory, 0.08, $true)
"favicon done"
