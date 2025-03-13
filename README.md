# Webcrawl

## How to run the python script
1. web to md: `python crawl_docs_fast.py` (currently it is hardcoded to CloudSynapps website)
- Input sitemap and output folder:
`python crawl_docs_fast.py -w "https://www.cloudsynapps.com/page-sitemap.xml" -o my_docs`
- adjust the number of concurrent crawls:
`python crawl_docs_fast.py -w "https://www.cloudsynapps.com/page-sitemap.xml" -o results -c 5`
2. md to pdf:
  - Using wildcards to convert multiple files at once: `python markdown_to_pdf.py "*.md"`
  - Converting all markdown files in a specific directory: `python markdown_to_pdf.py "docs/*.md"`
  - Converting all markdown files recursively in subdirectories: `python markdown_to_pdf.py "**/*.md"`
  - Specifying an output directory for all generated PDFs: `python markdown_to_pdf.py "*.md" -o output_directory`
  - Still supporting single file conversion if needed: `python markdown_to_pdf.py specific_file.md -s`

## Documentation on Web Crawling
Steps:
1.	Run a python script to web crawl and get all the sites from web page to markdown
2.	Run a python script to change markdown files to pdf
  a.	Follow the instructions to install weasyprint
3.	Upload the pdf to Agentforce data library (This will take time)
  a.	If search Index Status is failed, just click on rebuild. It might take time and it might fail more than once.
4.	Agentforce Topic: Use the topic “General FAQ”

## How to install weasyprint?
### Windows Installation:

1.  Install GTK3:
    
    *   Download and run the MSYS2 installer from [https://www.msys2.org/](https://www.msys2.org/)
        
    *   Open the MSYS2 terminal and run: 
    `pacman -S mingw-w64-x86\_64-gtk3 mingw-w64-x86\_64-python-pip mingw-w64-x86\_64-python-pillow mingw-w64-x86\_64-python-cffi
    `    
    *   Add the MSYS2 bin directory to your PATH (typically: `C:\\msys64\\mingw64\\bin`)
        
2.  Install weasyprint
`pip install weasyprint`
    

### macOS Installation:

1. Install dependencies using Homebrew:
`brew install python3 cairo pango gdk-pixbuf libffi`

2. Install WeasyPrint:
`pip install weasyprint`
    

### Linux (Ubuntu/Debian) Installation:

Linux (Ubuntu/Debian) Installation:

1. Install dependencies:
`sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`

2. Install WeasyPrint:
`pip install weasyprint`
    
### Linux (Fedora/RHEL/CentOS) Installation:

1. Install dependencies:
`sudo dnf install python3-devel python3-pip python3-setuptools python3-wheel python3-cffi libffi-devel redhat-rpm-config gcc cairo pango gdk-pixbuf2`

2. Install WeasyPrint:
`pip install weasyprint`


### Verification:

After installation, you can verify that WeasyPrint is correctly installed by running:

`python -m weasyprint --info`
