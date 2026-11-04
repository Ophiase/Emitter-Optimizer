# Cases

One folder per case: `source.jpg`, a vertical aerial photograph; two layers
painted over it at the same resolution, `attraction.png` (grey, white is the
most demand) and `collision.png` (black is a wall); and the laws `emitter.py`
($\varphi$) and `sensor.py` ($\psi$). `uv run python -m scripts.paint`
repaints the layers from the photographs.

`just case garden` optimizes a case into `out/garden`. `run`, `serve` and
`window` take `--case garden`: the case gives the extent, the grid, the emitter
count and the laws, and any flag given overrides its value.

| Case | Source | Author | License |
| --- | --- | --- | --- |
| garden | [Bamberg Kleingartenverein Sendelbach](https://commons.wikimedia.org/wiki/File:Bamberg_Kleingartenverein_Sendelbach_Luftbild-20240218-RM-103233.jpg) | Reinhold Möller | CC BY-SA 4.0 |
| beach | [Top-down aerial of Palombaggia Beach](https://commons.wikimedia.org/wiki/File:Top-down_aerial_of_Palombaggia_Beach,_France_(52723809351).jpg) | dronepicr | CC BY 2.0 |
| marina | [Top-down aerial of the old town of Saint-Tropez](https://commons.wikimedia.org/wiki/File:Top-down_aerial_of_the_old_town_of_Saint-Tropez,_France_(52724273618).jpg) | dronepicr | CC BY 2.0 |
| harbor | [Top-down aerial of Skopelos Harbor](https://commons.wikimedia.org/wiki/File:Top-down_aerial_of_Skopelos_Harbor,_Greece_(51696631060).jpg) | dronepicr | CC BY 2.0 |
| ramparts | [Top-down aerial of the Palace of the Grand Master in Rhodes](https://commons.wikimedia.org/wiki/File:Top-down_aerial_of_the_Palace_of_the_Grand_Master_in_Rhodes_Old_Town,_Greece_(51698570066).jpg) | dronepicr | CC BY 2.0 |

The photographs are the Commons 1280-pixel renditions. The painted layers are
derivatives: those of `garden` are shared under CC BY-SA 4.0, as its source is.

## Beyond photographs

- **globe**: `attraction.png` and `land.png` are rasterized from
  [Natural Earth](https://www.naturalearthdata.com/), public domain, 110 m
  populated places and land, by `scripts/spaces/globe.py`.
- **urea**: `structure.csv` is the 12 K asymmetric unit of Swaminathan, Craven
  and McMullan, Acta Cryst. B40, 300 (1984).
