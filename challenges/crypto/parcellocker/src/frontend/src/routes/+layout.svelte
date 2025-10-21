<script lang="ts">
 import '../app.css';

 let { children } = $props();
</script>

<svelte:head>
	<title>ParcelLocker</title>
	<link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet" />
</svelte:head>

{@render children?.()}
