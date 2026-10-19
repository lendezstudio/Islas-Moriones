# Minimal Chrome DevTools Protocol helper for visual QA (dot-source this file).
#   . _tools/cdp.ps1
#   Start-Cdp; Set-Viewport 390 844 3 $true; Open-Page "file:///.../index.html"
#   Save-Shot "out.png"; Invoke-Js "document.title"; Stop-Cdp
$ErrorActionPreference = 'Stop'
$script:chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$script:id = 0
$script:events = New-Object System.Collections.ArrayList

function Start-Cdp([int]$port = 9333) {
  $script:profileDir = Join-Path $env:TEMP ('cdp-profile-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
  $script:proc = Start-Process $script:chrome -ArgumentList @('--headless=new', "--remote-debugging-port=$port", "--user-data-dir=$($script:profileDir)",
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--disable-gpu', '--allow-file-access-from-files', 'about:blank') -PassThru
  $targets = $null
  for ($i = 0; $i -lt 50 -and -not $targets; $i++) {
    Start-Sleep -Milliseconds 200
    try { $targets = Invoke-RestMethod "http://127.0.0.1:$port/json" } catch {}
  }
  $page = $targets | Where-Object { $_.type -eq 'page' } | Select-Object -First 1
  $script:ws = New-Object System.Net.WebSockets.ClientWebSocket
  $script:ws.Options.KeepAliveInterval = [TimeSpan]::FromSeconds(30)
  $script:ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  Send-Cdp 'Page.enable' | Out-Null
  Send-Cdp 'Runtime.enable' | Out-Null
  Send-Cdp 'Log.enable' | Out-Null
}

function Receive-Msg {
  $buffer = New-Object byte[] 1048576
  $ms = New-Object System.IO.MemoryStream
  do {
    $seg = New-Object System.ArraySegment[byte] -ArgumentList (, $buffer)
    $res = $script:ws.ReceiveAsync($seg, [Threading.CancellationToken]::None).Result
    $ms.Write($buffer, 0, $res.Count)
  } while (-not $res.EndOfMessage)
  [Text.Encoding]::UTF8.GetString($ms.ToArray()) | ConvertFrom-Json
}

function Send-Cdp([string]$method, $params = @{}) {
  $script:id++
  $msg = @{ id = $script:id; method = $method; params = $params } | ConvertTo-Json -Depth 20 -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList (, $bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  while ($true) {
    $r = Receive-Msg
    if ($r.id -eq $script:id) {
      if ($r.error) { throw "CDP $method failed: $($r.error.message)" }
      return $r.result
    }
    if ($r.method) { [void]$script:events.Add($r) }
  }
}

function Set-Viewport([int]$w, [int]$h, [double]$dpr = 1, [bool]$mobile = $false) {
  Send-Cdp 'Emulation.setDeviceMetricsOverride' @{ width = $w; height = $h; deviceScaleFactor = $dpr; mobile = $mobile } | Out-Null
  Send-Cdp 'Emulation.setTouchEmulationEnabled' @{ enabled = $mobile; maxTouchPoints = $(if ($mobile) { 5 } else { 1 }) } | Out-Null
}

function Set-ReducedMotion([bool]$on) {
  $v = $(if ($on) { 'reduce' } else { 'no-preference' })
  Send-Cdp 'Emulation.setEmulatedMedia' @{ features = @(@{ name = 'prefers-reduced-motion'; value = $v }) } | Out-Null
}

function Open-Page([string]$url, [int]$settleMs = 1500) {
  Send-Cdp 'Page.navigate' @{ url = $url } | Out-Null
  for ($i = 0; $i -lt 100; $i++) {
    Start-Sleep -Milliseconds 100
    if ((Invoke-Js 'document.readyState') -eq 'complete') { break }
  }
  Start-Sleep -Milliseconds $settleMs
}

function Invoke-Js([string]$expr, [bool]$await = $false) {
  $r = Send-Cdp 'Runtime.evaluate' @{ expression = $expr; returnByValue = $true; awaitPromise = $await }
  if ($r.exceptionDetails) { return "JS-ERROR: " + $r.exceptionDetails.exception.description }
  return $r.result.value
}

function Save-Shot([string]$path, [switch]$full) {
  $p = @{ format = 'png' }
  if ($full) {
    $m = Send-Cdp 'Page.getLayoutMetrics'
    $p.captureBeyondViewport = $true
    $p.clip = @{ x = 0; y = 0; width = $m.cssContentSize.width; height = $m.cssContentSize.height; scale = 1 }
  }
  $r = Send-Cdp 'Page.captureScreenshot' $p
  [IO.File]::WriteAllBytes($path, [Convert]::FromBase64String($r.data))
}

function Get-ConsoleProblems {
  $script:events | Where-Object {
    ($_.method -eq 'Runtime.exceptionThrown') -or
    ($_.method -eq 'Log.entryAdded' -and $_.params.entry.level -in @('error', 'warning')) -or
    ($_.method -eq 'Runtime.consoleAPICalled' -and $_.params.type -in @('error', 'warning'))
  } | ForEach-Object {
    if ($_.method -eq 'Runtime.exceptionThrown') { 'EXCEPTION: ' + $_.params.exceptionDetails.exception.description }
    elseif ($_.method -eq 'Log.entryAdded') { 'LOG ' + $_.params.entry.level + ': ' + $_.params.entry.text + ' ' + $_.params.entry.url }
    else { 'CONSOLE ' + $_.params.type + ': ' + (($_.params.args | ForEach-Object { $_.value }) -join ' ') }
  }
}

function Stop-Cdp {
  try { $script:ws.Dispose() } catch {}
  # Only stop processes that belong to this session's temporary profile.
  $tag = Split-Path $script:profileDir -Leaf
  Get-CimInstance Win32_Process -Filter "Name = 'chrome.exe'" | Where-Object { $_.CommandLine -like "*$tag*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}
