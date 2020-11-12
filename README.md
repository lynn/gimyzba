# gimyzba
This is a fork of https://github.com/teleological/gimyzba.

## Changes
- Port from Python 2 to Python 3
- Use `multiprocessing` to parallelize work (this now happens by default, the `-n` flag is gone)
- [Replace regex-based “dyad scoring” by a manual check](https://github.com/lynn/gimyzba/commit/40b3b68288ccb92eb126916fdb98eb54ac2aae89)
- [Tweak the LCS computation a little](https://github.com/lynn/gimyzba/commit/3d8385129b2c5dc76dd5774c1aca62d029a081ec)

The result is about 5× faster on my laptop. (7 seconds down to about 1.4 seconds)

## Usage

Create a gismu from transliterations:

    python gismu_score.py mandarin hindi english spanish russian arabic

For example:

    python gismu_score.py uan rakan ekspekt esper predpologa mulud

Use `-w` to specify a list of weights. The default is `0.347,0.196,0.160,0.123,0.089,0.085` and corresponds to the six languages above. The official Lojban gismu were made with this configuration. Here is a weighted 8-language configuration by Ilmen:

    python gismu_score.py -w 0.271,0.170,0.130,0.125,0.104,0.076,0.064,0.060  mandarin english spanish hindi arabic bengali russian portuguese

See old-README.txt for more info.
