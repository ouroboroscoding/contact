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
import RadioButtons from '@ouroboros/react-radiobuttons-mui'
import { pathToTree } from '@ouroboros/tools';

// NPM modules
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Material UI
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormHelperText from '@mui/material/FormHelperText';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import Switch from '@mui/material/Switch';

// Project components
import HTML from 'components/elements/HTML';
import Minutes from 'components/elements/Minutes';

// Project modules
import Message from 'message';

// Load Campaign definition
import CampaignDef from 'definitions/contact/campaign';

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
	const [ categories, categoriesSet ] = useState([]);
	const [ contacts, contactsSet ] = useState('all')
	const [ contactsList, contactsListSet ] = useState([]);
	const [ content, contentSet ] = useState('');
	const [ errs, errsSet ] = useState({});
	const [ minMax, minMaxSet ] = useState([ 300, 600 ]);
	const [ name, nameSet ] = useState('');
	const [ project, projectSet ] = useState('-1');
	const [ projects, projectsSet ] = useState([]);
	const [ sender, senderSet ] = useState('-1');
	const [ senders, sendersSet ] = useState([]);
	const [ subject, subjectSet ] = useState('');

	// Hooks
	const navigate = useNavigate();

	// Projects load effect
	useEffect(() => {
		body.read('contact', 'projects').then(projectsSet, Message.error);
	}, []);

	// Project effect
	useEffect(() => {
		if(project === '-1') {
			sendersSet([]);
		} else {
			body.read('contact', '__list', [
				['senders', { _project: project }],
				['categories', { _project: project }]
			], ).then(data => {
				if(data) {
					sendersSet(data[0][1].data);
					categoriesSet(data[1][1].data);
				}
			}, Message.error);
		}

	}, [ project ]);

	// Called when any of the contact list options changes
	function contactsListChange(_id, checked) {
		contactsListSet(l => {
			if(checked) {
				if(!l.includes(_id)) {
					const lNew = [ ...l ];
					lNew.push(_id);
					return lNew;
				}
			} else {
				const i = l.indexOf(_id);
				if(i > -1) {
					const lNew = [ ...l ];
					lNew.splice(i, 1);
					return lNew;
				}
			}
		});
	}

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

		// Generate the data
		const oData = {
			record: {
				_project: project,
				_sender: sender,
				name,
				min_interval: minMax[0],
				max_interval: minMax[1],
				subject,
				content
			},
			contacts
		};

		// If contacts is categories or ids
		if(['categories', 'ids'].indexOf(contacts) > -1) {

			// Add the list of IDs
			oData.contacts_list = contactsList;
		}

		// Send the request
		body.create('contact', 'campaign', oData).then(data => {

			// Success
			Message.success('New Campaign created');

			// Navigate to the new campaign
			navigate(`/campaigns/${data}`);

		}, error => {
			if(error.code === errors.DATA_FIELDS) {
				errsSet(pathToTree(error.msg));
			} else {
				Message.error(error);
			}
		});
	}

	// Render
	return (
		<Box id="campaignNew" className="flexDynamic padding">
			<Box className="pageHeader">
				<h1>New Campaign</h1>
			</Box>
			<Grid container spacing={2} className="campaignForm">
				<Grid item xs={12} md={6} className="field">
					<FormControl error={errs.records && errs.records._project && errs.records._project !== false} variant="outlined">
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
						{errs.records && errs.records._project &&
							<FormHelperText>{errs.record._project}</FormHelperText>
						}
					</FormControl>
				</Grid>
				{project !== '-1' && <>
					<Grid item xs={12} md={6} className="field">
						<FormControl error={errs.records && errs.records._sender && errs.records._sender !== false} variant="outlined">
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
							{errs.records && errs.records._sender &&
								<FormHelperText>{errs.record._sender}</FormHelperText>
							}
						</FormControl>
					</Grid>
					{sender !== '-1' && <>
						<Grid item xs={12} md={4} className="field">
							<DefineNode
								error={(errs.record && errs.record.name) || false}
								name="name"
								node={CampaignTree.get('name')}
								onChange={nameSet}
								type="create"
								value={name}
							/>
						</Grid>
						<Grid item xs={12} md={4}>
							<Minutes
								error={(errs.record && errs.record.min_interval) || false}
								label="Minimum Interval"
								onChange={val => minMaxChange('min', val)}
								value={minMax[0]}
							/>
						</Grid>
						<Grid item xs={12} md={4}>
							<Minutes
								error={(errs.record && errs.record.max_interval) || false}
								label="Maxmimum Interval"
								onChange={val => minMaxChange('max', val)}
								value={minMax[1]}
							/>
						</Grid>
						<Grid item xs={12} className="field">
							<DefineNode
								error={(errs.record && errs.record.subject) || false}
								name="subject"
								node={CampaignTree.get('subject')}
								onChange={subjectSet}
								type="create"
								value={subject}
							/>
						</Grid>
						<Grid item xs={12} className="field">
							<FormControl error={errs.records && errs.records.content && errs.records.content !== false} variant="outlined">
								<InputLabel id="campaignNewContent" shrink={true}>E-Mail Content Template</InputLabel>
								<HTML
									labelId="campaignNewContent"
									onChange={contentSet}
									value={content}
								/>
								{errs.records && errs.records.content &&
									<FormHelperText>{errs.record.content}</FormHelperText>
								}
							</FormControl>
						</Grid>
						<Grid item xs={12}>
							<RadioButtons
								border={true}
								gridContainerProps={{ spacing: 2 }}
								gridItemProps={{ xs: 4 }}
								label="Choose Contacts"
								options={[
									{ text: 'All', value: 'all' },
									{ text: 'Categories', value: 'categories' },
									{ text: 'List', value: 'ids' }
								]}
								onChange={val => {
									contactsSet(val);
									contactsListSet([]);
								}}
								value={contacts}
								variant="grid"
							/>
						</Grid>
						{(contacts === 'categories' &&
							categories.map(o =>
								<Grid key={o._id} item xs={6} sm={4} md={3} lg={2}>
									<FormControlLabel
										control={
											<Switch
												checked={contactsList.includes(o._id)}
												onChange={ev => contactsListChange(o._id, ev.target.checked)}
											/>}
										label={o.name}
									/>
								</Grid>
							)
						) || (contacts === 'ids' &&

							<Box />
						)}
						<Grid item xs={12} className="actions">
							<Button
								color="primary"
								onClick={submit}
								variant="contained"
							>Create Campgin</Button>
						</Grid>
					</>}
				</>}
			</Grid>
		</Box>
	);
}

// Valid props
CampaignNew.propTypes = { }