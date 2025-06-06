# PowerShell Script for CSV File Processing with UI
# Requires: Windows Forms (built-in)

# Import required modules
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Global variables
$script:CSVData = @()
$script:ProcessingResults = @()

# Method to read CSV file and extract data
function Read-CSVData {
    param([string]$FilePath)
    
    try {
        $data = Import-Csv -Path $FilePath
        $script:CSVData = $data | Select-Object "Source File path", "Target File Path", "TCIN"
        return $true
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show("Error reading CSV file: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
}

# Method to update results grid with proper formatting
function Update-ResultsGrid {
    $dataGridView.Rows.Clear()
    $dataGridView.Columns.Clear()
    
    # Add columns
    $dataGridView.Columns.Add("Row", "Row #") | Out-Null
    $dataGridView.Columns.Add("TCIN", "TCIN") | Out-Null
    $dataGridView.Columns.Add("Status", "Status") | Out-Null
    $dataGridView.Columns.Add("TexturingFound", "Texturing Found") | Out-Null
    $dataGridView.Columns.Add("SourceTCINMatches", "Source TCIN Match") | Out-Null
    $dataGridView.Columns.Add("TargetTCINMatches", "Target TCIN Match") | Out-Null
    $dataGridView.Columns.Add("SourceFolder", "Source Last Folder") | Out-Null
    $dataGridView.Columns.Add("TargetFolder", "Target Last Folder") | Out-Null
    
    # Set column widths
    $dataGridView.Columns["Row"].Width = 50
    $dataGridView.Columns["TCIN"].Width = 70
    $dataGridView.Columns["Status"].Width = 250
    $dataGridView.Columns["TexturingFound"].Width = 80
    $dataGridView.Columns["SourceTCINMatches"].Width = 90
    $dataGridView.Columns["TargetTCINMatches"].Width = 90
    $dataGridView.Columns["SourceFolder"].Width = 110
    $dataGridView.Columns["TargetFolder"].Width = 110
    
    # Add rows
    foreach ($result in $script:ProcessingResults) {
        $rowIndex = $dataGridView.Rows.Add()
        $row = $dataGridView.Rows[$rowIndex]
        
        $row.Cells["Row"].Value = $result.Row
        $row.Cells["TCIN"].Value = $result.TCIN
        $row.Cells["Status"].Value = $result.Status
        $row.Cells["TexturingFound"].Value = if ($result.TexturingFolderFound) { "Yes" } else { "No" }
        $row.Cells["SourceTCINMatches"].Value = if ($result.SourceTCINMatches) { "Yes" } else { "No" }
        $row.Cells["TargetTCINMatches"].Value = if ($result.TargetTCINMatches) { "Yes" } else { "No" }
        $row.Cells["SourceFolder"].Value = $result.SourceLastFolder
        $row.Cells["TargetFolder"].Value = $result.TargetLastFolder
        
        # Color code rows based on status
        if ($result.Status.StartsWith("SUCCESS")) {
            $row.DefaultCellStyle.BackColor = [System.Drawing.Color]::LightGreen
        }
        elseif ($result.Status.StartsWith("WARNING")) {
            $row.DefaultCellStyle.BackColor = [System.Drawing.Color]::LightYellow
        }
        elseif ($result.Status.StartsWith("ERROR")) {
            $row.DefaultCellStyle.BackColor = [System.Drawing.Color]::LightCoral
        }
    }
    
    $dataGridView.Refresh()
}

# Method to process folders and verify TCIN matching
function Process-FoldersAndVerifyTCIN {
    param($ProgressBar, $StatusLabel)
    
    $script:ProcessingResults = @()
    $totalRows = $script:CSVData.Count
    
    for ($i = 0; $i -lt $totalRows; $i++) {
        $row = $script:CSVData[$i]
        $sourcePath = $row."Source File path"
        $targetPath = $row."Target File Path"
        $tcin = $row."TCIN"
        
        # Update progress
        $percentage = [math]::Round(($i / $totalRows) * 100)
        $ProgressBar.Value = $percentage
        $StatusLabel.Text = "Processing row $($i + 1) of $totalRows - TCIN: $tcin"
        [System.Windows.Forms.Application]::DoEvents()
        
        $result = @{
            Row = $i + 1
            TCIN = $tcin
            SourcePath = $sourcePath
            TargetPath = $targetPath
            TexturingFolderFound = $false
            SourceTCINMatches = $false
            TargetTCINMatches = $false
            SourceLastFolder = ""
            TargetLastFolder = ""
            Status = ""
            Error = ""
        }
        
        try {
            # Check if source path exists and find "Texturing" folder
            if (Test-Path $sourcePath) {
                # Get the last folder name from source path
                $sourceLastFolder = Split-Path $sourcePath -Leaf
                $result.SourceLastFolder = $sourceLastFolder
                
                # Verify if source path's last folder matches TCIN
                if ($sourceLastFolder -eq $tcin) {
                    $result.SourceTCINMatches = $true
                } else {
                    $result.SourceTCINMatches = $false
                }
                
                $texturingPath = Join-Path $sourcePath "Texturing"
                if (Test-Path $texturingPath) {
                    $result.TexturingFolderFound = $true
                    
                    # Get the last folder name from target path
                    $targetLastFolder = Split-Path $targetPath -Leaf
                    $result.TargetLastFolder = $targetLastFolder
                    
                    # Verify if target path's last folder matches TCIN
                    if ($targetLastFolder -eq $tcin) {
                        $result.TargetTCINMatches = $true
                    } else {
                        $result.TargetTCINMatches = $false
                    }
                    
                    # Determine overall status based on both source and target verification
                    if ($result.SourceTCINMatches -and $result.TargetTCINMatches) {
                        $result.Status = "SUCCESS: Both source and target folder names match TCIN"
                        
                        # Copy Texturing folder to target path if it doesn't exist
                        $targetTexturingPath = Join-Path $targetPath "Texturing"
                        if (-not (Test-Path $targetTexturingPath)) {
                            Copy-Item -Path $texturingPath -Destination $targetPath -Recurse -Force
                            $result.Status += " - Texturing folder copied"
                        } else {
                            $result.Status += " - Texturing folder already exists"
                        }
                    }
                    elseif ($result.SourceTCINMatches -and -not $result.TargetTCINMatches) {
                        $result.Status = "WARNING: Source matches TCIN ($tcin) but target folder name ($targetLastFolder) does not match"
                    }
                    elseif (-not $result.SourceTCINMatches -and $result.TargetTCINMatches) {
                        $result.Status = "WARNING: Target matches TCIN ($tcin) but source folder name ($sourceLastFolder) does not match"
                    }
                    else {
                        $result.Status = "ERROR: Neither source ($sourceLastFolder) nor target ($targetLastFolder) folder names match TCIN ($tcin)"
                    }
                } else {
                    if ($result.SourceTCINMatches) {
                        $result.Status = "WARNING: Source folder name matches TCIN but Texturing folder not found in source path"
                    } else {
                        $result.Status = "ERROR: Source folder name ($sourceLastFolder) does not match TCIN ($tcin) and Texturing folder not found"
                    }
                }
            } else {
                $result.Status = "ERROR: Source path does not exist"
            }
        }
        catch {
            $result.Error = $_.Exception.Message
            $result.Status = "ERROR: $($_.Exception.Message)"
        }
        
        $script:ProcessingResults += $result
    }
    
    # Complete progress
    $ProgressBar.Value = 100
    $StatusLabel.Text = "Processing completed!"
}

# Create the main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "CSV File Processor - TCIN Verification"
$form.Size = New-Object System.Drawing.Size(800, 600)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# CSV file selection group
$groupBox1 = New-Object System.Windows.Forms.GroupBox
$groupBox1.Location = New-Object System.Drawing.Point(20, 20)
$groupBox1.Size = New-Object System.Drawing.Size(740, 80)
$groupBox1.Text = "CSV File Selection"

# CSV file path textbox
$textBoxCSVPath = New-Object System.Windows.Forms.TextBox
$textBoxCSVPath.Location = New-Object System.Drawing.Point(20, 30)
$textBoxCSVPath.Size = New-Object System.Drawing.Size(500, 23)
$textBoxCSVPath.ReadOnly = $true

# Browse button
$buttonBrowse = New-Object System.Windows.Forms.Button
$buttonBrowse.Location = New-Object System.Drawing.Point(540, 30)
$buttonBrowse.Size = New-Object System.Drawing.Size(80, 23)
$buttonBrowse.Text = "Browse..."
$buttonBrowse.UseVisualStyleBackColor = $true

# Process button
$buttonProcess = New-Object System.Windows.Forms.Button
$buttonProcess.Location = New-Object System.Drawing.Point(640, 30)
$buttonProcess.Size = New-Object System.Drawing.Size(80, 23)
$buttonProcess.Text = "Process"
$buttonProcess.UseVisualStyleBackColor = $true
$buttonProcess.Enabled = $false

# Progress group
$groupBox2 = New-Object System.Windows.Forms.GroupBox
$groupBox2.Location = New-Object System.Drawing.Point(20, 120)
$groupBox2.Size = New-Object System.Drawing.Size(740, 100)
$groupBox2.Text = "Progress"

# Progress bar
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20, 30)
$progressBar.Size = New-Object System.Drawing.Size(700, 25)
$progressBar.Minimum = 0
$progressBar.Maximum = 100
$progressBar.Value = 0

# Status label
$labelStatus = New-Object System.Windows.Forms.Label
$labelStatus.Location = New-Object System.Drawing.Point(20, 65)
$labelStatus.Size = New-Object System.Drawing.Size(700, 23)
$labelStatus.Text = "Ready to process..."

# Results group
$groupBox3 = New-Object System.Windows.Forms.GroupBox
$groupBox3.Location = New-Object System.Drawing.Point(20, 240)
$groupBox3.Size = New-Object System.Drawing.Size(740, 300)
$groupBox3.Text = "Processing Results"

# Results DataGridView
$dataGridView = New-Object System.Windows.Forms.DataGridView
$dataGridView.Location = New-Object System.Drawing.Point(20, 30)
$dataGridView.Size = New-Object System.Drawing.Size(700, 220)
$dataGridView.AllowUserToAddRows = $false
$dataGridView.AllowUserToDeleteRows = $false
$dataGridView.ReadOnly = $true
$dataGridView.AutoSizeColumnsMode = "AllCells"
$dataGridView.SelectionMode = "FullRowSelect"
$dataGridView.MultiSelect = $false

# Export results button
$buttonExport = New-Object System.Windows.Forms.Button
$buttonExport.Location = New-Object System.Drawing.Point(20, 260)
$buttonExport.Size = New-Object System.Drawing.Size(120, 25)
$buttonExport.Text = "Export Results"
$buttonExport.UseVisualStyleBackColor = $true
$buttonExport.Enabled = $false

# Clear results button
$buttonClear = New-Object System.Windows.Forms.Button
$buttonClear.Location = New-Object System.Drawing.Point(150, 260)
$buttonClear.Size = New-Object System.Drawing.Size(100, 25)
$buttonClear.Text = "Clear Results"
$buttonClear.UseVisualStyleBackColor = $true
$buttonClear.Enabled = $false

# Event handlers
$buttonBrowse.Add_Click({
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "CSV Files (*.csv)|*.csv"
    $openFileDialog.Title = "Select CSV File"
    
    if ($openFileDialog.ShowDialog() -eq "OK") {
        $textBoxCSVPath.Text = $openFileDialog.FileName
        $buttonProcess.Enabled = $true
    }
})

$buttonProcess.Add_Click({
    if ([string]::IsNullOrEmpty($textBoxCSVPath.Text)) {
        [System.Windows.Forms.MessageBox]::Show("Please select a CSV file first.", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }
    
    # Reset progress
    $progressBar.Value = 0
    $labelStatus.Text = "Reading CSV file..."
    [System.Windows.Forms.Application]::DoEvents()
    
    # Read CSV data
    if (Read-CSVData -FilePath $textBoxCSVPath.Text) {
        $labelStatus.Text = "CSV file loaded successfully. Processing folders..."
        [System.Windows.Forms.Application]::DoEvents()
        
        # Process folders and verify TCIN
        Process-FoldersAndVerifyTCIN -ProgressBar $progressBar -StatusLabel $labelStatus
        
        # Update results grid - Convert to DataTable for better display
        Update-ResultsGrid
        $buttonExport.Enabled = $true
        $buttonClear.Enabled = $true
        
        [System.Windows.Forms.MessageBox]::Show("Processing completed! Check the results below.", "Information", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    }
})

$buttonExport.Add_Click({
    if ($script:ProcessingResults.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("No results to export.", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }
    
    $saveFileDialog = New-Object System.Windows.Forms.SaveFileDialog
    $saveFileDialog.Filter = "CSV Files (*.csv)|*.csv"
    $saveFileDialog.Title = "Save Results"
    $saveFileDialog.FileName = "ProcessingResults_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
    
    if ($saveFileDialog.ShowDialog() -eq "OK") {
        try {
            $script:ProcessingResults | Export-Csv -Path $saveFileDialog.FileName -NoTypeInformation
            [System.Windows.Forms.MessageBox]::Show("Results exported successfully!", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        }
        catch {
            [System.Windows.Forms.MessageBox]::Show("Error exporting results: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        }
    }
})

$buttonClear.Add_Click({
    $dataGridView.Rows.Clear()
    $dataGridView.Columns.Clear()
    $script:ProcessingResults = @()
    $buttonExport.Enabled = $false
    $buttonClear.Enabled = $false
    $progressBar.Value = 0
    $labelStatus.Text = "Results cleared. Ready to process..."
})

# Add controls to form
$groupBox1.Controls.Add($textBoxCSVPath)
$groupBox1.Controls.Add($buttonBrowse)
$groupBox1.Controls.Add($buttonProcess)

$groupBox2.Controls.Add($progressBar)
$groupBox2.Controls.Add($labelStatus)

$groupBox3.Controls.Add($dataGridView)
$groupBox3.Controls.Add($buttonExport)
$groupBox3.Controls.Add($buttonClear)

$form.Controls.Add($groupBox1)
$form.Controls.Add($groupBox2)
$form.Controls.Add($groupBox3)

# Show the form
[System.Windows.Forms.Application]::EnableVisualStyles()
$form.ShowDialog()