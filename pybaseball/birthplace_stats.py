from datetime import datetime
from typing import Optional
import pandas as pd
from pybaseball.datasources.html_table_processor import HTMLTableProcessor

birthplace_dict = {
    # United States
    "AL": "/bio/AL_born.shtml",
    "AK": "/bio/AK_born.shtml",
    "AZ": "/bio/AZ_born.shtml",
    "AR": "/bio/AR_born.shtml",
    "CA": "/bio/CA_born.shtml",
    "CO": "/bio/CO_born.shtml",
    "CT": "/bio/CT_born.shtml",
    "DE": "/bio/DE_born.shtml",
    "DC": "/bio/DC_born.shtml",
    "FL": "/bio/FL_born.shtml",
    "GA": "/bio/GA_born.shtml",
    "HI": "/bio/HI_born.shtml",
    "ID": "/bio/ID_born.shtml",
    "IL": "/bio/IL_born.shtml",
    "IN": "/bio/IN_born.shtml",
    "IA": "/bio/IA_born.shtml",
    "KS": "/bio/KS_born.shtml",
    "KY": "/bio/KY_born.shtml",
    "LA": "/bio/LA_born.shtml",
    "ME": "/bio/ME_born.shtml",
    "MD": "/bio/MD_born.shtml",
    "MA": "/bio/MA_born.shtml",
    "MI": "/bio/MI_born.shtml",
    "MN": "/bio/MN_born.shtml",
    "MS": "/bio/MS_born.shtml",
    "MO": "/bio/MO_born.shtml",
    "MT": "/bio/MT_born.shtml",
    "NE": "/bio/NE_born.shtml",
    "NV": "/bio/NV_born.shtml",
    "NH": "/bio/NH_born.shtml",
    "NJ": "/bio/NJ_born.shtml",
    "NM": "/bio/NM_born.shtml",
    "NY": "/bio/NY_born.shtml",
    "NC": "/bio/NC_born.shtml",
    "ND": "/bio/ND_born.shtml",
    "OH": "/bio/OH_born.shtml",
    "OK": "/bio/OK_born.shtml",
    "OR": "/bio/OR_born.shtml",
    "PA": "/bio/PA_born.shtml",
    "RI": "/bio/RI_born.shtml",
    "SC": "/bio/SC_born.shtml",
    "SD": "/bio/SD_born.shtml",
    "TN": "/bio/TN_born.shtml",
    "TX": "/bio/TX_born.shtml",
    "UT": "/bio/UT_born.shtml",
    "VT": "/bio/VT_born.shtml",
    "VA": "/bio/VA_born.shtml",
    "WA": "/bio/WA_born.shtml",
    "WV": "/bio/WV_born.shtml",
    "WI": "/bio/WI_born.shtml",
    "WY": "/bio/WY_born.shtml",
    # Other Countries
    "Afghanistan": "/bio/Afghanistan_born.shtml",
    "American-Samoa": "/bio/American-Samoa_born.shtml",
    "Aruba": "/bio/Aruba_born.shtml",
    "At-Sea": "/bio/At-Sea_born.shtml",
    "Australia": "/bio/Australia_born.shtml",
    "Austria": "/bio/Austria_born.shtml",
    "Bahamas": "/bio/Bahamas_born.shtml",
    "Belgium": "/bio/Belgium_born.shtml",
    "Belize": "/bio/Belize_born.shtml",
    "Brazil": "/bio/Brazil_born.shtml",
    "Canada": "/bio/Canada_born.shtml",
    "China": "/bio/China_born.shtml",
    "Colombia": "/bio/Colombia_born.shtml",
    "Cuba": "/bio/Cuba_born.shtml",
    "Curacao": "/bio/Curacao_born.shtml",
    "Czech-Republic": "/bio/Czech-Republic_born.shtml",
    "Denmark": "/bio/Denmark_born.shtml",
    "Dominican-Republic": "/bio/Dominican-Republic_born.shtml",
    "Finland": "/bio/Finland_born.shtml",
    "France": "/bio/France_born.shtml",
    "Germany": "/bio/Germany_born.shtml",
    "Greece": "/bio/Greece_born.shtml",
    "Guam": "/bio/Guam_born.shtml",
    "Honduras": "/bio/Honduras_born.shtml",
    "Hong-Kong": "/bio/Hong-Kong_born.shtml",
    "Indonesia": "/bio/Indonesia_born.shtml",
    "Ireland": "/bio/Ireland_born.shtml",
    "Italy": "/bio/Italy_born.shtml",
    "Jamaica": "/bio/Jamaica_born.shtml",
    "Japan": "/bio/Japan_born.shtml",
    "Latvia": "/bio/Latvia_born.shtml",
    "Lithuania": "/bio/Lithuania_born.shtml",
    "Mexico": "/bio/Mexico_born.shtml",
    "Netherlands": "/bio/Netherlands_born.shtml",
    "Nicaragua": "/bio/Nicaragua_born.shtml",
    "Norway": "/bio/Norway_born.shtml",
    "Panama": "/bio/Panama_born.shtml",
    "Peru": "/bio/Peru_born.shtml",
    "Philippines": "/bio/Philippines_born.shtml",
    "Poland": "/bio/Poland_born.shtml",
    "Portugal": "/bio/Portugal_born.shtml",
    "Puerto-Rico": "/bio/Puerto-Rico_born.shtml",
    "Russian-Federation": "/bio/Russian-Federation_born.shtml",
    "Saudi-Arabia": "/bio/Saudi-Arabia_born.shtml",
    "Singapore": "/bio/Singapore_born.shtml",
    "Slovakia": "/bio/Slovakia_born.shtml",
    "South-Africa": "/bio/South-Africa_born.shtml",
    "South-Korea": "/bio/South-Korea_born.shtml",
    "Spain": "/bio/Spain_born.shtml",
    "Sweden": "/bio/Sweden_born.shtml",
    "Switzerland": "/bio/Switzerland_born.shtml",
    "Taiwan": "/bio/Taiwan_born.shtml",
    "U--S--Virgin-Islands": "/bio/U--S--Virgin-Islands_born.shtml",
    "Ukraine": "/bio/Ukraine_born.shtml",
    "United-Kingdom": "/bio/United-Kingdom_born.shtml",
    "Venezuela": "/bio/Venezuela_born.shtml",
    "Viet-Nam": "/bio/Viet-Nam_born.shtml"
}

