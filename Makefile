PY ?= pypy3.10
MAIN_FILE = src/main.py

main: download_data
	@$(PY) $(MAIN_FILE)

download_data:
ifeq (,$(wildcard data/.data_downloaded))
	@$(PY) download_data.py 
endif