# Car Ownership Tree

An interactive radial tree chart showing global automotive brand ownership — which parent corporations control which car brands.

![](car-ownership.jpg)

## Features

- **Radial tree layout** — root in the center, brands radiate outward
- **Click to collapse/expand** any node to reduce clutter
- **Scroll to zoom, drag to pan** around the chart
- **Brand logo images** displayed for each leaf node
- **Dark mode** support (follows OS preference)
- **Asterisk notation**: `*` = majority-owned, `**` = joint venture

## Data

Covers 10 major automotive groups and ~57 brands:

| Group | Brands |
|-------|--------|
| Volkswagen Group | VW, Škoda, SEAT, CUPRA, Audi, Porsche, Bentley, Lamborghini, Ducati |
| Stellantis | Jeep, Ram, Peugeot, FIAT, Chrysler, Dodge, Citroën, Opel, Vauxhall, Alfa Romeo, DS, Lancia, Abarth, Maserati |
| Toyota | Toyota, Lexus, Daihatsu, Hino, Subaru\*, Mazda\* |
| Renault-Nissan-Mitsubishi | Renault, Dacia, Alpine, Nissan, Infiniti, Mitsubishi |
| Hyundai | Hyundai, Kia, Genesis |
| Geely | Geely Auto, Zeekr, Lynk & Co, Volvo\*, Polestar\*, Lotus\*, Smart\*\* |
| General Motors | Chevrolet, GMC, Cadillac |
| Ford | Ford, Lincoln |
| Tata Motors | Jaguar, Land Rover |
| Independent | Tesla, BYD, BMW, MINI, Rolls-Royce |

## Logo download scripts

- `download-logos.py` — downloads brand logos from Wikipedia to `car-logos/`
- `download-logos-retry.py` — retries failed downloads with alternate page titles
- `download-logos-final.py` — final pass for stubborn brands using known file names

Run them in order if starting fresh:
```bash
python3 download-logos.py
python3 download-logos-retry.py
python3 download-logos-final.py
```

## Tech

Built with [D3.js v7](https://d3js.org/) — standalone HTML, no build step.
