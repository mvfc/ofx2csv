# ofx2csv
Python script that converts .ofx and .qfx files to .csv


# Running

1. Have Python 3 installed
2. Install dependencies
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     python3 -m pip install -r requirements.txt
     ```
4. Put the ofx files in the same folder as `ofx2csv.py`
5. Do 

    ```bash
    python ofx2csv.py
    ```

# Options

## JSON Output

It defaults to `csv`. You can also request JSON.

```bash
python ofx2csv.py -o json
```

## Specify a file

It defaults to `*.ofx`; you can specify a file if you want:

```bash
python ofx2csv.py -i foo.qfx
```

Or two files:

```bash
python ofx2csv.py -i foo.qfx bar.qfx
```

You can also include wildcards:

```bash
python ofx2csv.py -i 2024-*.qfx bar.qfx
```
