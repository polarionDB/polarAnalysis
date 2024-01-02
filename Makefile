PY ?= python3

main: download_data
	@$(PY) src/legal_moves.py

download_data:
ifeq (,$(wildcard data/.data_downloaded))
	@$(PY) download_data.py 
endif