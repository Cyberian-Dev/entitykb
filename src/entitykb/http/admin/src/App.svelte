<script>
    import Menu from "./Menu.svelte";
    import Bottom from "./Bottom.svelte";
    import Admin from "./Admin.svelte";

    let choice = "admin";
</script>

<main>
    <Menu bind:choice={choice} />

    {#if (choice === "admin")}
    <div id="content">
        <Admin />
    </div>
    {:else if (choice === "api")}
        <iframe src="/docs"></iframe>
    {:else if (choice === "docs")}
        <iframe src="https://www.entitykb.org/"></iframe>
    {:else if (choice === "docs")}
        <iframe src="https://www.entitykb.org/"></iframe>
    {/if}

    <Bottom />
</main>

<style>
    iframe {
        width: 100%;
        height: calc(85vh);
        border: 0;
    }
    #content {
        padding: 1em;
        margin: 1em 3em 5em 3em;
    }
</style>