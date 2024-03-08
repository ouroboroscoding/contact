/**
 * Campaigns: Existing
 *
 * Shows existing campaigns
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-20
 */

// Ouroboros modules
import body from '@ouroboros/body';
import { safeLocaleStorage } from '@ouroboros/browser';
import { Tree } from '@ouroboros/define';
import { Options, Results } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';

// Material UI
import Box from '@mui/material/Box';
import Select from '@mui/material/Select';
import Typography from '@mui/material/Typography';

// Project modules
import Message from 'message';

// Definitions
import CampaignDef from 'definitions/contact/campaign';

// Project options
const ProjectOptions = new Options.Custom();

// Generate the Tree
const CampaignTree = new Tree(CampaignDef, {
	__ui__: {
		__results__: [ '_id', '_created', '_updated', '_project', 'name' ]
	},

	_id: { __ui__: { __title__: 'ID' } },
	_updated: { __ui__: { __title__: 'Last Updated' } },
	_project: { __ui__: { __options__: ProjectOptions } },
	name: { __ui__: { __title__: 'Campaign Name' } }
});

/**
 * Campaigns: Existing
 *
 * @name CampaignsExisting
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function CampaignsExisting(props) {

	// State
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
			resultsSet(false);
		} else {
			body.read('contact', 'campaigns', {
				'_project': project
			}).then(resultsSet, Message.error);
		}
	}, [ project ]);

	// Called to delete a campaign
	function resultRemove(key) {

		// Send the delete request
		body.delete('contact', 'campaign', { _id: key }).then(data => {
			if(data) {

				// Notify the user
				Message.success('Campaign deleted. Refreshing campaign list.');

				// Fetch the latest results
				body.read('contact', 'campaigns', {
					'_project': project
				}).then(resultsSet, Message.error);
			}
		}, error => {
			Message.error(error);
		});
	}

	// Render
	return (
		<Box id="categories" className="flexDynamic padding">
			<Box className="pageHeader flexColumns">
				<h1 className="flexDynamic">Existing Campaigns</h1>
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
						<option key={o._id} value={o._id}>{o.name}</option>
					)}
				</Select>
			</Box>
			{(results === false &&
				<Typography>Please select a project</Typography>
			) || (results.length === 0 &&
				<Typography>No Campaigns found.</Typography>
			) ||
				<Results
					actions={[{
						dynamic: row => ({
							url: `/campaigns/${row._id}`
						}),
						icon: 'fa-solid fa-magnifying-glass',
						tooltip: 'View Campaign',
					}]}
					data={results}
					onDelete={resultRemove}
					orderBy="name"
					tree={CampaignTree}
				/>
			}
		</Box>
	);
}

// Valid props
CampaignsExisting.propTypes = { }