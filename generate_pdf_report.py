import sys
import os
import subprocess

def generate_pdf(md_file, pdf_file=None):
    if pdf_file is None:
        pdf_file = md_file.replace('.md', '.pdf')
    # Try to use pandoc if available
    try:
        subprocess.run(["pandoc", md_file, "-o", pdf_file], check=True)
        print(f"PDF generated: {pdf_file}")
    except Exception as e:
        print(f"Pandoc PDF generation failed: {e}\nPlease install Pandoc or use VS Code's Markdown PDF extension.")

def main():
    files = [
        "ghostwalk_final_remediation_report.md",
        "ghostwalk_final_triage.md",
        "OmniSOC_ITDR_Report_Auto.md"
    ]
    for md in files:
        if os.path.exists(md):
            generate_pdf(md)

if __name__ == "__main__":
    main()
