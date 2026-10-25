$ErrorActionPreference = 'Stop'
$reportPath = Join-Path $PSScriptRoot 'MMA3001_suspension_report_draft.docx'
$renderDirectory = Join-Path $PSScriptRoot 'rendered'
New-Item -ItemType Directory -Path $renderDirectory -Force | Out-Null
$pdfPath = Join-Path $renderDirectory 'MMA3001_suspension_report_draft.pdf'
$word = $null
$report = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $report = $word.Documents.Open($reportPath, $false, $false)
    $report.Fields.Update() | Out-Null
    $report.Repaginate()
    $pageCount = $report.ComputeStatistics(2)
    $report.Save()
    $report.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "Rendered pages: $pageCount"
    Write-Output $pdfPath
}
finally {
    if ($null -ne $report) { $report.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
