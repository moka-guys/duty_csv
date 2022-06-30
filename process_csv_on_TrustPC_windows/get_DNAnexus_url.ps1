# Works like wget, pass URLs to script to download them to destination folder each argument is a sting containing source path and destination separated by comma
# dl_urls.ps1 url [url path]
Import-Module BitsTransfer
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip
{
    param([string]$zipfile, [string]$outpath)
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}
foreach ($url in $args) 
{
$array =$url.Split(",") 
$path = $array[0]
$output = $array[1]
Write-Output "Downloading $path to $output"
Start-BitsTransfer -Source $path -Destination $output
if ($path.Contains("/Results.zip")) {
    $filetoextract=$output+"\Results.zip"
    $extactpath=$output+"\Results"
    Unzip $filetoextract $extractpath
    Remove-Item $filetoextract
}
}