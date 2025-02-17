#!/bin/bash
# upload_to_gsc.sh
#
# This shell scripts processes 
# It uses `librosa` via Python and saves the spectrogram as an image.
#
# Author: John Doe
# Email: johndoe@example.com

# NOTE***** This is how I downloaded each file from Zenodo and added to my local
# <wget https://zenodo.org/record/3384388/files/6_dB_slider.zip>   
# Downloaded these files manually one by one using above, we could probably also use a shell script for this process

# Bucketname
BUCKET_NAME="pmf-data-store"

# Where it's stored in memory 
LOCAL_FOLDER="/Users/jaimacabangon/data_for_pmf"

# Temp folder it's going to when we unzip
TEMP_FOLDER="/Users/jaimacabangon/temp_extracted"


# Check if gsutil is part of GC SDK, tool we use to interact with blob storage 
if ! command -v gsutil &> /dev/null; then
    echo "Error: gsutil is not installed. Please install the Google Cloud SDK."
    exit 1
fi

# Check if the local folder exists
if [ ! -d "$LOCAL_FOLDER" ]; then
    echo "Error: Folder $LOCAL_FOLDER does not exist. Please check the path."
    exit 1
fi

# Create a temporary folder for extraction if it doesn't exist
mkdir -p "$TEMP_FOLDER"

# Initialize counters
success_count=0
fail_count=0

# Loop through all .zip files in the folder
for zip_file in "$LOCAL_FOLDER"/*.zip; do
    if [ -f "$zip_file" ]; then
        echo "Processing $zip_file..."
        
        # Extract the .zip file to the TEMP_FOLDER
        unzip -q "$zip_file" -d "$TEMP_FOLDER/"
        
        # Find and upload all .wav files to the GCS bucket, preserving directory structure
        find "$TEMP_FOLDER" -type f -name "*.wav" | while read wav_file; do
            # Get the relative path of the .wav file inside the TEMP_FOLDER
            relative_path="${wav_file#$TEMP_FOLDER/}"

            # Upload the file to the corresponding path in GCS
            echo "Uploading $relative_path to gs://$BUCKET_NAME/$relative_path"
            gsutil cp "$wav_file" "gs://$BUCKET_NAME/$relative_path"
            if [ $? -eq 0 ]; then
                echo "$relative_path uploaded successfully."
                ((success_count++))
            else
                echo "Failed to upload $relative_path."
                ((fail_count++))
            fi
        done
        
        # Clean up temporary folder
        echo "Cleaning up extracted files from $zip_file..."
        rm -rf "$TEMP_FOLDER"/*
    else
        echo "No .zip files found in $LOCAL_FOLDER."
        break
    fi
done

# Summary report
echo "Upload process complete."
echo "Files successfully uploaded: $success_count"
echo "Files failed to upload: $fail_count"

if [ $fail_count -gt 0 ]; then
    echo "Some files failed to upload. Please check the logs above for details."
fi
