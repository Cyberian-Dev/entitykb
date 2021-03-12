<script>
    import {createEventDispatcher, onMount} from 'svelte';
    const dispatch = createEventDispatcher();

    export let name = null;
    export let value = null;
    export let display = null;
    export let options = "";

    let inFilterMode = false;

    const cancelFilter = () => {
        inFilterMode = false;
        value = "";
    };

    const openFilter = () => {
        inFilterMode = true;
    };

    $: dispatch("update", {"name": name, "value": value});
</script>

<div id="column">
    {#if inFilterMode}
        <a class="clickable" on:click={cancelFilter}>
            <i class="red window close icon"></i>
        </a>
        {#if options}
            <select bind:value={value}>
                <option value="">Any {display}</option>
            {#each options as option}
                <option>{option}</option>
            {/each}
            </select>
        {:else}
            <input placeholder="{display}" bind:value={value} autofocus>
        {/if}
    {:else}
        <a href="javascript:void(0)" class="clickable" on:click={openFilter}>
            <i class="blue filter icon"></i>
            {display}
        </a>
    {/if}
</div>

<style>
    #column {
        white-space: nowrap;
        vertical-align: middle;
        height: 1.5em;
    }
    .icon {
        width: 1em;
    }
</style>

