import subprocess
import os
import shutil
import sys

def get_changed_latex_file():
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^', '--', 'texFiles/*.tex'], stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split('\n')
    if len(files) != 1:
        print("Error: There should be exactly one LaTeX file changed.")
        sys.exit(1)
    return files[0]

def build_latex(filename):
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    
    os.chdir(dirname)
    result = subprocess.run(['xelatex', name + '.tex'], stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    
    os.chdir('..')
    return os.path.join(dirname, name + '.pdf')

def move_pdf(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.move(pdf_path, output_dir)

if __name__ == "__main__":
    tex_file = get_changed_latex_file()
    pdf_file = build_latex(tex_file)
    move_pdf(pdf_file, 'pdfFiles')