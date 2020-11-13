<script>
    import {onMount} from 'svelte';

    import {RequestManager} from "./kb/manager";

    import Menu from "./Menu.svelte";
    import Bottom from "./Bottom.svelte";
    import ListView from "./ListView.svelte";
    import DetailView from "./DetailView.svelte";

    let choice = "graph";
    let selectKey = null;
    let schema = null;
    const manager = new RequestManager();

    onMount(async () => {
        schema = await manager.getSchema();
    });


    const updateKey = () => {
        if (selectKey !== null) {
            choice = "detail"
        } else {
            choice = "graph";
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

    {#if (choice === "graph")}
    <div id="content">
        <ListView bind:selectKey={selectKey} schema={schema} />
    </div>
    {:else if (choice === "detail")}
    <div id="content">
        <DetailView bind:selectKey={selectKey} schema={schema} />
    </div>
    {:else if (choice === "api")}
        <iframe title="Swagger API" src="/docs"></iframe>
    {:else if (choice === "docs")}
        <iframe title="Docs" src="https://www.entitykb.org/"></iframe>
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