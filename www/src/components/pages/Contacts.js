/**
 * Contacts
 *
 * List contacts in the system
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-14
 */

// Ouroboros modules
import body, { errors } from '@ouroboros/body';
import { Tree } from '@ouroboros/define';
import { Form, Options, Results } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Select from '@mui/material/Select';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

// Project modules
import Message from 'message';

// Definitions
import ContactDef from 'definitions/admin/contact';
import { arrayFindDelete, arrayFindMerge } from '@ouroboros/tools';

// Init category options
const CategoryOptions = new Options.Custom();

// Generate the Tree
const ContactTree = new Tree(ContactDef, {
	__ui__: {
		__create__: [
			'email_address', 'name', 'alias', 'company', 'categories'
		],
		__update__: [
			'email_address', 'name', 'alias', 'company', 'categories'
		],
		__results__: [ '_created', '_updated', 'name', 'company' ]
	},

	_updated: { __ui__: { __title__: 'Last Updated' } },
	email_address: { __ui__: { __title__: 'E-Mail Address' } },
	name: { __ui__: { __title__: 'Full Name' } },

	categories: {
		__ui__: { __header__: 'Categories' },
		__type__: {
			__ui__: {
				__title__: 'Category',
				__type__: 'select',
				__options__: CategoryOptions
			}
		}
	}
});

// Constants
const GRID_SIZES = {
	__default__: { xs: 12 },
	_project: { xs: 12 },
	email_address: { xs: 12, md: 6, xl: 3 },
	name: { xs: 12, md: 6, xl: 3 },
	alias: { xs: 12, md: 4, xl: 3 },
	company: { xs: 12, md: 8, xl: 3 },
	categories: { xs: 12, md: 6, xl: 3 }
};

/**
 * Contacts
 *
 * Displays current contacts with the ability to edit them, or add a new one
 *
 * @name Contacts
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Contacts(props) {

	// State
	const [ create, createSet ] = useState(false);
	const [ project, projectSet ] = useState('');
	const [ projects, projectsSet ] = useState([]);
	const [ results, resultsSet ] = useState(false);

	// Projects load effect
	useEffect(() => {
		body.read('admin', 'projects').then(
			data => projectsSet(data.map(o => [ o._id, o.name ])),
			Message.error
		);
	}, []);

	// Project effect
	useEffect(() => {
		if(project === '') {
			createSet(false);
			resultsSet(false);
			CategoryOptions.set([]);
		} else {
			body.read('admin', '__list', [
				[ 'contacts', { '_project': project } ],
				[ 'categories', { '_project': project } ]
			]).then(data => {
				resultsSet(data[0][1].data);
				CategoryOptions.set(data[1][1].data.map(o => [ o._id, o.name ]))
			}, Message.error);
		}
	}, [ project ]);

	// Called when the create form is submitted
	function createSubmit(record) {

		// Add the current project to the record
		record._project = project;

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('admin', 'contact', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				Message.success('Contact created. Refreshing contact list.');

				// Fetch the latest results
				body.read('admin', 'contacts', {
					'_project': project
				}).then(resultsSet, error => {
					Message.error(error);
				});

				// Resolve ok
				resolve(true);

			}, error => {
				if(error.code === errors.DATA_FIELDS) {
					reject(error.msg);
				} else {
					Message.error(error);
				}
			});
		});
	}

	// Called to delete a contact
	function resultRemove(key) {

		// Send the delete request
		body.delete('admin', 'contact', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				Message.success('Contact deleted. Refreshing contact list.');

				// Find the record and remove it
				resultsSet(l => arrayFindDelete(l, '_id', key, true));
			}
		}, Message.error);
	}

	// Called when a result form is submitted
	function updateSubmit(record, key) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the update request
			body.update('admin', 'contact', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				Message.success('Contact updated. Refreshing contact list.');

				// Fetch the latest results
				body.read('admin', 'contacts', {
					'_project': project
				}).then(resultsSet, error => {
					Message.error(error);
				});

				// Resolve ok
				resolve(true);

			}, error => {
				console.error(error);
				if(error.code === errors.DATA_FIELDS) {
					reject(error.msg);
				} else {
					Message.error(error);
				}
			});
		});
	}

	// Render
	return (
		<Box id="contacts" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Contacts</h1>
				<Select
					native
					size="small"
					onChange={ev => projectSet(ev.target.value)}
					value={project}
				>
					<option value="">Select Project...</option>
					{projects.map(l =>
						<option value={l[0]}>{l[1]}</option>
					)}
				</Select>
				<Tooltip className="flexStatic" title="Create new Contact">
					<IconButton onClick={() => createSet(b => !b)} className={create ? 'open' : null}>
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
						tree={ContactTree}
						type="create"
					/>
				</Paper>
			}
			{(results === false &&
				<Typography>Please select a project</Typography>
			) || (results.length === 0 &&
				<Typography>No Contacts found.</Typography>
			) ||
				<Results
					data={results}
					gridSizes={GRID_SIZES}
					onDelete={resultRemove}
					onUpdate={updateSubmit}
					orderBy="name"
					tree={ContactTree}
				/>
			}
		</Box>
	);
}

// Valid props
Contacts.propTypes = { }