/**
 * Minutes
 *
 * Used for setting minutes by min/sec
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc.
 * @created 2024-02-06
 */

// Ouroboros Modules
import { DefineNodeBase } from '@ouroboros/define-mui';

// NPM modules
import PropTypes from 'prop-types';
import React from 'react';

// Material UI
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';

// Project components
import Minutes from 'components/elements/Minutes';

/**
 * NodeMinutes
 *
 * @name NodeMinutes
 * @access public
 * @extends NodeBase
 */
class NodeMinutes extends DefineNodeBase {

	// Constructor
	constructor(props) {

		// Call the parent
		super(props);

		// Init state
		this.state = {
			error: false,
			value: props.value
		}
	}

	// Render
	render() {
		return (
			<Minutes
				error={this.state.error}
				label={this.props.display.__title__}
				onChange={val => this.setState({ value: val })}
				value={this.state.value}
			/>
		);
	}

	get value() {
		return this.state.value;
	}

	set value(val) {
		this.setState({ value: val });
	}
}

// Register with Node
DefineNodeBase.pluginAdd('minutes', NodeMinutes);

// Valid props
NodeMinutes.propTypes = {
	value: PropTypes.string
}

// Default props
NodeMinutes.defaultProps = {
	value: ''
}