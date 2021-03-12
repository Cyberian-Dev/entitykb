<script>
    import {onMount, createEventDispatcher} from "svelte";

    const dispatch = createEventDispatcher();

    export let display;
    export let name;
    export let options = [];
    let dropdown;

    function onChange(event) {
        const selectedValues = Array.from(event.target.selectedOptions).map(
                o => {
                    return o.value
                }
        );
        dispatch("update", {"name": name, "value": selectedValues});
    }

    onMount(() => {
        window.$(dropdown).dropdown();
    });
</script>

<select bind:this={dropdown}
        on:change={onChange}
        multiple="multiple"
        class="ui fluid search dropdown multiple">
    <option value="">Select {display}</option>
    {#each options as option}
        <option value={option}>{option}</option>
    {/each}
</select>