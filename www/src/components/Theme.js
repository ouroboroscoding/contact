/**
 * Theme
 *
 * Used to override those things that just can't be done in SASS cause of
 * Material UI
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @copyright Ouroboros Coding Inc.
 * @created 2023-01-17
 */

// Material UI
import { createTheme } from '@mui/material/styles';

// Create the theme
const Theme = createTheme({
	palette: {
		info: {
			dark: '#a3a3a3',
			light: '#dddddd',
			main: '#c5c5c5'
		},
		primary: {
			dark: '#246c91',
			light: '#37a3d9',
			main: '#2f8bb9'
		},
		secondary: {
			dark: '#ad0303',
			light: '#ed4c4c',
			main: '#d42828'
		}
	}
})

// Export the theme
export default Theme;