class BirthplaceHTMLTableProcessor(HTMLTableProcessor):
    def get_tabular_data_from_element(self, element, column_name_mapper=None,
                                      known_percentages=None, row_id_func=None, row_id_name=None):
        
        """
        Extracts tabular data from an HTML element and converts it into a Pandas DataFrame.

        Args:
            element: The HTML element containing the table data.
            column_name_mapper: Optional function to rename column headings.
            known_percentages: Optional list of columns to treat as percentages.
            row_id_func: Optional function to generate row IDs.
            row_id_name: Optional name for the row ID column.

        Returns:
            A Pandas DataFrame containing the extracted table data.
        """

        headings = element.xpath(self.headings_xpath)
        if column_name_mapper:
            headings = list(column_name_mapper(headings))

        data_rows_dom = element.xpath(self.data_rows_xpath)

        data_rows = []
        for row_index, row in enumerate(data_rows_dom):
            cells = row.xpath(self.data_cell_xpath)
            cell_texts = [''.join(cell.itertext()).strip() for cell in cells]  # Extract and clean text

            parsed_row = []
            for index, cell in enumerate(cell_texts):
                try:
                    # Attempt to parse numbers and dates where applicable
                    if cell.replace('.', '', 1).isdigit():
                        parsed_value = float(cell) if '.' in cell else int(cell)
                    elif any(char.isdigit() for char in cell) and "/" in cell:  # Date-like value
                        parsed_value = cell
                    else:
                        parsed_value = cell
                except ValueError:
                    parsed_value = cell  # Fallback to raw value if parsing fails
                parsed_row.append(parsed_value)

            data_rows.append(parsed_row)

        if row_id_func:
            headings = [row_id_name or 'id'] + headings
            for index in range(len(data_rows_dom)):
                data_rows[index].insert(0, row_id_func(data_rows_dom[index]))

        # Create DataFrame
        data_frame = pd.DataFrame(data_rows, columns=headings)

        return data_frame
    
