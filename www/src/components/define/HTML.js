/**
 * HTML
 *
 * Used for WYSIWYG editor
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc.
 * @created 2022-04-26
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
import HTML from 'components/elements/HTML';

/**
 * NodeHTML
 *
 * Handles writing WYSIWYG HTML content
 *
 * @name NodeHTML
 * @access public
 * @extends NodeBase
 */
class NodeHTML extends DefineNodeBase {

	// Constructor
	constructor(props) {

		// Call the parent
		super(props);

		// Init state
		this.state = {
			error: props.error,
			value: props.value
		}
	}

	// Render
	render() {
		return (
			<FormControl
				className={`field_${this.props.name} nodeHTML`}
				error={this.state.error !== false}
				variant={this.props.variant}
			>
				<InputLabel
					id={this.props.name}
					shrink={true}
				>
					{this.props.display.__title__}
				</InputLabel>
				<HTML
					onChange={val => this.setState({ value: val })}
					value={this.state.value}
				/>
				{this.state.error &&
					<FormHelperText>{this.state.error}</FormHelperText>
				}
			</FormControl>
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
DefineNodeBase.pluginAdd('html', NodeHTML);

// Valid props
NodeHTML.propTypes = {
	error: PropTypes.oneOfType([ PropTypes.bool, PropTypes.string ]),
	value: PropTypes.string
}

// Default props
NodeHTML.defaultProps = {
	error: false,
	value: ''
}