<script>
    import {onMount} from 'svelte';
    import {RequestManager} from './kb/manager';
    import {Entity} from "./kb/nodes";

    import Pagination from "./Pagination.svelte";
    import ColumnFilter from "./ColumnFilter.svelte";

    export let schema;
    export let selectKey = null;

    const manager = new RequestManager();
    const defaults = {direction: '', verb: '', name: '', label: ''};
    const nextRequest = {...defaults, key: selectKey};

    $: labels = (schema !== null && schema.labels) || [];
    $: verbs = (schema !== null && schema.verbs) || [];

    let entity = new Entity({});
    let neighbors = [];
    let page = 0;

    const directions = ["Incoming", "Outgoing"];

    onMount(() => {
        loadEntity();
        loadNeighbors();
        setInterval(loadNeighbors, 50);
    });

    const loadEntity = async () => {
        entity = await manager.getEntity(selectKey);
    };

    const loadNeighbors = async () => {
        if (manager.isAvailable(page, nextRequest)) {
            neighbors = await manager.getNeighbors(page, nextRequest);
        }
    };

    const onUpdate = async (event) => {
        nextRequest[event.detail.name] = event.detail.value;
        page = 0;
    };


    const openRow = (rowKey) => {
        page = 0;
        selectKey = rowKey;
        nextRequest["key"] = rowKey;
        loadEntity();
    };

</script>

<div class="ui grid">
    <div class="seven wide column">
        <h3>Node Details</h3>
        <table class="ui compact definition table top aligned">
            <tbody>
            <tr>
                <td class="two wide column">key</td>
                <td class="five wide column">{entity.key}</td>
            </tr>
            <tr>
                <td>name</td>
                <td>{entity.name}</td>
            </tr>
            <tr>
                <td>label</td>
                <td>{entity.label}</td>
            </tr>
            {#each Object.entries(entity.attributes).sort() as [name, value]}
            <tr>
                <td>{name}</td>
                <td>
                    {#if value instanceof Array}
                    {#each value as item}
                        {item}<br/>
                    {/each}
                    {:else}
                        {value}
                    {/if}
                </td>
            </tr>
            {/each}
            </tbody>
        </table>
    </div>
    <div class="nine wide column">
        <div class="ui grid">
            <div class="one wide column">
                <h3>Relationships</h3>
            </div>
            <div class="fifteen wide column right aligned">
                <Pagination bind:page={page}/>
            </div>
        </div>

        <table class="ui compact selectable celled striped table top aligned">
            <thead class="full-width">
            <tr>
                <th class="two wide" nowrap="nowrap">
                    <ColumnFilter name="direction"
                                  display="Direction"
                                  options={directions}
                                  on:update={onUpdate}/>
                </th>
                <th class="two wide" nowrap="nowrap">
                    <ColumnFilter name="verb" display="Verb"
                                  options={verbs}
                                  on:update={onUpdate}/>
                </th>
                <th class="three wide" nowrap="nowrap">
                    <ColumnFilter name="name" display="Name"
                                  on:update={onUpdate}/>
                </th>
                <th class="two wide">
                    <ColumnFilter name="label" display="Label"
                          options={labels}
                          on:update={onUpdate}/>
                </th>
            </tr>
            </thead>
            <tbody>
            {#each neighbors as neighbor}
                <tr on:click={openRow(neighbor.key)}>
                    <td>{neighbor.direction}</td>
                    <td>{neighbor.verb}</td>
                    <td>{neighbor.name}</td>
                    <td>{neighbor.label}</td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
</div>
