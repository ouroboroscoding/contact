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
import { safeLocaleStorage } from '@ouroboros/browser';
import { Tree } from '@ouroboros/define';
import { Form, Options, Results } from '@ouroboros/define-mui';

// NPM modules
import { convertCSVToArray } from 'convert-csv-to-array';
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

// Project modules
import Message from 'message';

// Definitions
import ContactDef from 'definitions/contact/contact';
import { arrayFindDelete } from '@ouroboros/tools';

// Init category options
const CategoryOptions = new Options.Custom();
const ProjectOptions = new Options.Custom();

// Generate the Tree
const ContactTree = new Tree(ContactDef, {
	__ui__: {
		__create__: [
			'email_address', 'name', 'alias', 'company', 'categories'
		],
		__update__: [
			'email_address', 'name', 'alias', 'company', 'categories'
		],
		__results__: [
			'_id', '_created', '_updated', '_project', 'name', 'company'
		]
	},

	_id: { __ui__: { __title__: 'ID' } },
	_updated: { __ui__: { __title__: 'Last Updated' } },
	_project: { __ui__: { __options__: ProjectOptions } },
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
	const [ cats, catsSet ] = useState(false);
	const [ create, createSet ] = useState(false);
	const [ csv, csvSet ] = useState(false);
	const [ project, projectSet ] = useState(safeLocalStorage.string('project', ''));
	const [ projects, projectsSet ] = useState([]);
	const [ results, resultsSet ] = useState(false);

	// Projects load effect
	useEffect(() => {
		body.read('contact', 'projects').then(data => {
			ProjectOptions.set(data.map(o => [ o._id, o.name ]));
			projectsSet(data);
		}, Message.error);
	}, []);

	// Project effect
	useEffect(() => {
		if(project === '') {
			catsSet(false);
			createSet(false);
			csvSet(false);
			resultsSet(false);
			CategoryOptions.set([]);
		} else {

			body.read('contact', '__list', [
				[ 'contacts', { '_project': project } ],
				[ 'categories', { '_project': project } ]
			]).then(data => {
				resultsSet(data[0][1].data);
				catsSet(data[1][1].data.reduce((o, l) => Object.assign(o, {[l.name]: l._id}), {}));
				CategoryOptions.set(data[1][1].data.map(o => [ o._id, o.name ]))
			}, Message.error);
		}
	}, [ project ]);

	// Called when create button clicked
	function createToggle() {

		// If we're already enabled
		if(create) {
			createSet(false);
		} else {
			if(project === '') {
				Message.success('Please select a Project first');
			} else {
				createSet(true);
			}
		}
	}

	// Called when csv button clicked
	function csvToggle() {

		// If we're already enabled
		if(csv) {
			csvSet(false);
		} else {
			if(project === '') {
				Message.success('Please select a Project first');
			} else {
				csvSet('');
			}
		}
	}

	// Called when the create form is submitted
	function createSubmit(record) {

		// Add the current project to the record
		record._project = project;

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('contact', 'contact', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				Message.success('Contact created. Refreshing contact list.');

				// Fetch the latest results
				body.read('contact', 'contacts', {
					'_project': project
				}).then(resultsSet, Message.error);

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

	// Called to create the records from the CSV
	function csvSubmit() {

		// Add the header and the actual CSV
		const sContent = 'email_address,name,alias,company,categories\n' + csv.trim() + '\n';

		// Convert it to an array of objects
		const lContacts = convertCSVToArray(sContent, {
			header: false,
			type: 'object',
			separator: ','
		});

		// Go through each contact
		for(const o of lContacts) {
			if(o.categories in cats) {
				o.categories = [ cats[o.categories] ]
			} else {
				delete o.categories;
			}
		}

		// Send the data to the server
		body.create('contact', 'contacts', {
			_project: project,
			records: lContacts
		}).then(data => {

			// Close the csv form
			csvSet(false);

			// Notify the user
			Message.success('Contacts created. Refreshing contact list.');

			// Fetch the latest results
			body.read('contact', 'contacts', {
				'_project': project
			}).then(resultsSet, Message.error);

		}, Message.error);
	}

	// Called to delete a contact
	function resultRemove(key) {

		// Send the delete request
		body.delete('contact', 'contact', { _id: key }).then(data => {
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
			body.update('contact', 'contact', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				Message.success('Contact updated. Refreshing contact list.');

				// Fetch the latest results
				body.read('contact', 'contacts', {
					'_project': project
				}).then(resultsSet, Message.error);

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

	// Render
	return (
		<Box id="contacts" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Contacts</h1>
				<Select
					native
					size="small"
					onChange={ev => {
						projectSet(ev.target.value);
						localStorage.setItem('project', ev.target.value);
					}}
					value={project}
				>
					<option value="">Select Project...</option>
					{projects.map(o =>
						<option value={o._id}>{o.name}</option>
					)}
				</Select>
				<Tooltip className="flexStatic" title={project !== '' ? 'Import CSV' : 'Select a Project'}>
					<IconButton onClick={csvToggle} className={csv ? 'open' : null}>
						<i className="fa-solid fa-file-csv" />
					</IconButton>
				</Tooltip>
				<Tooltip className="flexStatic" title={project !== '' ? 'Create new Contact' : 'Select a Project'}>
					<IconButton onClick={createToggle} className={create !== false ? 'open' : null}>
						<i className="fa-solid fa-circle-plus" />
					</IconButton>
				</Tooltip>
			</Box>
			{csv !== false &&
				<Paper className="padding">
					<Typography>Enter CSV text below</Typography>
					<Box className="field">
						<TextField
							onChange={ev => csvSet(ev.target.value)}
							multiline={true}
							value={csv}
							variant="outlined"
						/>
					</Box>
					<br />
					<Box className="actions">
						<Button
							color="primary"
							onClick={csvSubmit}
							variant="contained"
						>Add Contacts</Button>
					</Box>
				</Paper>
			}
			{create &&
				<Paper className="padding">
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