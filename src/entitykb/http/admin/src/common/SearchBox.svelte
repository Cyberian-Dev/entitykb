<script>
    import {createEventDispatcher} from 'svelte';

    const dispatch = createEventDispatcher();

    export let name;
    export let q = "";
    let lastQ = q;
    let qInput;

    function clearQ() {
        q = "";
        qInput.focus();
    }

    function updateQ() {
        if (q !== lastQ) {
            dispatch("update", {"name": name, "value": q});
            lastQ = q;
        }
    }

    $: updateQ(q);
</script>

<div id="action-item" class="ui fluid action input">
    <input size="20" id="search" bind:this={qInput} type="text"
           placeholder="Search"
           bind:value={q}>

    {#if q}
        <button class="ui red right icon button" on:click={clearQ}>
            <i class="window close icon"></i>
        </button>
    {:else}
        <button class="ui grey right icon button" on:click={clearQ}>
            <i class="search icon"></i>
        </button>
    {/if}
</div>
