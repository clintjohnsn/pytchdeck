
import glob
import os

def stitch_markdown_to_txt(directory, output_file):
    md_files = sorted(
        glob.glob(os.path.join(directory, '*.md'))
    )
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for md_file in md_files:
            outfile.write(f'\n\n')
            with open(md_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stitch_markdown_to_txt(
        directory=base_dir,
        output_file=os.path.join(base_dir, 'llms.txt')
    )

