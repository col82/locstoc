from click_shell import shell
import pandas as pd
from thefuzz import fuzz
from tabulate import tabulate
import os, click, datetime


### Preamble
# ascii header lol
def print_header():
    header = r"""
----------------------------------------
----------------------------------------
   __               __  _               
  / /   ___    ___ / _\| |_  ___    ___ 
 / /   / _ \  / __|\ \ | __|/ _ \  / __|
/ /___| (_) || (__ _\ \| |_| (_) || (__ 
\____/ \___/  \___|\__/ \__|\___/  \___|
                                        
----------------------------------------
--------------LOC 04.25-----------------
----------------------------------------
Happy Sunday Chief!  Time to count
----------------------------------------
          """
    print(header)


# save folders
os.makedirs("exports", exist_ok=True)
os.makedirs("autosaves", exist_ok=True)


# list of possible stock locations
rooms = {
    "SR": "Spirit Room",
    "BC": "Beer Cellar",
    "TAP": "Tap Room",
    "BL": "Blighters",
    "TER": "Terrace",
}

# sample product list
product_list = [
    "Tanqueray",
    "Tanqueray 10",
    "Tanqueray Rangpur",
    "Brenne Single Malt",
    "Zacapa 230",
    "Woodford Reserve",
    "Michters Bourbon",
    "Zacapa XO",
    "Michters Rye",
    "Whistlepig 10",
    "Whistlepig 6",
    "Powers Rye",
    "Stauning Rye",
]

# create empty dataframe with rooms as col index, and products as row index
products_df = pd.DataFrame(0.0, index=product_list, columns=rooms.values())
# add totals col
products_df["Total"] = products_df.sum(axis=1)

# starting location
global current_loc
current_loc = "someplace"


### create shell instance
@shell(prompt="locstoc > ")
def locstoc():
    pass


### help command
@locstoc.command()
def help():
    print(
        """All commands are listed below:
          
          help:         see this list
          where:        prints current location
          mv:           change stock location [SR, BC, TAP, BL, TER]
          begin:        start count in current room
          check:        make sure you haven't missed a room 
          table:        prints current days stock as recorded so far
          export-csv:   export count data to csv
          export-excel: export count data to excel
          ls:           lists all products 
          exit:         exits shell instance
          """
    )


### where command - am i currently in a room or not
@locstoc.command()
def where():
    """returns users current location"""
    print(f"You are in: {current_loc}")


### change room command
@locstoc.command()
@click.argument("room", type=str, nargs=1)
def mv(room):
    """
    Change current stock location.
    Options: SR, BC, TAP, BL, TER
    """
    global current_loc
    # check if room exists
    room = room.upper()
    if room in rooms.keys():
        print(f"Moved to {rooms[room]}")
        current_loc = rooms[room]

    # if input is wrong, suggest rooms that exist
    else:
        print(
            f"""{room} doesn't exist :(
Try: SR, BC, TAP, BL, or TER"""
        )


### TODO: list products + do standard ls options, -r, also include filters for different product types
@locstoc.command()
def ls():
    """returns product list"""
    for bev in sorted(product_list):
        print(bev)


