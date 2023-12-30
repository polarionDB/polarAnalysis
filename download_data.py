import os
from concurrent.futures import ThreadPoolExecutor

def download_file(file: str, url: str):
    command: str = 'wget' + ' -q -O ' + file + ' ' + url
    print(command)
    os.system(command)

def unzip_file(file: str):
    command: str = 'unzip -qq ' + file
    print(command)
    os.system(command)
    
def download_wrapper(args: (str, str)):
    download_file(*args)

def unzip_wrapper(args: (str, str)):
    unzip_file(args[0])

def main():
    tasks = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        for i in range(1300, 1520):
            fname: str = 'data/twic' + str(i) + '.zip'
            url: str = 'https://theweekinchess.com/zips/twic' + str(i) + 'g.zip'

            tasks.append((fname, url))
        
        executor.map(download_wrapper, tasks)
        executor.map(unzip_wrapper, tasks)

    os.system('mv *.pgn data/')
    os.system('rm -fdr data/*.zip')
    os.system('cat data/*.pgn > data/twic_full.pgn1')
    os.system('rm data/*.pgn')
    os.system('mv data/twic_full.pgn1 data/twic_full.pgn')

    temp = open('data/.data_downloaded', 'w')
    temp.close()

if __name__ == "__main__":
    main()
