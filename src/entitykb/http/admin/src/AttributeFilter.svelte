<script>
    import {createEventDispatcher} from 'svelte';
    const dispatch = createEventDispatcher();

    let name = "";
    let value = "";
    let inFilterMode = false;

    const cancelFilter = () => {
        inFilterMode = false;
        name = "";
        value = "";
    };

    const openFilter = () => {
        inFilterMode = true;
    };

    const updateFilterValue = () => {
        let data = null;
        if (Boolean(name) && Boolean(value)) {
            data = {name: name, value:value};
        }
        dispatch("update", {"name": "attribute", "value": data});
    };

    $: updateFilterValue(name, value);
</script>

<div id="column">
    {#if inFilterMode}
        <a on:click={cancelFilter}><i class="red window close icon"></i></a>
        <input placeholder="name" bind:value={name} autofocus>
        &thickapprox;
        <input placeholder="value" bind:value={value}>
    {:else}
        <a on:click={openFilter}><i class="blue filter icon"></i></a>
        Attributes
    {/if}
</div>

<style>
    #column {
        vertical-align: middle;
        height: 1.5em;
    }

    .icon {
        width: 1em;
    }
</style>

