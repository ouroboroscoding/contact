/**
 * Body Init
 *
 * Initialises body module by setting domain and adding callbacks
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2023-01-17
 */

// Ouroboros modules
import body from '@ouroboros/body';
import events from '@ouroboros/events';

// Set the body domain
body.domain = process.env.REACT_APP_REST_DOMAIN || `rest.${window.location.domain}`;

// Set callbacks for errors and no session
body.onError((error, info) => {
	events.get('error').trigger(
		(typeof error === 'string') ? error : JSON.stringify(error, null, 4)
	);
	console.error(error, info);
});
body.onErrorCode((error, info) => {
	let message = '';
	switch(error.code) {
		case 207:
			message = `${info.url} crashed. Please see administrator`;
			break;
		case 208:
			message = `${info.url} requires data to be sent`;
			break;
		case 209:
			message = `${info.url} requires a session`;
			break;
		default:
			console.error(error, info);
			return false;
	}

	// Notify the user
	events.get('error').trigger(message);
});