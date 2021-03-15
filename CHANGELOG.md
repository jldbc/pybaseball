
**2.1.1 Hotfix: October 15, 2020**

-  Fix statcast perf regression

**2.1.0 Release: October 14, 2020**

## Release Notes

We have a lot of new stuff in this release.

- Caching
   - We now cache most of the time expensive scraping functions. In addition, we have a consistent storage location for the Lahman Databank, so no more five copies of baseball-databank. This is currently disabled by default, you can enable it (see caching in the docs).
   - Basically, now when you call something like `batting_stats(2018)`, for a while subsequent calls will just hit the cache, if it is enabled, so you don't need to do a bunch of pd.load and df.to_csv all over your notebooks.
   - Right now this is a week by default, which is configurable in code, and will probably change soon to more specific per-function staleness. @TheCleric, @schorrm

- FanGraphs fielding - @TheCleric

- Massively expanded options for FanGraphs scraping - @TheCleric

- Marcel projections - @bdilday

- Batted ball trajectories - @bdilday

- Baseball Reference splits - @mwisnie5

- Add spray angle to statcast dataframes - @tjburch

- Flag imputed data (where Trackman didn't do it, stringers did) in statcast batting - @tjburch
   - See this piece in [The Hardball Times](https://tht.fangraphs.com/43416-2/) for more info.

- Plot batted ball profile - @tjburch

- Improvements to data type inference - @TheCleric

- Unit testing, by @TheCleric

- And various bugfixes, with thanks to @bdilday, @bgunn34, and @TheCleric.

**2.0.0 Release: August 28, 2020**

## Recent Updates
- New Maintainer: after a period of inactive maintenance, this is again being actively maintained.
- New functionality:
   - Plot spray charts on stadium (schorrm/pybaseball#9, thanks to @andersonfrailey)
   - Baseball Reference game logs (schorrm/pybaseball#4, thanks to @reddigari)
   - More functions for Chadwick Bureau data (schorrm/pybaseball#8, thanks to @valdezt)
   - Exposes Chadwick Bureau lookup table (schorrm/pybaseball#7)
   - Top Prospects (schorrm/pybaseball#5, thanks to @TylerLiu42)
   - Full Season Statcast data (schorrm/pybaseball#2, @TylerLiu42)
   - Amateur Draft results (schorrm/pybaseball#11, @TylerLiu42)
- Bugfixes, with thanks to @bgunn34 and @TAThor
