# Manager-only full run. No execution is performed by the build lane.
$archiveRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $archiveRoot
$env:R_ENVIRON_USER = 'NUL'
# No package library is hard-coded here. Set R_LIBS_USER (and R_LIBS if needed) before
# running when the paper's R 4.6.0 / metafor 5.2.1 packages are not on R's own default
# path; whatever is inherited is used as is. v2/pins.R gates the exact versions and fails
# closed, so a library without them cannot pass.
$env:OPENBLAS_NUM_THREADS = '1'
$env:LC_ALL = 'C'
Remove-Item Env:INFLUENCE_V2_ONLY -ErrorAction SilentlyContinue
$rscriptPath = 'C:\Program Files\R\R-4.6.0\bin\Rscript.exe'
$started = [DateTime]::UtcNow.ToString('o')
$state = [ordered]@{command='Rscript validate.R'; started_utc=$started; ended_utc=$null; exit_code=$null; status='running'}
$state | ConvertTo-Json | Set-Content -LiteralPath 'validate_full_run.json' -Encoding UTF8
$runExit = 1
try {
    & $rscriptPath validate.R *> validate_full.log
    $runExit = $LASTEXITCODE
} catch {
    $_ | Out-String | Add-Content -LiteralPath 'validate_full.log'
} finally {
    $state.ended_utc = [DateTime]::UtcNow.ToString('o')
    $state.exit_code = $runExit
    $state.status = if ($runExit -eq 0) {'completed'} else {'failed'}
    $state | ConvertTo-Json | Set-Content -LiteralPath 'validate_full_run.json' -Encoding UTF8
}
exit $runExit
