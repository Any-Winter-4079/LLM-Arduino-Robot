# Notes on the `tools/` code:

## To compress videos

- Move to the tools dir:
  `cd tools`
- Make the script executable: `chmod +x compress_videos.sh`
- Provide input and output folders: `./compress_videos.sh ../videos/raw ../videos/compressed`
- Videos already compressed should be automatically skipped.

## To convert images to webp

- Move to the tools dir:
  `cd tools`
- Make the script executable: `chmod +x convert_to_webp.sh`
- Provide input and output folders: `./convert_to_webp.sh ../images/original ../images/webp`
- Images already in webp should be automatically skipped.

## To convert videos to gif

- Move to the tools dir:
  `cd tools`
- Make the script executable: `chmod +x convert_to_gif.sh`
- Provide input and output folders: `./convert_to_gif.sh ../videos/compressed ../videos/gif`
- Videos already in gif should be automatically skipped.
