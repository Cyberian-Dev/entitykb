<script>
    import {createEventDispatcher} from 'svelte';
    const dispatch = createEventDispatcher();

    export let name;
    export let display;

    let filterValue;
    let inFilterMode = false;

    const cancelFilter = () => {
        inFilterMode = false;
        filterValue = "";
    };

    const openFilter = () => {
        inFilterMode = true;
    };

    const updateFilterValue = () => {
        dispatch("update", {"name": name, "value": filterValue});
    };

    $: updateFilterValue(filterValue);
</script>

<div id="column">
    {#if inFilterMode}
        <a on:click={cancelFilter}><i class="red window close icon"></i></a>
        &nbsp;
        <input placeholder="{display}" bind:value={filterValue} autofocus>
    {:else}
        <a on:click={openFilter}><i class="blue filter icon"></i></a>
        &nbsp;
        {display}
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

