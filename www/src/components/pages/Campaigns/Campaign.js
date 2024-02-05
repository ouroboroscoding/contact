/**
 * Campaigns: Campaign
 *
 * Shows an existing campaign
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-21
 */

// Ouroboros modules
import body, { errors } from '@ouroboros/body';
import { Tree } from '@ouroboros/define';
import { DefineNode } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

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
	const [ campaign, campaignSet ] = useState(false);

	// Hooks
	const { _id } = useParams();

	// Load / ID effect
	useEffect(() => {

		// Fetch the campaign
		body.read('contact', 'campaign', {
			_id,
			add_names: true
		}).then(campaignSet);

	}, []);

	// Render
	return (
		<Box id="campaignsCampaign" className="padding">
			<pre>{JSON.stringify(campaign, null, 4)}</pre>
		</Box>
	)
}