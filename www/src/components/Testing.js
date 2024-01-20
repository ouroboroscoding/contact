/**
 * Testing
 *
 * Shows a testing component with site info
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc.
 * @created 2023-05-19
 */

// NPM modules
//import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';

// Material UI
import { useWidth } from 'hooks/mui';

/**
 * Testing
 *
 * @name Testing
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Testing(props) {

	// State
	const [display, displaySet] = useState('closed');

	// Hooks
	const location = useLocation();
	const width = useWidth();

	// If it's closed
	if(display === 'closed') {
		return (
			<div id="testing" className="closed">
				<button onClick={() => displaySet('open')}>T</button>
			</div>
		);
	}

	// Render
	return (
		<div id="testing" className="open">
			<button onClick={() => displaySet('closed')}>X</button>
			<p>Version: {process.env.REACT_APP_VERSION}</p>
			<p>Location: {location.pathname}</p>
			<p>Width: {width}</p>
		</div>
	)
}

// Valid props
Testing.propTypes = {}