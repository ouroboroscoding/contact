/**
 * Message
 *
 * Handles adding success and error messgaes
 *
 * @author Chris Nasr
 * @copyright Ouroboros Coding Inc.
 * @created 2024-01-20
 */

// Ouroboros modules
import events from '@ouroboros/events';

/**
 * Success
 *
 * Adds a message to the snackbar
 *
 * @name success
 * @access public
 * @param {string} msg The message to add
 * @returns void
 */
export function success(msg) {
	events.get('success').trigger(msg);
}

/**
 * Error
 *
 * Adds a message or structure to the error list
 *
 * @name error
 * @access public
 * @param {string | object} error The error to add
 * @returns void
 */
export function error(error) {
	events.get('error').trigger(error);
}

// Default export
const Message = { error, success }
export default Message;