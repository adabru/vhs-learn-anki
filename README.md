# Anki card sets from official German vhs-learn.de learning platform

Setup virtual environment:

```py
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

Update the cards from the website:

```py
python anki_cards_from_vhs_learn.py
```

ISO 639-1 "ak" is Twi, the language the most spoken language in Ghana.

### Update tables from Anki card set

Export deck in Anki with settings "Notes in Plain Text (.txt)", rest default.
