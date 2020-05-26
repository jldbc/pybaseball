# Retrosheet

The functions in `retrosheet.py` retrieve game logs, rosters, schedules, park codes and event files by Retrosheet from [the Chadwick Bureau Github](https://github.com/chadwickbureau/retrosheet).

## Retrosheet Data Notice

Recipients of Retrosheet data are free to make any desired use of
the information, including (but not limited to) selling it,
giving it away, or producing a commercial product based upon the
data.  Retrosheet has one requirement for any such transfer of
data or product development, which is that the following
statement must appear prominently:

     The information used here was obtained free of
     charge from and is copyrighted by Retrosheet.  Interested
     parties may contact Retrosheet at "www.retrosheet.org".

Retrosheet makes no guarantees of accuracy for the information
that is supplied. Much effort is expended to make our website
as correct as possible, but Retrosheet shall not be held
responsible for any consequences arising from the use the
material presented here. All information is subject to corrections
as additional data are received. We are grateful to anyone who
discovers discrepancies and we appreciate learning of the details.

`season_game_logs(season)`: Retrieve game logs for a given season.

`world_series_logs()`: Retrieve game logs from all World Series games.

`all_star_game_logs()`: Retrieve game logs from all All Star Games

`wild_card_logs()`: Retrieve game logs from all Wild Card Games.

`division_series_logs`: Retrieve game logs from all Division Series Games.

`lcs_logs()`: Retrieve game logs from all LCS games.

`schedule(season)`: Retrieve all scheduled games and postponements for a given season.

`park_codes()`: Retrieves the park codes used by retrosheet.

`rosters(season)`: Retrieves all major league rosters for a given season.

`events(season, type='regular', export_dir='.')`: Downloads the event files from retrosheet. `type` can be one of `regular`, `post`, or `asg`. The files are saved in the specified export directory.
