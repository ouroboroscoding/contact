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
import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

// Project modules
import { addError } from 'components/Errors';
import { showSuccess } from 'components/Success';

// Definitions
import CategoryDef from 'definitions/admin/category';

// Generate the project options
const ProjectOptions = new Options.Fetch(() => {
	return new Promise((resolve, reject) => {
		body.read('admin', 'projects').then(resolve, error => {
			addError(error);
		});
	});
});

// Generate the Tree
const CategoryTree = new Tree(CategoryDef, {
	__ui__: {
		__create__: [ '_project', 'name' ],
		__update__: [ 'name' ],
		__results__: [ '_created', '_updated', '_project', 'name' ]
	},

	_updated: { __ui__: { __title__: 'Last Updated' } },
	_project: { __ui__: {
		__options__: ProjectOptions,
		__title__: 'Project',
		__type__: 'select'
	}},
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
	const [ results, resultsSet ] = useState(false);

	// Load effect
	useEffect(() => {

		// Fetch the categories from the server
		body.read('admin', 'categories').then(resultsSet);

	}, []);

	// Called when the create form is submitted
	function createSubmit(record) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the create request
			body.create('admin', 'category', { record }).then(data => {

				// Close the create form
				createSet(false);

				// Notify the user
				showSuccess('Category created. Refreshing category list.');

				// Fetch the latest results
				body.read('admin', 'categories').then(resultsSet);

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

	// Called to delete a category
	function resultRemove(key) {

		// Send the delete request
		body.delete('admin', 'category', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				showSuccess('Category deleted. Refreshing category list.');

				// Fetch the latest results
				body.read('admin', 'categories').then(resultsSet);
			}
		}, error => {
			addError(error);
		});
	}

	// Called when a result form is submitted
	function updateSubmit(record, key) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the update request
			body.update('admin', 'category', {
				_id: key,
				record
			}).then(data => {

				// Notify the user
				showSuccess('Category updated. Refreshing category list.');

				// Fetch the latest results
				body.read('admin', 'categories').then(resultsSet);

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

	// Render
	return (
		<Box id="categories" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Categories</h1>
				<Tooltip className="flexStatic" title="Create new Category">
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
						tree={CategoryTree}
						type="create"
					/>
				</Paper>
			}
			{(results === false &&
				<Typography>Loading...</Typography>
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
Categories.propTypes = {
	mobile: PropTypes.bool.isRequired
}