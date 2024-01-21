/**
 * Minutes
 *
 * Fields to allow for entering seconds as minutes
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc.
 * @created 2024-01-20
 */

// Ouroboros modules
import { divmod } from '@ouroboros/tools';

// NPM modules
import PropTypes from 'prop-types';
import React, { useRef } from 'react';
import { v4 } from 'uuid';

// Material UI
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';

/**
 * Minutes
 *
 * Displays the breakdown of minutes and seconds from seconds
 *
 * @name Minutes
 * @access public
 * @param Object props Properties passed to the component
 * @return React.Component
 */
export default function Minutes({ error, label, onChange, value }) {

	// Refs
	const refID = useRef(v4());

	// Called when the minutes change
	function minutes(ev) {

		// Get the new minutes
		const iMinutes = parseInt(ev.target.value);

		// Get the current seconds from the prop
		const iSeconds = value % 60;

		// Return the new value
		onChange((iMinutes * 60) + iSeconds);
	}

	// Called when the seconds change
	function seconds(ev) {

		// Get the current minutes from the prop
		const iMinutes = Math.floor(value / 60);

		// Get the new seconds
		const iSeconds = parseInt(ev.target.value);

		// Return the new value
		onChange((iMinutes * 60) + iSeconds);
	}

	// Options
	const lOptions = [];
	for(let i = 0; i < 60; ++i) {
		lOptions.push(
			<option key={i} value={i}>{i < 10 ? '0' + i : i}</option>
		);
	}

	// Breakdown
	const lBreakdown = divmod(value, 60);

	// Render
	return (
		<Grid container spacing={1}>
			<Grid item xs={6} className="field">
				<FormControl error={error !== false} variant="outlined">
					<InputLabel id={`mins-${refID.current}`}>{`${label} - Minutes`}</InputLabel>
					<Select
						label={`${label} - Minutes`}
						labelId={`mins-${refID.current}`}
						native
						onChange={minutes}
						value={lBreakdown[0]}
					>
						{Array(60).fill(null).map((v,i) =>
							<option key={i} value={i}>{i}</option>
						)}
					</Select>
					{error &&
						<FormHelperText>{error}</FormHelperText>
					}
				</FormControl>
			</Grid>
			<Grid item xs={6} className="field">
				<FormControl error={error !== false} variant="outlined">
					<InputLabel id={`secs-${refID.current}`}>Seconds</InputLabel>
					<Select
						label="Seconds"
						labelId={`secs-${refID.current}`}
						native
						onChange={seconds}
						value={lBreakdown[1]}
					>
						{Array(60).fill(null).map((v,i) =>
							<option key={i} value={i}>{i < 10 ? '0' + i : i}</option>
						)}
					</Select>
					{error &&
						<FormHelperText>{error}</FormHelperText>
					}
				</FormControl>
			</Grid>
		</Grid>
	);
}

// Valid props
Minutes.validProps = {
	error: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),
	label: PropTypes.string,
	onChange: PropTypes.func.isRequired,
	value: PropTypes.number.isRequired
}

// Default props
Minutes.defaultProps = {
	error: false,
	label: 'Minutes'
}