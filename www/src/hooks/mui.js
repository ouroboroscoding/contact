/**
 * MUI
 *
 * Hooks for dealing with MaterialUI
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2023-01-17
 */

// Material UI modules
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

/**
 * Use Width
 *
 * Returns the current MUI screen width label
 *
 * @name useWidth
 * @access public
 * @returns String
 */
export function useWidth() {
	const theme = useTheme();
	const keys = [...theme.breakpoints.keys].reverse();
	return (
		keys.reduce((output, key) => {
			// eslint-disable-next-line react-hooks/rules-of-hooks
			const matches = useMediaQuery(theme.breakpoints.up(key));
			return !output && matches ? key : output;
		}, null) || 'xs'
	);
}
