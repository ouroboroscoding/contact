/**
 * Site
 *
 * Primary entry into Admin site
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2023-01-17
 */

// Init body
import 'body_init';

// CSS
import '../sass/site.scss';

// Ouroboros modules
import { Results } from '@ouroboros/define-mui';
import events from '@ouroboros/events';

// NPM modules
import React, { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

// Material UI
import Box from '@mui/material/Box';
import { ThemeProvider } from '@mui/material/styles';
import { StyledEngineProvider } from '@mui/material/styles';

// CSS Theme
import Theme from 'components/Theme'

// Site component modules
import Errors from 'components/Errors';
import Header from 'components/Header';
import Network from 'components/Network';
import Success from 'components/Success';
import Testing from 'components/Testing';

// Site pages
import Categories from 'components/pages/Categories';
import Contacts from 'components/pages/Contacts';
import Projects from 'components/pages/Projects';
import Senders from 'components/pages/Senders';

// Add default onCopyKey methods to Results
Results.setOnCopyKey(() => {
	events.get('success').trigger('Record ID copied to clipboard!');
});

/**
 * Site
 *
 * Primary site component
 *
 * @name Site
 * @access public
 * @param Object props Properties passed to the component
 * @return React.Component
 */
export default function Site(props) {

	return (
		<StyledEngineProvider injectFirst={true}>
			<ThemeProvider theme={Theme}>
				<BrowserRouter>
					{['development', 'staging'].includes(process.env.NODE_ENV) &&
						<Testing />
					}
					<Network />
					<Success />
					<Errors />
					<Header />
					<Box className="flexDynamic">
						<Routes>
							<Route path="/categories" element={
								<Categories />
							} />
							<Route path="/contacts" element={
								<Contacts />
							} />
							<Route path="/projects" element={
								<Projects />
							} />
							<Route path="/senders" element={
								<Senders />
							} />
						</Routes>
					</Box>
				</BrowserRouter>
			</ThemeProvider>
		</StyledEngineProvider>
	);
}