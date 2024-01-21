/**
 * Campaigns: New
 *
 * Create a new, paused, campaign
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-20
 */

// Ouroboros modules
import body, { errors } from '@ouroboros/body';
import { Tree } from '@ouroboros/define';
import { DefineNode } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';
import { Editor } from '@tinymce/tinymce-react';

// Material UI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';

// Project components
import HTML from 'components/elements/HTML';
import Minutes from 'components/elements/Minutes';

// Project modules
import Message from 'message';

// Load Campaign definition
import CampaignDef from 'definitions/admin/campaign';

// Create the tree
const CampaignTree = new Tree(CampaignDef, {
	subject: { __ui__: { __title__: 'E-Mail Subject Template'}}
});

/**
 * Campaign New
 *
 * @name CampaignNew
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function CampaignNew(props) {

	// State
	const [ content, contentSet ] = useState('');
	const [ errors, errorsSet ] = useState({});
	const [ minMax, minMaxSet ] = useState([ 300, 600 ]);
	const [ name, nameSet ] = useState('');
	const [ project, projectSet ] = useState('-1');
	const [ projects, projectsSet ] = useState([]);
	const [ sender, senderSet ] = useState('-1');
	const [ senders, sendersSet ] = useState([]);
	const [ subject, subjectSet ] = useState('');

	// Projects load effect
	useEffect(() => {
		body.read('admin', 'projects').then(projectsSet, Message.error);
	}, []);

	// Project effect
	useEffect(() => {
		if(project === '-1') {
			sendersSet([]);
		} else {
			body.read('admin', 'senders', { _project: project }).then(
				sendersSet, Message.error
			);
		}

	}, [ project ]);

	// Called when either the min or max is changed
	function minMaxChange(which, value) {

		// Make sure the value is an int
		value = parseInt(value);

		// Get latest values
		minMaxSet(l => {

			// If the minimum changed
			if(which === 'min') {

				// If the new value is greater than the maximum, change it
				if(value >= l[1]) {
					value = l[1] - 1;

					// If the changed value is less than zero, change both
					if(value < 0) {
						value = 0;
						l[1] = 1;
					}
				}

				// Set the new values
				return [ value, l[1] ];
			}

			// Else, if the maximum changed
			else if(which === 'max') {

				// If the new value is less than the minimum, change it
				if(value <= l[0]) {
					value = l[0] + 1;
				}

				// Set the new values
				return [ l[0], value ];
			}
		});
	}

	// Called when the create form is submitted
	function submit(record) {

	}

	// Render
	return (
		<Box id="campaignNew" className="flexDynamic padding">
			<Box className="pageHeader">
				<h1>New Campaign</h1>
			</Box>
			<Grid container spacing={2} className="campaignForm">
				<Grid item xs={12} md={6} className="field">
					<FormControl error={errors._project && errors._project !== false} variant="outlined">
						<InputLabel id="campaignNewProject">Project</InputLabel>
						<Select
							label="Project"
							labelId="campaignNewProject"
							native
							onChange={ev => projectSet(ev.target.value)}
							value={project}
						>
							<option value="-1">Select Project...</option>
							{projects.map(o =>
								<option key={o._id} value={o._id}>{o.name}</option>
							)}
						</Select>
						{errors._project &&
							<FormHelperText>{errors._project}</FormHelperText>
						}
					</FormControl>
				</Grid>
				{project !== '-1' && <>
					<Grid item xs={12} md={6} className="field">
						<FormControl error={errors._project && errors._project !== false} variant="outlined">
							<InputLabel id="campaignNewSender">Sender</InputLabel>
							<Select
								label="Sender"
								labelId="campaignNewSender"
								native
								onChange={ev => senderSet(ev.target.value)}
								value={sender}
							>
								<option value="">Select Sender...</option>
								{senders.map(o =>
									<option key={o.email_address} value={o._id}>{o.email_address}</option>
								)}
							</Select>
							{errors._sender &&
								<FormHelperText>{errors._sender}</FormHelperText>
							}
						</FormControl>
					</Grid>
					{sender !== '-1' && <>
						<Grid item xs={12} md={4} className="field">
							<DefineNode
								name="name"
								node={CampaignTree.get('name')}
								onChange={nameSet}
								type="create"
								value={name}
							/>
						</Grid>
						<Grid item xs={12} md={4}>
							<Minutes
								label="Minimum Interval"
								onChange={val => minMaxChange('min', val)}
								value={minMax[0]}
							/>
						</Grid>
						<Grid item xs={12} md={4}>
							<Minutes
								label="Maxmimum Interval"
								onChange={val => minMaxChange('max', val)}
								value={minMax[1]}
							/>
						</Grid>
						<Grid item xs={12} className="field">
							<DefineNode
								name="subject"
								node={CampaignTree.get('subject')}
								onChange={subjectSet}
								type="create"
								value={subject}
							/>
						</Grid>
						<Grid item xs={12} className="field">
							<span className="fakeMuiLabel">E-Mail Content Template</span>
							<HTML
								onChange={contentSet}
								value={content}
							/>
						</Grid>
					</>}
				</>}
			</Grid>
		</Box>
	);
}

// Valid props
CampaignNew.propTypes = { }