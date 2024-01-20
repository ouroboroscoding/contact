/**
 * Senders
 *
 * List of senders in the system
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-16
 */

// Ouroboros modules
import body, { errors } from '@ouroboros/body';
import { Tree } from '@ouroboros/define';
import { Form, Options, Results } from '@ouroboros/define-mui';

// NPM modules
import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Select from '@mui/material/Select';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

// Project modules
import { addError } from 'components/Errors';
import { showSuccess } from 'components/Success';
import { SENDER_BEING_USED } from 'errors';

// Definitions
import SenderDef from 'definitions/admin/sender';

// Generate the Tree
const SenderTree = new Tree(SenderDef, {
	__ui__: {
		__create__: [ 'email_address', 'password', 'host', 'port', 'tls' ],
		__update__: [ 'email_address', 'password', 'host', 'port', 'tls' ],
		__results__: [
			'_created', '_updated', 'email_address', 'host', 'port', 'tls'
		]
	},

	_updated: { __ui__: { __title__: 'Last Updated' } },
	email_address: { __ui__: { __title__: 'E-Mail Address' } },
	password: { __ui__: { __type__: 'password' } },
	tls: { __ui__: { __title__: 'Enable TLS' } }
});

// Constants
const GRID_SIZES = {
	__default__: { xs: 12, md: 6, lg: 4, xl: 3 },
	email_address: { xs: 12, md: 6 },
	password: { xs: 12, md: 6 },
	host: { xs: 12, md: 6 },
	port: { xs: 6, md: 4 },
	tls: { xs: 6, md: 2 }
};

/**
 * Senders
 *
 * Displays current senders with the ability to edit them, or add a new one
 *
 * @name Senders
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Senders(props) {

	// State
	const [ create, createSet ] = useState(false);
	const [ project, projectSet ] = useState('');
	const [ projects, projectsSet ] = useState([]);
	const [ results, resultsSet ] = useState(false);

	// Projects load effect
	useEffect(() => {
		body.read('admin', 'projects').then(projectsSet)
	}, []);

	// Project effect
	useEffect(() => {
		if(project == '') {
			createSet(false);
			resultsSet(false);
		} else {
			body.read('admin', 'senders', {
				'_project': project
			}).then(resultsSet, error => {
				addError(error);
			});
		}
	}, [ project ]);

	// Called when the create form is submitted
	function createSubmit(record) {

		// Add the current project to the record
		record._project = project;

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('admin', 'sender', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				showSuccess('Sender created. Refreshing sender list.');

				// Fetch the latest results
				body.read('admin', 'senders', {
					_project: project
				}).then(resultsSet);

				// Resolve ok
				resolve(true);

			}, error => {
				console.error(error);
				if(error.code === errors.DATA_FIELDS) {
					reject(error.msg);
				} else {
					addError(error);
				}
			});
		});
	}

	// Calle when create button clicked
	function createToggle() {

		// If we're already enabled
		if(create) {
			createSet(false);
		} else {
			if(project === '') {
				showSuccess('Please select a Project first');
			} else {
				createSet(true);
			}
		}
	}

	// Called to delete a sender
	function resultRemove(key) {

		// Send the delete request
		body.delete('admin', 'sender', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				showSuccess('Sender deleted. Refreshing sender list.');

				// Fetch the latest results
				body.read('admin', 'senders', {
					_project: project
				}).then(resultsSet);
			}
		}, error => {
			if(error.code === SENDER_BEING_USED) {
				addError('Sender is still being used by active campaigns: ' +
						JSON.stringify(error.msg, null, 4));
			} else {
				addError(error);
			}
		});
	}

	// Called when a result form is submitted
	function updateSubmit(record, key) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the update request
			body.update('admin', 'sender', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				showSuccess('Sender updated. Refreshing sender list.');

				// Fetch the latest results
				body.read('admin', 'senders', {
					_project: project
				}).then(resultsSet);

				// Resolve ok
				resolve(true);

			}, error => {
				if(error.code === errors.DATA_FIELDS) {
					reject(error.msg);
				} else {
					addError(error);
				}
			});
		});
	}

	// Render
	return (
		<Box id="senders" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Senders</h1>
				<Select
					native
					size="small"
					onChange={ev => projectSet(ev.target.value)}
					value={project}
				>
					<option value="">Select Project...</option>
					{projects.map(o =>
						<option value={o._id}>{o.name}</option>
					)}
				</Select>
				<Tooltip className="flexStatic" title={project !== '' ? 'Create new Sender' : 'Select a Project'}>
					<IconButton onClick={createToggle} className={create ? 'open' : null}>
						<i className="fa-solid fa-circle-plus" />
					</IconButton>
				</Tooltip>
			</Box>
			{create &&
				<Paper>
					<Form
						gridSizes={GRID_SIZES}
						onCancel={() => createSet(false)}
						onSubmit={createSubmit}
						tree={SenderTree}
						type="create"
					/>
				</Paper>
			}
			{(results === false &&
				<Typography>Please select a project</Typography>
			) || (results.length === 0 &&
				<Typography>No Senders found.</Typography>
			) ||
				<Results
					data={results}
					gridSizes={GRID_SIZES}
					onDelete={resultRemove}
					onUpdate={updateSubmit}
					orderBy="email_address"
					tree={SenderTree}
				/>
			}
		</Box>
	);
}

// Valid props
Senders.propTypes = { }