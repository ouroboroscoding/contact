/**
 * Campaigns: New
 *
 * Create a new, paused, campaign
 *
 * @author Chris Nasr <chris@ouroboroscoding.com>
 * @created 2024-01-20
 */

// NPM modules
import PropTypes from 'prop-types';
import React from 'react';
import { Editor } from '@tinymce/tinymce-react';

/**
 * HTML
 *
 * @name HTML
 * @access public
 * @param Object props Properties passed to the component
 * @returns React.Component
 */
export default function HTML({ maxHeight, onChange, value }) {

	// Render
	return (
		<Editor
			apiKey={process.env.REACT_APP_TINYMCE}
			onEditorChange={onChange}
			init={{
				block_formats: 'Heading 1=h1; Heading 2=h2; Heading 3=h3; Paragraph=p; Preformatted=pre',
				content_style: 'body { font-family: "Roboto","Helvetica","Arial",sans-serif; font-size: 1rem }',
				height: 'auto',
				max_height: maxHeight,
				menubar: false,
				plugins: ['advlist', 'emoticons', 'link', 'lists', 'code', 'autoresize'],
				paste_as_text: true,
				statusbar: false,
				toolbar: 'undo redo | ' +
							'blocks | ' +
							'bold italic | ' +
							'alignleft aligncenter alignright alignjustify | ' +
							'bullist numlist outdent indent | ' +
							'subscript superscript | ' +
							'link emoticons | ' +
							'removeformat | code'
			}}
			value={value}
		/>
	);
}

// Valid props
HTML.propTypes = {
	maxHeight: PropTypes.number,
	onChange: PropTypes.func.isRequired,
	value: PropTypes.string.isRequired
}

// Default props
HTML.defaultProps = {
	maxHeight: 600
}