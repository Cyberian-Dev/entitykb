<script>
    import {onMount} from 'svelte';
    import {RequestManager} from './kb/manager';

    import Pagination from "./Pagination.svelte";
    import ColumnFilter from "./ColumnFilter.svelte";
    import AttributeFilter from "./AttributeFilter.svelte";

    export let schema;
    export let selectKey = null;

    const manager = new RequestManager();
    const nextRequest = {name: '', label: '', key: '', attribute: null};

    let entities = [];
    let page = 0;
    $: labels = (schema !== null && schema.labels) || [];

    onMount(() => {
        refreshData();
        setInterval(refreshData, 10);
    });

    const openRow = (key) => {
        selectKey = key;
    };

    const onUpdate = async (event) => {
        nextRequest[event.detail.name] = event.detail.value;
        page = 0;
    };

    const refreshData = async () => {
        if (manager.isAvailable(page, nextRequest)) {
            entities = await manager.getEntities(page, nextRequest);
        }
    };
</script>

<div class="ui grid">
    <div class="eight wide column">
    </div>
    <div class="eight wide column right aligned">
        <Pagination bind:page={page}/>
    </div>
</div>

<table class="ui compact selectable celled striped table top aligned">
    <thead class="full-width">
    <tr>
        <th class="two wide">
            <ColumnFilter name="name" display="Name"
                          on:update={onUpdate}/>
        </th>
        <th class="two wide">
            <ColumnFilter name="label" display="Label"
                          options={labels}
                          on:update={onUpdate}/>
        </th>
        <th class="two wide">
            <ColumnFilter name="key" display="Key"
                         on:update={onUpdate}/>
        </th>
        <th class="four wide">
            <AttributeFilter on:update={onUpdate}/>
        </th>
    </tr>
    </thead>
    <tbody>
    {#each entities as entity}
        <tr on:click={openRow(entity.key)}>
            <td>{entity.name}</td>
            <td>{entity.label}</td>
            <td>{entity.key}</td>
            <td>
                <table class="ui compact celled table top aligned">
                {#each Object.entries(entity.attributes).sort() as [name, value]}
                    <tr class="top aligned">
                        <td class="four wide field_name">{name}:</td>
                        <td class="twelve wide">
                        {#if value instanceof Array}
                            {#each value.slice(0, 5) as item}
                                {item}<br/>
                            {/each}
                            {#if value.length > 5}
                                <i>{value.length - 5} more...</i>
                            {/if}
                        {:else}
                            {value}
                        {/if}
                        </td>
                    </tr>
                {/each}
                </table>
            </td>
        </tr>
    {/each}
    </tbody>
</table>

<style>
    .field_name {
        font-weight: bold;
        color: #444444;
        background-color: #DDD5DD;
    }
</style>