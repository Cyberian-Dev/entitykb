<script>
    import {onMount} from 'svelte';
    import {push} from "svelte-spa-router";

    import MultiSelect from "../common/MultiSelect.svelte"
    import Pagination from "../common/Pagination.svelte"
    import SearchBox from "../common/SearchBox.svelte"

    import {manager} from '../kb/manager';
    import {Schema} from "../kb/schema";

    export let params;
    const nextRequest = {
        q: '',
        labels: '',
        page: 0
    };
    let entities = [];
    let schema = Schema.instance();

    onMount(() => {
        refreshData();
    });

    const refreshData = async () => {
        entities = await manager.getEntities(nextRequest);
    };

    const onUpdate = async (event) => {
        nextRequest[event.detail.name] = event.detail.value;
        nextRequest["page"] = 0;
        await refreshData();
    };

    async function doPageChange(event) {
        nextRequest["page"] = event.detail;
        await refreshData();
    }

    const openRow = (key) => {
        const encodedKey = encodeURIComponent(key);
        push("/detail/" + encodedKey);
        nextRequest["page"] = 0;
    };

    document.title = "Graph Search";
</script>

<div class="ui stackable sixteen column grid">
    <div class="two wide column">
        <h2>Graph</h2>
    </div>
    <div class="five wide column">
        <SearchBox name="q" on:update={onUpdate}/>
    </div>
    <div class="five wide column">
        <MultiSelect
                display="Labels"
                name="labels"
                options={schema.labels}
                on:update={onUpdate}
        />
    </div>
    <div class="four wide column">
        <Pagination page={nextRequest.page}
                    page_count={entities.length}
                    on:doPageChange={doPageChange}
        />
    </div>
</div>

<table class="ui compact selectable celled striped table top aligned">
    <thead class="full-width">
    <tr>
        <th class="two wide">Name</th>
        <th class="two wide">Label</th>
        <th class="two wide">Key</th>
        <th class="four wide">Attributes</th>
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
                    {#each entity.attributes as [name, value]}
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
