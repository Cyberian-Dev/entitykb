<script>
    import Menu from "./Menu.svelte";
    import Bottom from "./Bottom.svelte";
    import ListView from "./ListView.svelte";
    import DetailView from "./DetailView.svelte";

    let choice = "admin";
    let selectKey = null;

    const updateKey = () => {
        if (selectKey !== null) {
            choice = "detail"
        } else {
            choice = "admin";
        }
    };

    const updateChoice = () => {
        if (choice !== "detail") {
            selectKey = null;
        }
    };

    $: updateKey(selectKey);
    $: updateChoice(choice);
</script>

<main>
    <Menu bind:choice={choice} />

    {#if (choice === "admin")}
    <div id="content">
        <ListView bind:selectKey={selectKey} />
    </div>
    {:else if (choice === "detail")}
    <div id="content">
        <DetailView key={selectKey} />
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