class BaseballReferenceProcessor(BirthplaceHTMLTableProcessor):
    """
    A processor for extracting player data from Baseball Reference tables.

    Methods:
        get_top_players_by_war: Retrieves the top players by WAR for a given URL.
    """

    def __init__(self):
        """
        Initializes the BaseballReferenceProcessor with appropriate XPath queries
        for Baseball Reference table structures.
        """
        super().__init__(
            root_url="https://www.baseball-reference.com",
            headings_xpath='//*[@id="div_bio_batting"]/table/thead/tr/th/text()',
            data_rows_xpath='//*[@id="div_bio_batting"]/table/tbody/tr',
            data_cell_xpath='.//td | .//th'
        )

    def get_top_players_by_war(self, url: str, x: int = 25) -> pd.DataFrame:
        """
        Retrieves the top players by WAR from a Baseball Reference URL.

        Args:
            url: The relative URL for the player's birthplace page on Baseball Reference.
            x: The number of top players to retrieve.

        Returns:
            A Pandas DataFrame containing the top players by WAR.
        """

        # Fetch table data
        data = self.get_tabular_data_from_url(url)

        if 'WAR' not in data.columns or 'To' not in data.columns:
            raise ValueError("Expected columns 'WAR' and 'To' are missing. Check the table structure.")

        # Ensure numeric conversion
        data['WAR'] = pd.to_numeric(data['WAR'], errors='coerce')
        data['To'] = pd.to_numeric(data['To'], errors='coerce')

        # Filter players active in the current year
        current_year = datetime.now().year
        current_players = data[data['To'] == current_year]

        # Sort by WAR in descending order
        top_players = current_players.sort_values(by='WAR', ascending=False).head(x)

        return top_players


def display_top_players_with_stats(nationality: str, x: int = 25):
    """
    Displays and optionally saves the top players by WAR for a given nationality.

    Args:
        nationality: The player's nationality or birthplace.
        x: The number of top players to display.

    Raises:
        ValueError: If no URL mapping is found for the provided nationality.
    """
    
    # Get the URL for the given nationality
    birthplace_url = birthplace_dict.get(nationality)
    if not birthplace_url:
        raise ValueError(f"No URL mapping found for nationality '{nationality}'.")

    full_url = birthplace_url

    # Process the data
    processor = BaseballReferenceProcessor()
    top_players = processor.get_top_players_by_war(full_url, x)

    if top_players.empty:
        print("\nNo players found for the specified nationality and year.")
        return

    # Use Pandas to display the table
    print("\nTop Players by WAR:")
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.expand_frame_repr', False)  # Avoid truncation
    print(top_players.to_string(index=False))  # Print the DataFrame as a formatted string

    # Save as an HTML table
    save_option = input("\nWould you like to save the table? (y/n): ").strip().lower()
    if save_option == "y":
        file_name = input("Enter file name (with .html or .csv extension): ").strip()
        if file_name.endswith(".html"):
            top_players.to_html(file_name, index=False, border=1)
            print(f"Table saved as {file_name}")
        elif file_name.endswith(".csv"):
            top_players.to_csv(file_name, index=False)
            print(f"Table saved as {file_name}")
        else:
            print("Invalid file extension. Please save as .html or .csv.")