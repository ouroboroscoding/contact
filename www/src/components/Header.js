/**
 * Header
 *
 * Handles title and menu
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc
 * @created 2024-01-13
 */

// Ouroboros modules
import body from '@ouroboros/body';
import { cookies, safeLocalStorage } from '@ouroboros/browser';
import clone from '@ouroboros/clone';
import events from '@ouroboros/events';

// NPM modules
import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

// Material UI
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';

/**
 * Header
 *
 * Top of the page
 *
 * @name Header
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function Header(props) {

	// State
	const [loading, loadingSet] = useState(0);
	const [menu, menuSet] = useState(false);
	const [subs, subsSet] = useState(safeLocalStorage.json('submenu', {}))

	// Hooks
	const location = useLocation();

	// Load effect
	useEffect(() => {
		body.onRequested(info => {
			loadingSet(val => {
				val -= 1;
				if(val < 0) {
					val = 0;
				}
				return val;
			});
		});
		body.onRequesting(info => {
			loadingSet(val => val + 1)
		});
	}, [])

	// Hide menu
	function menuOff() {
		menuSet(false);
	}

	// Show/Hide menu
	function menuToggle() {
		menuSet(val => !val);
	}

	// Toggles sub-menus and stores the state in local storage
	function subMenuToggle(name) {

		// Clone the current subs
		let oSubs = clone(subs);

		// If the name exists, delete it
		if(oSubs[name]) {
			delete oSubs[name];
		}
		// Else, add it
		else {
			oSubs[name] = true;
		}

		// Store the value in storage
		localStorage.setItem('submenu', JSON.stringify(oSubs));

		// Update the state
		subsSet(oSubs);
	}

	// Render
	return (
		<Box id="header" className="flexStatic">
			<Box className="flexColumns">
				<IconButton edge="start" color="inherit" aria-label="menu" onClick={menuToggle}>
					<i className="fa-solid fa-bars" />
				</IconButton>
				<Box><Typography className="title">
					<Link to="/" onClick={menuOff}>{props.mobile ? 'Contact' : <span>Contact - Ouroboros Coding Inc.</span>}</Link>
				</Typography></Box>
				<Box className="center flexDynamic">
					{loading > 0 &&
						<img src="/images/loading.gif" alt="loader animation" />
					}
				</Box>
			</Box>
			<Drawer
				anchor="left"
				id="menu"
				open={menu}
				onClose={menuOff}
			>
				<Box className="flexRows">
					<List className="flexDynamic">
						<Link to="/projects" onClick={menuOff}>
							<ListItemButton selected={location.pathname === '/projects'}>
								<ListItemIcon><i className="fa-solid fa-diagram-project" /></ListItemIcon>
								<ListItemText primary="Projects" />
							</ListItemButton>
						</Link>
					</List>
					<Box className="flexStatic footer">
						Version {process.env.REACT_APP_VERSION}
					</Box>
				</Box>
			</Drawer>
		</Box>
	);
}

// Valid props
Header.propTypes = {
	mobile: PropTypes.bool.isRequired
}
