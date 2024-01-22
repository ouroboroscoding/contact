/**
 * Success
 *
 * Handles displaying a temporary success message
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2023-01-17
 */

// Ouroboros modules
import events from '@ouroboros/events';

// NPM modules
import React, { useEffect, useState } from 'react';

// Material UI
import IconButton from '@mui/material/IconButton';
import Slide from '@mui/material/Slide';
import Snackbar from '@mui/material/Snackbar';
import Typography from '@mui/material/Typography';

/**
 * Success
 *
 * Handles the snackbar
 *
 * @name Success
 * @access public
 * @param Object props Properties passed to the component
 * @return React.Component
 */
export default function Success(props) {

	// State
	let [message, messageSet] = useState(false);

	// Load effect
	useEffect(() => {

		// Track success events
		events.get('success').subscribe(messageSet);

		// Clean up
		return () => {
			events.get('success').unsubscribe(messageSet);
		}
	}, []);

	// If we have no message, do nothing
	if(!message) {
		return '';
	}

	// Render
	return (
		<Snackbar
			action={
				<React.Fragment>
					<IconButton
						color="inherit"
						onClick={() => messageSet(false)}
					>
						<i className="fas fa-times-circle"/>
					</IconButton>
				</React.Fragment>
			}
			anchorOrigin={{
				vertical: 'bottom',
				horizontal: 'center',
			}}
			message={message.split('\n').map((s,i) => <Typography key={i}>{s}</Typography>)}
			onClose={() => messageSet(false)}
			open={true}
			TransitionComponent={(props) => <Slide {...props} direction="up" />}
			transitionDuration={1000}
			TransitionProps={{
				onExited: () => messageSet(false)
			}}
		/>
	);
}