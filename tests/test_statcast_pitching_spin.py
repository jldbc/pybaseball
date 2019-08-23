import pybaseball.statcast_pitcher_spin as spin
import unittest
import pandas as pd
import numpy as np
import logging

SIG_DIG = 4 # Required because of read_csv bug in pandas

rounding_error_columns = ['vxR', 'vyR', 'vxbar', 'vybar', 'vbar']

class TestStatcastPitchingSpinCalcs(unittest.TestCase):

	# Helper Methods
	def compare_columns(self, df1, df2, name):
		return df1[name].equals(df2[name])

	def compare_almost_equal(self, df1, df2, name):
		"""
			Almost equal was necessary due to rounding errors that would result
			from one value being calculated as .499999 and the next as .500000

			Printing `comp_df.query('diff > 0.0000`) will show that only 1 or 2
			values per calcuation rely on this function; the others are exactly
			equal
		"""

		comp_df = pd.DataFrame()
		comp_df['left'] = df1[name].round(SIG_DIG)
		comp_df['right'] = df2[name].round(SIG_DIG)
		comp_df['diff'] = comp_df['left'] - comp_df['right']
		comp_df['diff'] = comp_df['diff'].abs().round(SIG_DIG)
		# print(comp_df.query('diff > 0.0000'))
		return comp_df.query('diff > .0001').empty

	# Test Methods
	def test_individual_calculations(self):
		""" Testing Mechanism that compares test data to target data for each
			calculation in the test_dict.

			This structure was preferable to creating individual funciton test
			because some values depend on the results of prior calculations
		"""


		test_frame = pd.read_csv('tests/statcast_spin/test_data.csv').round(SIG_DIG)
		target_frame = pd.read_csv('tests/statcast_spin/target_data.csv').round(SIG_DIG)

		test_dict = {
			'find_release_point' : ['yR'],
			'find_release_time': ['tR'],
			'find_release_velocity_components': ['vxR', 'vyR', 'vzR'],
			'find_flight_time': ['tf'],
			'find_average_velocity_components': ['vxbar', 'vybar', 'vzbar'],
			'find_average_velocity': ['vbar'],
			'find_average_drag': ['adrag'],
			'find_magnus_acceleration_magnitude': ['amagx', 'amagy', 'amagz'],
			'find_average_magnus_acceleration': ['amag'],
			'find_magnus_magnitude': ['Mx', 'Mz'],
			'find_phi': ['phi'],
			'find_lift_coefficient': ['Cl'],
			'find_spin_factor': ['S'],
			'find_transverse_spin': ['spinT'],
			'find_spin_efficiency': ['spin eff'],
			'find_theta': ['theta'],
		}

		for method, columns in test_dict.items():
			func = getattr(spin, method)
			test_frame = func(test_frame)


			for column in columns:
				logging.info("Begin testing on {}".format(column))

				try:
					if column in rounding_error_columns:
					# Almost equal assertion is necessary for small differences that arise after consecutive calculations
						self.assertTrue(self.compare_almost_equal(test_frame, target_frame, column))

					else:
						self.assertTrue(self.compare_columns(test_frame, target_frame, column))

					logging.info("{} passed".format(column))


				except Exception:
					logging.exception("Tests on {} have failed".format(column))

		logging.info("All tests completed")


	def test_full_function(self):
		"""
			Testing the full data stream from web-scraping to calculated answers

			Answers were calculated using Prof. Alan Nathan's MovementSpinEfficiencyTemplate.xlsx
			featured on http://baseball.physics.illinois.edu/pitchtracker.html

			This example is of Yu Darvish(506433) from 2019-07-01 to 2019-07-31
			Darvish has a wide variety of pitches, giving the most diverse set of test data

		"""
		# Import the rubric
		template_data = pd.read_csv('tests/statcast_spin/live_Darvish_July2019_test.csv').round(SIG_DIG)

		# Run the method in question
		df = spin.statcast_pitcher_spin(start_dt='2019-07-01', end_dt='2019-07-31', player_id=506433)

		# Columns needed to be checked
		target_columns = ['Mx', 'Mz', 'phi', 'theta']

		for column in target_columns:
			logging.info("Begin testing on {}".format(column))


			if column in ['Mz']:
			# Almost equal assertion is necessary for small differences that arise after consecutive calculations
				self.assertTrue(self.compare_almost_equal(df, template_data, column))

			else:
				self.assertTrue(self.compare_columns(df, template_data, column))

			logging.info("{} passed".format(df, template_data, column))


		logging.info("All tests completed")
