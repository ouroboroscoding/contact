/**
 * Categories
 *
 * List of categories in the system
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
import CategoryDef from 'definitions/contact/category';

// Project options
const ProjectOptions = new Options.Custom();

// Generate the Tree
const CategoryTree = new Tree(CategoryDef, {
	__ui__: {
		__create__: [ 'name' ],
		__update__: [ 'name' ],
		__results__: [ '_created', '_updated', '_project', 'name' ]
	},

	_updated: { __ui__: { __title__: 'Last Updated' } },
	_project: { __ui__: { __options__: ProjectOptions } },
	name: { __ui__: { __title__: 'Category Name' } }
});

// Constants
const GRID_SIZES = {
	__default__: { xs: 12, md: 6 }
};

/**
 * Categories
 *
 * Displays current categories with the ability to edit them, or add a new one
 *
 * @name Categories
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Categories(props) {

	// State
	const [ create, createSet ] = useState(false);
	const [ project, projectSet ] = useState('');
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
			createSet(false);
			resultsSet(false);
		} else {
			body.read('contact', 'categories', {
				'_project': project
			}).then(resultsSet, Message.error);
		}
	}, [ project ]);

	// Called when the create form is submitted
	function createSubmit(record) {

		// Add the current project to the record
		record._project = project;

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('contact', 'category', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				Message.success('Category created. Refreshing category list.');

				// Fetch the latest results
				body.read('contact', 'categories', {
					'_project': project
				}).then(resultsSet, Message.error);

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

	// Calle when create button clicked
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

	// Called to delete a category
	function resultRemove(key) {

		// Send the delete request
		body.delete('contact', 'category', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				Message.success('Category deleted. Refreshing category list.');

				// Fetch the latest results
				body.read('contact', 'categories', {
					'_project': project
				}).then(resultsSet, Message.error);
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
			body.update('contact', 'category', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				Message.success('Category updated. Refreshing category list.');

				// Fetch the latest results
				body.read('contact', 'categories', {
					'_project': project
				}).then(resultsSet, Message.error);

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
		<Box id="categories" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Categories</h1>
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
				<Tooltip className="flexStatic" title={project !== '' ? 'Create new Category' : 'Select a Project'}>
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
						tree={CategoryTree}
						type="create"
					/>
				</Paper>
			}
			{(results === false &&
				<Typography>Please select a project</Typography>
			) || (results.length === 0 &&
				<Typography>No Categories found.</Typography>
			) ||
				<Results
					data={results}
					gridSizes={GRID_SIZES}
					onDelete={resultRemove}
					onUpdate={updateSubmit}
					orderBy="name"
					tree={CategoryTree}
				/>
			}
		</Box>
	);
}

// Valid props
Categories.propTypes = { }