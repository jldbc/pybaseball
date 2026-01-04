# Statcast Utils

Utility functions for additional calculations on StatCast DataFrames. Located in `pybaseball/datahelpers/statcast_utils.py

## Add Spray Angle

`add_spray_angle(df: pd.DataFrame,  adjusted: Optional[bool] = False)`

Adds spray angle and adjusted spray angle to StatCast DataFrames
    - Spray angle is the raw left-right angle of the hit 
    - Adjusted spray angle flips the sign for left handed batters, making it a push/pull angle. Inspired by [this Alan Nathan post](http://baseball.physics.illinois.edu/carry-v2.pdf).
The formula to transform hit coordinates to spray angle used was obtained from [this blog post](https://baseballwithr.wordpress.com/2018/01/15/chance-of-hit-as-function-of-launch-angle-exit-velocity-and-spray-angle/).


### Arguments

df (pd.DataFrame): StatCast pd.DataFrame (retrieved through statcast, statcast_batter, etc)

### Example

The following code:

```python
from pybaseball.datahelpers.statcast_utils import add_spray_angle
from pybaseball import statcast

df = statcast("2018-05-01","2018-05-02")
# get hits
df = df[~df["bb_type"].isna()]
# Add Spray angle
df = add_spray_angle(df)
print("Spray Angle:")
print(df["spray_angle"][0:5])
df = add_spray_angle(df, adjusted=True)
print("Adjusted Spray Angle:")
print(df["adj_spray_angle"][0:5])
```

Will yield these calculated spray angles:

```
Spray Angle:
255    35.923343
300     3.571058
632    25.055293
698    -1.642098
732     2.711636
Name: spray_angle, dtype: float64
Adjusted Spray Angle:
255   -35.923343
300     3.571058
632    25.055293
698     1.642098
732     2.711636
Name: adj_spray_angle, dtype: float64
```

Notice the first (return index 255) and fourth (index 698) are from left-handed batters, since the sign on their spray angle is opposite that of their adjusted spray angle.

### Sample distributions

Shown for 2018 data:

![](images/spray_angle_hists.png)


## Vertical Approach Angle
`add_vertical_approach_angle(df: pd.DataFrame)`

Adds a column called "vaa" with the vertical approach angle of each pitch to a StatCast DataFrame
    
- Vertical approach angle is the angle, in degrees, at which the ball crosses home plate
    
- Formula obtained from [this Fangraphs article](https://blogs.fangraphs.com/a-visualized-primer-on-vertical-approach-angle-vaa/)

### Arguments

df (pd.DataFrame): StatCast pd.DataFrame (retrieved through statcast, statcast_pitcher, etc)

### Example

The following code:

```python
from pybaseball.datahelpers.statcast_utils import add_vertical_approach_angle
from pybaseball import statcast_pitcher

df = statcast_pitcher('2022-01-01', '2022-12-31', 543037)

# Add vertical approach angle
df = add_vertical_approach_angle(df)

print("Vertical approach angle:")
print(df['vaa'][0:5])
print("Average vertical approach angle by pitch type:")
print(df.groupby(['pitch_type'])['vaa'].mean())
```

Will output these vertical approach angles:

```
Vertical approach angle:
1   -11.867287
2    -3.098514
3    -2.910248
4    -7.566446
Name: vaa, dtype: float64
Average vertical approach angle by pitch type:
pitch_type
CH   -6.660848
FC   -5.804296
FF   -4.584262
KC   -9.739730
SI   -5.865324
SL   -7.742220
Name: vaa, dtype: float64
```