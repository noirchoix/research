<script lang="ts">
	import "./layout.css";
	import { goto } from "$app/navigation";

	let { children } = $props();

	function goBack() {
		// Works for normal navigation; if there is no history, fallback to home.
		if (typeof window !== "undefined" && window.history.length > 1) {
			window.history.back();
		} else {
			goto("/");
		}
	}
</script>

<nav class="w-full bg-white border-b border-[#E6DCCB] px-6 py-3">
	<div class="max-w-6xl mx-auto flex items-center justify-between gap-4">
		<div class="flex items-center gap-3">
			<button
				type="button"
				onclick={goBack}
				class="text-sm border border-[#E6DCCB] rounded-full px-4 py-2 bg-[#F7F3EB] text-black"
			>
				← Back
			</button>

			<span class="text-sm font-semibold text-black">Research</span>
		</div>

		<div class="flex items-center gap-2">
			<a
				href="/"
				class="text-sm border border-[#E6DCCB] rounded-full px-4 py-2 bg-white text-black"
			>
				Dashboard
			</a>

			<a
				href="/prompt"
				class="text-sm border border-[#E6DCCB] rounded-full px-4 py-2 bg-white text-black"
			>
				Prompt Builder
			</a>
		</div>
	</div>
</nav>

<main class="min-h-[calc(100vh-56px)]">
	{@render children()}
</main>
