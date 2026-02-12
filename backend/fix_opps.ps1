$path = "C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend\app\routers\opportunities.py"
$content = Get-Content $path
# Lines to keep: 1..401 (indices 0..400) and 455..end (indices 454..end)
# Removing lines 402..454 (indices 401..453)
$newContent = $content[0..400] + $content[454..($content.Length-1)]
$newContent | Set-Content $path -Encoding UTF8
Write-Output "Fixed opportunities.py"
