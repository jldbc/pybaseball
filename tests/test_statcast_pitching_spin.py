import pybaseball.statcast_pitcher_spin as spin
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import logging

rounding_error_columns = ['vxR', 'vyR', 'vxbar', 'vybar', 'vbar']


class TestStatcastPitchingSpinCalcs(unittest.TestCase):

	# Test Methods
	def test_individual_calculations(self):
		""" Testing Mechanism that compares test data to target data for each
			calculation in the test_dict.

			This structure was preferable to creating individual funciton test
			because some values depend on the results of prior calculations
		"""

		test_frame = pd.read_csv('tests/statcast_spin/test_data.csv')
		target_frame = pd.read_csv('tests/statcast_spin/target_data.csv')

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
				left = test_frame.loc[:, [column]]
				right = target_frame.loc[:, [column]]
				assert_frame_equal(left, right, check_dtype=False)


	def test_full_function(self):
		"""
			Testing the full data stream from web-scraping to calculated answers

			Answers were calculated using Prof. Alan Nathan's MovementSpinEfficiencyTemplate.xlsx
			featured on http://baseball.physics.illinois.edu/pitchtracker.html

			This example is of Yu Darvish(506433) from 2019-07-01 to 2019-07-31
			Darvish has a wide variety of pitches, giving the most diverse set of test data

		"""
		# Import the rubric
		template_data = pd.read_csv('tests/statcast_spin/live_Darvish_Feb2021_test.csv')

		# Run the method in question
		df = spin.statcast_pitcher_spin(start_dt='2019-07-01', end_dt='2019-07-31', player_id=506433)

		# Columns needed to be checked
		target_columns = ['Mx', 'Mz', 'phi', 'theta']

		for column in target_columns:
			left = template_data.loc[:, [column]]
			right = df.loc[:, [column]]
			assert_frame_equal(left, right)
