<script lang="ts">
 import { onMount } from 'svelte';

 let api_server: string = '';
 let dialog: object = {};
 let dialog_title: object = {};
 let dialog_message: object = {};

 onMount(() => {
	 dialog = document.getElementById('box-dialog');
	 dialog_title = document.getElementById('dialog-title');
	 dialog_message = document.getElementById('dialog-message');
 });

 async function openSlot(elem) {
	 let signature: string = elem.dataset.signature;
	 let id: string = elem.id;
	 let sig: string = new URLSearchParams({ sig: signature }).toString()
	 let url: string = api_server + '/api/open/' + id.toString() + '?' + sig;

	 const response = await fetch(url).then((res) => res.json());

	 if (response.success) {
		 dialog_title.innerText = 'Opened parcel:';
		 dialog_message.innerText = '"' + response.content + '"';
	 } else {
		 dialog_title.innerText = 'Failed opening slot:';
		 dialog_message.innerText = '[!] ' + response.content;
	 }
	 dialog.showModal();
 }

 async function getMyParcel() {
	 const response = await fetch(api_server + '/api/my_parcel').then((res) => res.json());
	 let box = document.getElementById(response['id']);

	 box.classList.remove('is-disabled');
	 box.classList.add('is-error');
	 box.disabled = null;
	 box.dataset.signature = response['sig'];
 }
</script>

<dialog class="absolute left-1/2 top-1/2 -translate-1/2 p-8 nes-dialog max-w-128" id="box-dialog">
	<form method="dialog" class="flex flex-col gap-4">
		<b class="title" id="dialog-title"></b>
		<p id="dialog-message"></p>
		<menu class="dialog-menu">
			<button class="nes-btn is-primary w-full">Close</button>
		</menu>
	</form>
</dialog>

<div class="flex flex-col h-screen w-screen min-w-[90rem] overflow-scroll">
	<div class="flex h-4/5 justify-center items-end gap-2 bg-sky-300">
		<div class="h-128 w-72 m-8 rounded-2xl flex px-2 py-12 bg-black translate-y-32">
			<div
				class="h-full w-full min-w-fit bg-neutral-800 flex-col p-4 text-white text-xs flex justify-between"
			>
				<div class="flex flex-row gap-4 justify-between">
					<div class="flex flex-row gap-4 justify-start">
						<span>#</span>
						<span>#</span>
						<span>#</span>
					</div>
					<div class="flex flex-row gap-4 justify-end">
						<span>70%</span>
						<span>13:37</span>
					</div>
				</div>
				<div>
					<b class="w-full min-w-fit title">Your parcel is ready for pickup!</b>
					<div class="w-full min-w-fit mt-8 flex flex-col gap-4">
						<p>Pickup location:<br />NNS HQ, Norway</p>
						<button class="nes-btn is-primary w-full min-w-fit p-8" on:click={getMyParcel}
						>Open slot</button
									   >
					</div>
				</div>
			</div>
		</div>
		{#each { length: 3 }, i}
			<div
				class="grid grid-cols-2 gap-4 w-fit justify-center items-center nes-container bg-gray-300 translate-y-48"
			>
				<div class="col-span-full justify-center items-center p-2">
					<h1 class="title text-red-700">ParcelLocker</h1>
				</div>
				{#each { length: 2 * 6 }, id}
					<button
						id={id + 2 * 6 * i}
						   disabled="true"
						   class="w-32 h-12 nes-btn is-disabled"
						   on:click={(e) => openSlot(e.target)}>+</button
																 >
				{/each}
				<div class="col-span-full p-2 h-16"></div>
			</div>
		{/each}
	</div>
	<div class="bg-green-700 w-full min-w-fit h-2/5"></div>
</div>
