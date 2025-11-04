// Photoshop Script to Run Action 'DFG' from Action Set 'ABC'
// Save this file with a .jsx extension and run it from File > Scripts > Browse in Photoshop

try {
    // Define the action set and action names
    var actionSetName = "ABC";
    var actionName = "DFG";
    
    // Play the action
    app.doAction(actionName, actionSetName);
    
    // Optional: Display success message
    // alert("Action '" + actionName + "' from set '" + actionSetName + "' completed successfully.");
    
} catch (e) {
    // Error handling
    alert("Error running action:\n" + e.message + "\n\nPlease ensure:\n1. Action set '" + actionSetName + "' exists\n2. Action '" + actionName + "' exists in that set\n3. The action set is loaded in Photoshop");
}



// To Prosses if Image path is provided as array
// Photoshop Script to Run Action 'DFG' from Action Set 'ABC' on Multiple Files
// Save this file with a .jsx extension and run it from File > Scripts > Browse in Photoshop

// Configuration
var actionSetName = "ABC";
var actionName = "DFG";
var inputFiles = ["C:\\local\\folder1\\image1.jpg", "C:\\local\\folder2\\image2.png"]; // Add your file paths here
var suffix = "_applied";

// Main function
function main() {
    try {
        var totalProcessed = 0;
        var totalErrors = 0;
        var errorMessages = [];
        
        $.writeln("Starting batch processing of " + inputFiles.length + " file(s)");
        
        // Process each file
        for (var i = 0; i < inputFiles.length; i++) {
            var filePath = inputFiles[i];
            var file = new File(filePath);
            
            if (!file.exists) {
                var msg = "File does not exist: " + filePath;
                $.writeln(msg);
                errorMessages.push(msg);
                totalErrors++;
                continue;
            }
            
            try {
                processImage(file);
                totalProcessed++;
                $.writeln("Processed (" + (i + 1) + "/" + inputFiles.length + "): " + file.name);
            } catch (e) {
                var msg = "Error processing " + file.name + ": " + e.message;
                $.writeln(msg);
                errorMessages.push(msg);
                totalErrors++;
            }
        }
        
        // Show completion message
        var message = "Batch processing complete!\n\n";
        message += "Successfully processed: " + totalProcessed + " file(s)\n";
        if (totalErrors > 0) {
            message += "Errors: " + totalErrors + " file(s)\n\n";
            message += "Error details:\n";
            for (var j = 0; j < Math.min(errorMessages.length, 5); j++) {
                message += "- " + errorMessages[j] + "\n";
            }
            if (errorMessages.length > 5) {
                message += "... and " + (errorMessages.length - 5) + " more error(s)";
            }
        }
        alert(message);
        
    } catch (e) {
        alert("Error: " + e.message + "\n\nPlease ensure:\n1. Action set '" + actionSetName + "' exists\n2. Action '" + actionName + "' exists in that set\n3. The action set is loaded in Photoshop");
    }
}

// Process individual image
function processImage(file) {
    // Open the file
    var doc = app.open(file);
    
    try {
        // Run the action
        app.doAction(actionName, actionSetName);
        
        // Generate new filename with suffix
        var newFile = generateNewFilename(file);
        
        // Save the file
        saveFile(doc, newFile);
        
        // Close the document
        doc.close(SaveOptions.DONOTSAVECHANGES);
        
    } catch (e) {
        // Close document even if error occurs
        if (doc) {
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }
        throw e;
    }
}

// Generate new filename with suffix
function generateNewFilename(file) {
    var fileName = file.name;
    var folderPath = file.parent.fsName;
    
    // Get file extension
    var lastDot = fileName.lastIndexOf(".");
    var baseName = fileName.substring(0, lastDot);
    var extension = fileName.substring(lastDot);
    
    // Create new filename
    var newFileName = baseName + suffix + extension;
    var newFilePath = folderPath + "/" + newFileName;
    
    return new File(newFilePath);
}

// Save file based on its format
function saveFile(doc, file) {
    var extension = file.name.toLowerCase();
    
    if (extension.indexOf(".jpg") !== -1 || extension.indexOf(".jpeg") !== -1) {
        // Save as JPEG
        var jpegOptions = new JPEGSaveOptions();
        jpegOptions.quality = 12; // Maximum quality
        jpegOptions.embedColorProfile = true;
        doc.saveAs(file, jpegOptions, true, Extension.LOWERCASE);
        
    } else if (extension.indexOf(".png") !== -1) {
        // Save as PNG
        var pngOptions = new PNGSaveOptions();
        pngOptions.compression = 6;
        pngOptions.interlaced = false;
        doc.saveAs(file, pngOptions, true, Extension.LOWERCASE);
        
    } else if (extension.indexOf(".tif") !== -1 || extension.indexOf(".tiff") !== -1) {
        // Save as TIFF
        var tiffOptions = new TiffSaveOptions();
        tiffOptions.imageCompression = TIFFEncoding.TIFFLZW;
        tiffOptions.embedColorProfile = true;
        doc.saveAs(file, tiffOptions, true, Extension.LOWERCASE);
        
    } else if (extension.indexOf(".psd") !== -1) {
        // Save as PSD
        var psdOptions = new PhotoshopSaveOptions();
        psdOptions.embedColorProfile = true;
        psdOptions.layers = true;
        doc.saveAs(file, psdOptions, true, Extension.LOWERCASE);
        
    } else if (extension.indexOf(".bmp") !== -1) {
        // Save as BMP
        var bmpOptions = new BMPSaveOptions();
        bmpOptions.depth = BMPDepthType.TWENTYFOUR;
        doc.saveAs(file, bmpOptions, true, Extension.LOWERCASE);
        
    } else {
        // Default: save as original format
        doc.save();
    }
}

// Run the main function
main();