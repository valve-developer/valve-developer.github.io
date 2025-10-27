from PIL import Image
import os
import glob

# Define the target size
TARGET_SIZE = (500, 500)

# Get all jpg files in the current directory
jpg_files = glob.glob('*.jpg') + glob.glob('*.JPG')

# Process each image
for filename in jpg_files:
    try:
        # Open the image
        img = Image.open(filename)
        
        # Resize the image
        img_resized = img.resize(TARGET_SIZE)
        
        # Save the resized image (overwrites original)
        img_resized.save(filename)
        
        print(f"Resized: {filename}")
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")

print(f"Completed! Processed {len(jpg_files)} images.")
