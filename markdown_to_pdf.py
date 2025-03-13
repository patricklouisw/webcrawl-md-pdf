import argparse
import markdown
import os
import glob
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def markdown_to_pdf(input_file, output_file=None):
    """
    Convert a single Markdown file to a formatted PDF
    
    Args:
        input_file (str): Path to the markdown file
        output_file (str, optional): Path for the output PDF file.
                                    If not provided, will use the same name as input file with .pdf extension
    """
    # Set default output file if not provided
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.pdf'
    
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br'
        ]
    )
    
    # Add CSS styling for better formatting
    css = CSS(string='''
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            margin: 2cm;
            max-width: 21cm;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #333;
        }
        h1 { font-size: 2.2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
        h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
        h3 { font-size: 1.5em; }
        h4 { font-size: 1.3em; }
        p { margin-bottom: 1em; }
        code {
            background-color: #f6f8fa;
            border-radius: 3px;
            font-family: monospace;
            padding: 0.2em 0.4em;
            font-size: 85%;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            font-family: monospace;
            padding: 16px;
            overflow: auto;
            font-size: 85%;
        }
        blockquote {
            margin: 0;
            padding-left: 1em;
            border-left: 4px solid #ddd;
            color: #666;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background-color: #f6f8fa;
        }
        img {
            max-width: 100%;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        ul, ol {
            padding-left: 2em;
        }
        li {
            margin-bottom: 0.25em;
        }
    ''')
    
    # Create full HTML document
    full_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{os.path.basename(input_file)}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    '''
    
    # Configure fonts
    font_config = FontConfiguration()
    
    # Generate PDF
    HTML(string=full_html).write_pdf(
        output_file,
        stylesheets=[css],
        font_config=font_config
    )
    
    print(f"Successfully converted {input_file} to {output_file}")

def process_multiple_files(input_pattern, output_dir=None):
    """
    Process multiple markdown files based on a glob pattern
    
    Args:
        input_pattern (str): Glob pattern to match markdown files (e.g., "*.md" or "docs/*.md")
        output_dir (str, optional): Directory to save output files. If not specified,
                                   PDFs will be saved in the same location as their source files
    """
    # Find all files matching the pattern
    matching_files = glob.glob(input_pattern, recursive=True)
    
    if not matching_files:
        print(f"No files found matching pattern: {input_pattern}")
        return
    
    # Process each file
    for input_file in matching_files:
        if output_dir:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the filename without the path
            filename = os.path.basename(input_file)
            
            # Create output filename
            output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.pdf')
        else:
            output_file = None  # Use default naming
            
        # Convert the file
        try:
            markdown_to_pdf(input_file, output_file)
        except Exception as e:
            print(f"Error converting {input_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown to formatted PDF")
    parser.add_argument("input", help="Input markdown file or pattern (e.g., '*.md', 'docs/*.md')")
    parser.add_argument("-o", "--output-dir", help="Output directory for PDF files (optional)")
    parser.add_argument("-s", "--single", action="store_true", 
                        help="Treat input as a single file rather than a pattern")
    
    args = parser.parse_args()
    
    if args.single:
        # Process as a single file
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            output_file = os.path.join(args.output_dir, 
                                      os.path.splitext(os.path.basename(args.input))[0] + '.pdf')
        else:
            output_file = None
            
        markdown_to_pdf(args.input, output_file)
    else:
        # Process as a pattern
        process_multiple_files(args.input, args.output_dir)