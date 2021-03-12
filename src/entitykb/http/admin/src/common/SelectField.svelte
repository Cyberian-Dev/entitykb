<script>
    import {onMount} from "svelte";
    import {createEventDispatcher} from 'svelte';

    const dispatch = createEventDispatcher();

    export let name = null;
    export let label = false;
    export let options = {};
    export let value = "";
    export let placeholder = "";
    export let display = "";
    let dropdown = null;

    placeholder = placeholder || label;

    const updateValue = (event) => {
        value = event.target.value;
        display = options[value];
        dispatch("change", {name, value});
    };

    onMount(() => {
       updateDropdown();
    });

    const updateDropdown = () => {
        if (value !== null) {
            window.$(dropdown).dropdown("set selected", value);
        } else {
            window.$(dropdown).dropdown("restore defaults preventChangeTrigger");

        }
    };

    $: updateDropdown(value);
</script>

<div class="field">
    <div class:labeled={label} class="ui right icon input">
        {#if label}
            <div class="ui label">
                {label}:
            </div>
        {/if}
        <div bind:this={dropdown} class="ui search selection dropdown">
            <input type="hidden" value={value} on:change={updateValue}>
            <i class="dropdown icon"></i>
            <div class="default text">{placeholder}</div>
            <div class="menu">
                {#each Object.entries(options || {}) as [item, display]}
                    <div class="item" data-value={item}>
                        {display}
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>

<style>
    .ui.label {
        width: 8em;
        text-align: left;
    }
</style>