# Birthplace Statistics

`display_top_players_with_stats(nationality, x=25)`

Display the top MLB players by WAR (Wins Above Replacement) for a given nationality or U.S. state.

## Arguments

`nationality`: The nationality or state abbreviation to filter players by. The following is the list of available nationalities and state codes:

|Name|Code|Name|Code|
|:--:|:--:|:--:|:--:|
|Alabama|AL|Montana|MT|
|Alaska|AK|Nebraska|NE|
|Arizona|AZ|Nevada|NV|
|Arkansas|AR|New Hampshire|NH|
|California|CA|New Jersey|NJ|
|Colorado|CO|New Mexico|NM|
|Connecticut|CT|New York|NY|
|Delaware|DE|North Carolina|NC|
|District of Columbia|DC|North Dakota|ND|
|Florida|FL|Ohio|OH|
|Georgia|GA|Oklahoma|OK|
|Hawaii|HI|Oregon|OR|
|Idaho|ID|Pennsylvania|PA|
|Illinois|IL|Rhode Island|RI|
|Indiana|IN|South Carolina|SC|
|Iowa|IA|South Dakota|SD|
|Kansas|KS|Tennessee|TN|
|Kentucky|KY|Texas|TX|
|Louisiana|LA|Utah|UT|
|Maine|ME|Vermont|VT|
|Maryland|MD|Virginia|VA|
|Massachusetts|MA|Washington|WA|
|Michigan|MI|West Virginia|WV|
|Minnesota|MN|Wisconsin|WI|
|Mississippi|MS|Wyoming|WY|
|Missouri|MO|Dominican Republic|Dominican-Republic|
|Afghanistan|Afghanistan|France|France|
|American Samoa|American-Samoa|Germany|Germany|
|Aruba|Aruba|Italy|Italy|
|Australia|Australia|Japan|Japan|
|Austria|Austria|Mexico|Mexico|
|Bahamas|Bahamas|Netherlands|Netherlands|
|Belgium|Belgium|Puerto Rico|Puerto-Rico|
|Brazil|Brazil|Venezuela|Venezuela|

`x`: (Optional) The number of top players to display. Default is 25.

---

## Examples of valid queries

### Example 1: Display the top 10 players from California
```python
from birthplace_stats import display_top_players_with_stats

display_top_players_with_stats("CA", 10)
