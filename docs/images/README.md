# README screenshots

These images are direct Chromium captures of the application using temporary
**standard-mode** events. The event title and all competitor names are fictional.
They do not contain real event data, pairing codes or webcam feeds.

| Image | Application state |
| --- | --- |
| `song-selection.jpg` | Six candidates, two bans and two completed picks |
| `control-panel.jpg` | Main control processing the second song, with saved demo scores |
| `event-template.jpg` | Editable configuration before selecting a qualifier plan |
| `final-standings.jpg` | Confirmed two-song final, with a podium and unordered placement bands |

To regenerate them, install the project dependencies, the Python packages from
`requirements-test.txt` and Chromium, then run from the project root:

```sh
python3 scripts/capture-readme-screenshots.py
```

The script creates and removes temporary event directories. It never opens the
live `data/` directory. Set `CHROME_BINARY` to use an installed browser. Qualifier
scores and bracket results are generated through the tournament actions; song
draws are random, so regenerated jackets may differ. Reduced motion makes the
captures settle without changing the application layout.

Screenshots share the bundled artwork whose sources are documented in the
[song jacket notes](../../public/assets/song/song-list-2026/README.md). See the
[project README](../../README.md) for the main operating guide.
