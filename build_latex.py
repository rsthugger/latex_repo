import subprocess
import os
import shutil
import sys
import tempfile

def get_changed_latex_file():
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD^', '--', 'texFiles/*.tex'], stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split('\n')
    if len(files) != 1:
        print("Error: There should be exactly one LaTeX file changed.")
        sys.exit(1)
    return files[0]

def copy_required_files(tex_file, temp_dir):
    dirname = os.path.dirname(tex_file)
    basename = os.path.basename(tex_file)
    
    shutil.copy(tex_file, temp_dir)
    
    # Copy .bib files
    bib_files = [f for f in os.listdir(dirname) if f.endswith('.bib')]
    for bib_file in bib_files:
        shutil.copy(os.path.join(dirname, bib_file), temp_dir)
    
    # Copy image files (assuming images are in a subdirectory named "images")
    image_dir = os.path.join(dirname, 'images')
    if os.path.exists(image_dir):
        shutil.copytree(image_dir, os.path.join(temp_dir, 'images'))
    
    return basename

def build_latex(filename, temp_dir):
    name, _ = os.path.splitext(filename)
    
    os.chdir(temp_dir)
    try:
        # Run xelatex, biber, and xelatex twice to ensure proper compilation with bibliography
        for _ in range(2):
            result = subprocess.run(['xelatex', filename], stdout=subprocess.PIPE, text=True)
            print(result.stdout)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args)

        result = subprocess.run(['biber', name], stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)

        for _ in range(2):
            result = subprocess.run(['xelatex', filename], stdout=subprocess.PIPE, text=True)
            print(result.stdout)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args)
    finally:
        os.chdir('..')
    
    return os.path.join(temp_dir, name + '.pdf')

def move_pdf(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.move(pdf_path, os.path.join(output_dir, os.path.basename(pdf_path)))

if __name__ == "__main__":
    tex_file = get_changed_latex_file()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_basename = copy_required_files(tex_file, temp_dir)
        pdf_file = build_latex(tex_basename, temp_dir)
    
    move_pdf(pdf_file, 'pdfFiles')
