<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { Confetti } from 'svelte-confetti';

	import { WEBUI_NAME, config, showSidebar } from '$lib/stores';

	import { WEBUI_VERSION } from '$lib/constants';
	import { getChangelog } from '$lib/apis';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	let changelog = null;

	onMount(async () => {
		showSidebar.set(false);
		const res = await getChangelog();
		changelog = res;
	});
</script>

<div class="flex flex-col min-h-screen px-5">
	<header class="sticky top-0 z-10">
		<div class="px-5 pt-4 dark:text-gray-300 text-gray-700">
			<div class="flex justify-between items-start">
				<div class="text-xl font-semibold">
					{$i18n.t('What’s New in')}
					{$WEBUI_NAME}
					<Confetti x={[0, 3]} y={[0, -1]} duration={3000} />
				</div>
			</div>
			<div class="flex items-center mt-1">
				<div class="text-sm dark:text-gray-200">{$i18n.t('Release Notes')}</div>
				<div class="flex self-center w-[1px] h-6 mx-2.5 bg-gray-200 dark:bg-gray-700" />
				<div class="text-sm dark:text-gray-200">
					V{WEBUI_VERSION}
				</div>
			</div>
		</div>
	</header>

	<main class="scrollable-content text-gray-700 dark:text-gray-100 p-4 flex-1">
		<div class="mb-3">
			{#if changelog}
				{#each Object.keys(changelog) as version}
					<div class=" mb-3 pr-2">
						<div class="font-semibold text-xl mb-1 dark:text-white">
							V{version} - {changelog[version].date}
						</div>

						<hr class=" dark:border-gray-800 my-2" />

						{#each Object.keys(changelog[version]).filter((section) => section !== 'date') as section}
							<div class="">
								<div
									class="font-semibold uppercase text-xs {section === 'added'
										? 'text-white bg-blue-600'
										: section === 'fixed'
										? 'text-white bg-green-600'
										: section === 'changed'
										? 'text-white bg-yellow-600'
										: section === 'removed'
										? 'text-white bg-red-600'
										: ''}  w-fit px-3 rounded-full my-2.5"
								>
									{section}
								</div>

								<div class="my-2.5 px-1.5">
									{#each Object.keys(changelog[version][section]) as item}
										<div class="text-sm mb-2">
											<div class="font-semibold uppercase">
												{changelog[version][section][item].title}
											</div>
											<div class="mb-2 mt-1">{changelog[version][section][item].content}</div>
											{#if changelog[version][section][item].url}
												<a class="mb-2 mt-1" target="_blank" href="{changelog[version][section][item].url}">{changelog[version][section][item].url}</a>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/each}
			{/if}
		</div>
	</main>

	<footer class="p-4 sticky bottom-0 z-10 text-sm font-medium">
		<button
			on:click={async () => {
				localStorage.version = $config.version;
				await goto('/auth');
			}}
			class="fixed bottom-4 right-4 px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
		>
			<span class="relative">{$i18n.t("Okay, Let's Go!")}</span>
		</button>
	</footer>
</div>

<style>
	.scrollable-content {
		max-height: calc(100vh - 8rem);
		overflow-y: auto;
	}
</style>
