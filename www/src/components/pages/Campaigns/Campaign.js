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
import { Form, Options, Results } from '@ouroboros/define-mui';

// NPM modules
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

// Material UI
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';

// Project components
import 'components/define/HTML';
import 'components/define/Minutes';

// Project modules
import Message from 'message';

// Load Campaign definition
import CampaignDef from 'definitions/contact/campaign';

// Options
const SenderOptions = new Options.Custom();

// Create the tree
const CampaignTree = new Tree(CampaignDef, {
	__ui__: {
		__update__: [
			'_sender', 'next_trigger', 'min_interval', 'max_interval',
			'subject', 'content'
		]
	},

	_sender: { __ui__: {
		__options__: SenderOptions, __title__: 'Sender',
		__type__: 'select'
	} },
	next_trigger: { __ui__: { __title__: 'Next Trigger' } },
	min_interval: { __ui__: { __type__: 'minutes', __title__: 'Min Interval' } },
	max_interval: { __ui__: { __type__: 'minutes', __title__: 'Max Interval' } },
	subject: { __ui__: { __title__: 'E-Mail Subject Template' } },
	content: { __ui__: { __type__: 'html' } }
});
const ContactTree = new Tree({
	__ui__: { __results__: [
		'_id', 'name', 'email_address', 'sent', 'delivered', 'opened',
		'unsubscribed'
	]},
	__name__: 'Contact',
	_id: { __type__: 'uuid', __ui__: { __title__: 'ID' } },
	name: { __type__: 'string' },
	email_address: { __type__: 'string' },
	sent: { __type__: 'timestamp' },
	delivered: { __type__: 'timestamp' },
	opened: { __type__: 'timestamp' },
	unsubscribed: { __type__: 'timestamp' }
})

// Constants
const GRID_SIZES = {
	__default__: { xs: 12 },
	next_trigger: { xs: 12, md: 6 },
	min_interval: { xs: 6, md: 3 },
	max_interval: { xs: 6, md: 3}
};

/**
 * Campaign
 *
 * @name Campaign
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Campaign(props) {

	// State
	const [ campaign, campaignSet ] = useState(false);
	const [ tab, tabSet ] = useState(0);

	// Hooks
	const { _id } = useParams();

	// Load / ID effect
	useEffect(() => {

		// Fetch the campaign
		body.read('contact', 'campaign', {
			_id,
			add_names: true
		}).then(data => {

			// Fetch the senders list
			body.read('contact', 'senders', {
				_project: data._project
			}).then(senders => {
				SenderOptions.set(senders.map(o => [ o._id, o.email_address ]))
				campaignSet(data);
			});

		}, Message.error);

	}, [ _id ]);

	function campaignUpdate(data, key) {

		// Create a new Promise and return it
		return new Promise((resolve, reject) => {

			// Send the update to the server
			body.update('contact', 'campaign', {
				_id: key,
				record: data
			}).then(data => {

				// Notify the user
				Message.success('Campaign updated.');

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
		<Box id="campaignsCampaign">
			<Tabs value={tab} onChange={(ev,val) => tabSet(val)}>
				<Tab label="Content" />
				<Tab label="Contacts" />
			</Tabs>
			{(tab === 0 &&
				<Box className="campaign padding">
					{(campaign === false &&
						<Box className="padding">Loading...</Box>
					) || (campaign &&
						<Form
							gridSizes={GRID_SIZES}
							onSubmit={campaignUpdate}
							tree={CampaignTree}
							type="update"
							value={campaign}
						/>
					)}
				</Box>
			) || (tab === 1 &&
				<Box className="contacts padding">
					<Results
						data={campaign.contacts}
						tree={ContactTree}
					/>
				</Box>
			)}
		</Box>
	)
}