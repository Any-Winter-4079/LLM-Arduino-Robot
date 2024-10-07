#!/bin/bash

# Check if cwebp is installed
if ! command -v cwebp &> /dev/null
then
    echo "cwebp is not installed. Please install it using 'brew install webp'"
    exit 1
fi

# Check if input and output directories are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_folder> <output_folder>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Set quality (0-100, higher is better quality but larger file size)
QUALITY=100

# Process PNG and JPG files in the input directory
for input_file in "$INPUT_DIR"/*.{png,jpg,jpeg}; do
    # Check if the glob didn't match any files
    [ -e "$input_file" ] || continue
    
    # Get the filename without path and extension
    filename=$(basename "$input_file")
    filename_noext="${filename%.*}"
    
    # Check if a WebP version already exists
    if [ ! -f "$OUTPUT_DIR/${filename_noext}.webp" ]; then
        echo "Converting $filename to WebP..."
        
        # Convert the image to WebP
        cwebp -q $QUALITY -m 6 -af -f 100 -sharpness 0 -mt -v "$input_file" -o "$OUTPUT_DIR/${filename_noext}.webp"
        
        echo "Conversion complete for $filename"
    else
        echo "WebP version of $filename already exists. Skipping."
    fi
done

echo "All images processed."