# Player ID Lookup

`chadwick_register(save: bool = False)`

Get the Chadwick register people info.

## Arguments

`save:` bool. Save the file to disk.

<!-- This data comes from Chadwick Bureau, meaning that there are several people in this data who are not MLB players. For this reason, supplying both last and first name is recommended to narrow your search.  -->

## Example

```python
from pybaseball import chadwick_register

# get the register data
data = chadwick_register()

# get the register data and save to disk
data = chadwick_register(save=True)
```
