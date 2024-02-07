PY ?= python3

main: legal_moves

legal_moves: download_data
	bun src/legal_moves.ts data/twic_full.pgn
	$(PY) src/plot_legal_moves.py

download_data:
	bash download_data.sh
