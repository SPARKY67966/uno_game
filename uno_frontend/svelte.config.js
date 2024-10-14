import adapter from '@sveltejs/adapter-vercel';
import preprocess from 'svelte-preprocess';

const config = {

	preprocess: preprocess({
		postcss: true,
	  }),

	kit: {
		adapter: adapter()
	}
};

export default config;