### begin count in a given room command
@locstoc.command()
def begin():
    """starts count instance in current location."""
    global current_loc, products_df

    # if room not selected, prompt
    if current_loc == "someplace":
        print("Please change your current location before beginning count")
        return

    # now ready for count
    print(f"Beginning count in {current_loc}")
    print(
        f"""Type product name (or abbreviation), followed by quantity.
    Type "undo" to revert the last change, or "done" to finish the count in {current_loc}."""
    )

    last_action = None

    # work through use input
    while True:
        # split input, check for done/exit statement
        entry = input("Product > ").strip()

        if entry.lower() in ["done", "exit"]:
            break

        # check for undo
        if entry.lower() == "undo":
            if last_action:
                product_name, room, old_val, new_val = last_action
                products_df.loc[product_name, room] = old_val
                print(f"Undid update: {product_name} in {room} reverted to {old_val}")
                last_action = None
            continue

        # separate input into name and quantity
        try:
            *name_parts, qty = entry.split()
            qty = float(qty)
            search_term = " ".join(name_parts)

        except:
            print("Badly formatted input - try: product-name quantity ")
            continue

        # fuzzy find
        matches = {}

        for prod in product_list:
            ratio = fuzz.ratio(search_term.lower(), prod.lower())
            matches[prod] = ratio

        # sorting matches in order of descending ratio
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        top_match, score = sorted_matches[0]

        def handle_update(product_name, qty):
            # store undo
            nonlocal last_action
            old_val = products_df.loc[product_name, current_loc]

            # check for existing count in current loc
            if old_val > 0:
                print(
                    f"Existing count for {product_name} in {current_loc} is {old_val}"
                )
                decision = (
                    input("Type A to add, R to replace, or C to cancel: ")
                    .strip()
                    .lower()
                )
                if decision == "a":
                    new_val = old_val + qty
                    products_df.loc[product_name, current_loc] = new_val
                    print(
                        f"Updated {product_name} in {current_loc}: {old_val} -> {new_val}"
                    )
                    last_action = (product_name, current_loc, old_val, new_val)
                elif decision == "r":
                    new_val = qty
                    products_df.loc[product_name, current_loc] = new_val
                    print(
                        f"Replaced {product_name} in {current_loc}: {old_val} -> {new_val}"
                    )
                    last_action = (product_name, current_loc, old_val, new_val)
                else:
                    print("No update made.")

            else:
                new_val = qty
                products_df.loc[product_name, current_loc] = new_val
                print(f"Added {product_name} in {current_loc}: 0 -> {new_val}")
                last_action = (product_name, current_loc, 0.0, new_val)

            # update totals
            products_df["Total"] = products_df[rooms.values()].sum(axis=1)

        # good match
        if score >= 75:
            confirm = (
                input(
                    f"Closest match: {top_match} ({score}%) — Enter Y to confirm, N to cancel: "
                )
                .strip()
                .lower()
            )
            if confirm == "y":
                handle_update(top_match, qty)
            else:
                print("No update made.")
        else:
            # poor match
            print(f"Low confidence match ({score}%).")
            print("Top 3 suggestions:")
            for i, (prod, scr) in enumerate(sorted_matches[:3], 1):
                print(f"{i}. {prod} ({scr}%)")
            choice = (
                input("Type number to select match, or 'n' to cancel: ").strip().lower()
            )

            if choice in ["1", "2", "3"]:
                selected_match = sorted_matches[int(choice) - 1][0]
                handle_update(selected_match, qty)
            else:
                print("No update made.")


### check if any room has all empty product counts
@locstoc.command()
def check():
    """check if there are zero counts completed in any of the locations"""
    empty_rooms = []

    # Check each room to see if all products have zero count in that room
    for room in rooms.values():
        if products_df[room].sum() == 0:
            empty_rooms.append(room)

    # Print out the results
    if empty_rooms:
        print(
            f"The following rooms have all empty product counts: {', '.join(empty_rooms)}"
        )


### print table to console
@locstoc.command()
@click.argument("room", required=False)
def table(room):
    df = products_df.copy()

    # non zero rows only
    nz_df = df.loc[(df.drop(columns="Total", errors="ignore") > 0).any(axis=1)]

    if room:
        room = room.upper()

        if room in rooms:
            room_name = rooms[room]
            if "Total" in nz_df.columns:
                filtered = nz_df[[room_name, "Total"]]
            else:
                filtered = nz_df[[room_name]]
            print(f"\nStock count for {room_name} (non-zero only):\n")
            print(
                tabulate(
                    filtered[filtered[room_name] > 0], headers="keys", tablefmt="pretty"
                )
            )
        else:
            print(f"Room not recognised. Try one of {', '.join(rooms.keys())}")

    else:
        print("Current stock counts:")
        print(tabulate(products_df, headers="keys", tablefmt="pretty"))


### export to csv or xlsx
@locstoc.command()
@click.option("--csv", is_flag=True, help="Export CSV only")
@click.option("--excel", is_flag=True, help="Export Excel only")
@click.option("--autosave", is_flag=True, help="For internal use only")
def export(csv, excel, autosave):
    """Export stock data to file (default is CSV and Excel)

    Args:
        csv (str): Export CSV only
        excel (str): Export Excel only
    """
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    if not csv and not excel:
        csv = excel = True

    if not autosave:
        target = "exports"
    else:
        csv = True
        excel = True
        target = "autosaves"

    if csv:
        csv_name = f"{target}/stock_{timestamp}.csv"
        products_df.to_csv(csv_name)
        print(f"CSV exported as stock_{timestamp}.csv")

    if excel:
        excel_name = f"{target}/stock_{timestamp}.xlsx"
        products_df.to_excel(excel_name, engine="openpyxl")
        print(f"Excel exported as stock_{timestamp}.xlsx")


if __name__ == "__main__":
    try:
        print_header()
        locstoc()
    except (SystemExit, EOFError, KeyboardInterrupt):
        print("StocTake over - saving data...")
        try:
            export.callback(csv=False, excel=False, autosave=True)
            print("Autosave successful")
        except Exception as e:
            print(f"Autosave failed: {e}")
