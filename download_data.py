import os

def main():
    if os.path.exists("data/.data_downloaded"):
        return

    os.system("bash process_pgn.sh")

    temp = open('data/.data_downloaded', 'w')
    temp.close()

if __name__ == "__main__":
    main()
