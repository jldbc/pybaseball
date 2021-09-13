import pybaseball


class TestTeamGameLogs:
    def test_nyy_game_logs_regression1():
        """Regression test for NYY 2021 subway series"""
        df = pybaseball.team_game_logs(2021, "NYY", "pitching") 

        # NYY home against TOR 9/9/2021
        assert df.loc[139]["Home"]

        # subway series 9/11/2021, NYY playing Mets @ Citi (NYY is Away)
        assert not df.loc[141]["Home"]
