#  LocStoc — Stock Counting CLI

An interactive shell for counting and managing product stock across multiple storage rooms. Featuring fuzzy matching, autosave, undo and export features.

---

##  Features

-  Click-shell interface for smooth interaction
-  Count products per location with fuzzy product name matching
-  Undo previous actions
-  View counts in real time
-  Export to `.csv` and `.xlsx` formats (with timestamped filenames)
-  Autosave on exit
-  Room-check validation before finalizing

---

##  Usage

###  Requirements

Install required packages (if not already installed):

```bash
pip install click click-shell pandas thefuzz openpyxl
```

---

###  Launch the Stock Counting Shell

```bash
python locstoc.py
```

You’ll be greeted with a prompt like:

```
Happy Sunday Boss
locstoc >
```

---

###  Commands

#### `help`

List all available commands.

```bash
locstoc > help
```

#### `mv ROOM`

Change your current location.

```bash
locstoc > mv SR
```

**Room codes:**
- `SR` = Spirit Room  
- `BC` = Beer Cellar  
- `TAP` = Tap Room  
- `BL` = Blighters  
- `TER` = Terrace

#### `where`

Print your current location.

```bash
locstoc > where
```

#### `begin`

Begin counting in the current room. Input product name + quantity.

```bash
locstoc > begin
Product > tanq 3
Product > undo
Product > done
```

Fuzzy matching is used, and you'll be prompted to confirm matches or choose alternatives.

#### `export [--csv] [--excel]`

Export the product DataFrame with a timestamped filename.

```bash
locstoc > export --csv --excel
```

- Files are saved to the `exports/` directory.
- Autosaves (on exit) go to the `autosaves/` folder.

#### `table [--room ROOMCODE]`

Print current stock counts to terminal. Only non-zero counts are shown.

```bash
locstoc > table
locstoc > table --room BC
```

#### `check`

Ensure that each room has at least one product counted.

```bash
locstoc > check
```

#### `ls`

Lists all products possible to count.
```bash
locstoc > ls
```

#### `exit`

Exits the shell safely, autosaving your progress.

```bash
locstoc > exit
```

You’ll see:

```
StocTake over - saving data...
CSV exported as stock_22-04-2025_01-21-11.csv
Excel exported as stock_22-04-2025_01-21-11.xlsx
Autosave successful
```

---

##  Output Structure

- `/exports/`: Manual exports (via `export` command)
- `/autosaves/`: Autosaved files (on exit)

---

##  Dev Notes

- To add new products, edit the `product_list` at the top of the script.
- You can extend room support by modifying the `rooms` dictionary.

---


##  License

MIT — free to use and modify.  
Credit appreciated if you fork or build on it.
