/**
 * Projects
 *
 * List of projects in the system
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-13
 */

// Ouroboros modules
import body, { errors } from '@ouroboros/body';
import { Tree } from '@ouroboros/define';
import { Form, Results } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

// Project modules
import Message from 'message';

// Definitions
import ProjectDef from 'definitions/contact/project';

// Generate the Tree
const ProjectTree = new Tree(ProjectDef, {
	__ui__: {
		__create__: [ 'name', 'short_code', 'description' ],
		__update__: [ 'name', 'description' ],
		__results__: [
			'_id', '_created', '_updated', 'name', 'short_code', 'description'
		]
	},

	_id: { __ui__: { __title__: 'ID' } },
	_updated: { __ui__: { __title__: 'Last Updated' } },
	name: { __ui__: { __title__: 'Project Name' } },
	short_code: { __ui__: { __title__: 'Short Code ( 3 or 4 letters )' } }
});

// Constants
const GRID_SIZES = {
	__default__: { xs: 12 },
	name: { xs: 12, md: 9 },
	short_code: { xs: 12, md: 3 }
};

// Filter short codes
function shortCodeFilter(ev) {
	const s = ev.data.short_code.toUpperCase().split('').filter(
		c => (c >= 'A' && c <= 'Z')
	).join('')
	return { short_code: s }
}

/**
 * Projects
 *
 * Displays current projects with the ability to edit them, or add a new one
 *
 * @name Projects
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Projects(props) {

	// State
	const [ create, createSet ] = useState(false);
	const [ results, resultsSet ] = useState(false);

	// Load effect
	useEffect(() => {

		// Fetch the projects from the server
		body.read('contact', 'projects').then(resultsSet);

	}, []);

	// Called when the create form is submitted
	function createSubmit(record) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('contact', 'project', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				Message.success('Project created. Refreshing project list.');

				// Fetch the latest results
				body.read('contact', 'projects').then(resultsSet);

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

	// Called to delete a project
	function resultRemove(key) {

		// Send the delete request
		body.delete('contact', 'project', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				Message.success('Project deleted. Refreshing project list.');

				// Fetch the latest results
				body.read('contact', 'projects').then(resultsSet);
			}
		}, error => {
			Message.error(error);
		});
	}

	// Called when a result form is submitted
	function updateSubmit(record, key) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the update request
			body.update('contact', 'project', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				Message.success('Project updated. Refreshing project list.');

				// Fetch the latest results
				body.read('contact', 'projects').then(resultsSet);

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
		<Box id="projects" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Projects</h1>
				<Tooltip className="flexStatic" title="Create new Project">
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
						onNodeChange={{ short_code: shortCodeFilter }}
						onSubmit={createSubmit}
						tree={ProjectTree}
						type="create"
					/>
				</Paper>
			}
			{(results === false &&
				<Typography>Loading...</Typography>
			) || (results.length === 0 &&
				<Typography>No Projects found.</Typography>
			) ||
				<Results
					data={results}
					gridSizes={GRID_SIZES}
					onDelete={resultRemove}
					onUpdate={updateSubmit}
					onNodeChange={{ short_code: shortCodeFilter }}
					orderBy="name"
					tree={ProjectTree}
				/>
			}
		</Box>
	);
}

// Valid props
Projects.propTypes = { }